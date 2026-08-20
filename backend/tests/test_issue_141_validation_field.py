from fastapi.exceptions import RequestValidationError

from app.main import _humanize_validation_error


class _ValidationError(RequestValidationError):
    def __init__(self, payload):
        super().__init__(payload)
        self._payload = payload

    def errors(self):
        return self._payload


def _string_too_long_error(loc, max_length=100):
    return _ValidationError([
        {
            "type": "string_too_long",
            "loc": loc,
            "msg": f"String should have at most {max_length} characters",
            "input": "x" * (max_length + 1),
            "ctx": {"max_length": max_length},
        }
    ])


def test_string_too_long_identifies_top_level_caminos_field():
    message = _humanize_validation_error(
        _string_too_long_error(("body", "equipo"), max_length=100)
    )

    assert message == "El campo equipo excede el tamano maximo permitido"
    assert "body" not in message
    assert "x" * 20 not in message


def test_string_too_long_identifies_nested_process_field_without_internal_path():
    message = _humanize_validation_error(
        _string_too_long_error(("body", "procesos", 1, "predio"), max_length=50)
    )

    assert message == "El campo predio excede el tamano maximo permitido"
    assert "procesos" not in message
    assert "[1]" not in message


def test_string_too_long_unknown_field_keeps_safe_generic_message():
    message = _humanize_validation_error(
        _string_too_long_error(("body", "campo_interno"), max_length=10)
    )

    assert message == "uno de los textos excede el tamano maximo permitido"
    assert "campo_interno" not in message
