"""Tests for the user-facing validation error handling.

Covers two regressions reported from production:

1. Operators were seeing raw Pydantic JSON dumps (with docs URLs, internal
   field paths and the entire request payload echoed back) inside the toast
   when a record failed validation. The new global
   ``RequestValidationError`` handler must return a single, friendly string
   instead.

2. ``v-model.number`` on a cleared number input produces ``""`` (or ``null``)
   on the frontend, which the previous schema rejected with a raw
   ``int_parsing`` error. The ``TableroProduccionCreate`` schema now coerces
   blank numeric inputs to ``0`` so the operator never sees that error.
"""
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import SAFE_VALIDATION_ERROR_DETAIL, _humanize_validation_error
from app.schemas.produccion import TableroProduccionCreate


# --- Coercion of blank numeric inputs -------------------------------------


def test_blank_string_aceite_hidraulico_is_coerced_to_zero():
    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 31),
        aceite_hidraulico="",
    )

    assert payload.aceite_hidraulico == 0


def test_null_numeric_fields_are_coerced_to_zero():
    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 31),
        aceite_hidraulico=None,
        aceite_motor=None,
        combustible=None,
        km_combustible=None,
    )

    assert payload.aceite_hidraulico == 0
    assert payload.aceite_motor == 0
    assert payload.combustible == 0
    assert payload.km_combustible == 0


def test_whitespace_string_aceite_hidraulico_is_coerced_to_zero():
    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 31),
        aceite_hidraulico="   ",
    )

    assert payload.aceite_hidraulico == 0


def test_non_blank_string_aceite_hidraulico_still_fails_loudly():
    """We only coerce blank-looking inputs, not real garbage. A typo in the
    frontend still surfaces as a normal Pydantic error (handled by the new
    friendly handler, not silently swallowed)."""
    with pytest.raises(ValidationError):
        TableroProduccionCreate(
            fecha=date(2026, 7, 31),
            aceite_hidraulico="not-a-number",
        )


# --- Friendly RequestValidationError handler ------------------------------


def _build_request_validation_error(errors):
    """Helper: FastAPI wraps a ``ValidationError`` into a
    ``RequestValidationError`` using its own errors list, so we re-raise
    through Pydantic to mirror that path."""
    from pydantic import BaseModel

    class _Probe(BaseModel):
        x: int

    try:
        _Probe.model_validate({})
    except ValidationError as exc:
        # We can't synthesise the exact RequestValidationError without going
        # through FastAPI, so we return a wrapper with the same .errors()
        # shape used by the real handler.
        class _Wrapper(RequestValidationError):
            def __init__(self, payload):
                super().__init__(payload)
                self._payload = payload

            def errors(self):
                return self._payload

        return _Wrapper(errors)

    raise AssertionError("expected ValidationError to be raised by the probe")


def test_humanize_returns_value_error_message_without_pydantic_prefix():
    exc = _build_request_validation_error([
        {
            "type": "value_error",
            "loc": ("body",),
            "msg": "Value error, El combustible requiere un kilometraje u horometro mayor a cero",
            "input": {},
            "ctx": {"error": {}},
            "url": "https://errors.pydantic.dev/2.13/v/value_error",
        }
    ])

    message = _humanize_validation_error(exc)

    assert message == "El combustible requiere un kilometraje u horometro mayor a cero"
    assert "Value error" not in message
    assert "errors.pydantic.dev" not in message


def test_humanize_returns_translated_message_for_int_parsing():
    exc = _build_request_validation_error([
        {
            "type": "int_parsing",
            "loc": ("body", "aceite_hidraulico"),
            "msg": "Input should be a valid integer, unable to parse string as an integer",
            "input": "",
            "url": "https://errors.pydantic.dev/2.13/v/int_parsing",
        }
    ])

    message = _humanize_validation_error(exc)

    assert message == "uno de los campos numericos no es un numero valido"
    assert "Input should be" not in message
    assert "errors.pydantic.dev" not in message


def test_humanize_falls_back_to_generic_message_for_unknown_types():
    exc = _build_request_validation_error([
        {
            "type": "some_unknown_pydantic_thing",
            "loc": ("body",),
            "msg": "Some cryptic Pydantic message",
            "input": None,
        }
    ])

    assert _humanize_validation_error(exc) == SAFE_VALIDATION_ERROR_DETAIL


def test_validation_handler_returns_single_string_detail_over_http():
    """End-to-end: a request that triggers an int_parsing error must come
    back as a single string ``detail`` (the same shape other endpoints use),
    never as a list of Pydantic objects."""
    from pydantic import BaseModel as _BaseModel

    class _IntProbe(_BaseModel):
        aceite_hidraulico: int

    probe_app = FastAPI()

    @probe_app.post("/probe")
    async def _probe(payload: _IntProbe):
        return {"ok": True}

    from app.main import app as main_app, request_validation_exception_handler

    probe_app.add_exception_handler(RequestValidationError, request_validation_exception_handler)

    client = TestClient(probe_app)
    response = client.post("/probe", json={"aceite_hidraulico": "not-a-number"})

    assert response.status_code == 422
    body = response.json()
    assert isinstance(body["detail"], str)
    assert "Input should be" not in body["detail"]
    assert "errors.pydantic.dev" not in body["detail"]
    # The handler is wired up on the real app instance as well, so production
    # endpoints get the same friendly behaviour.
    from app.main import request_validation_exception_handler as real_handler

    assert main_app.exception_handlers.get(RequestValidationError) is real_handler
