"""Tests unitarios del helper de normalizacion de remito (issue #124)."""
import pytest

from app.core.remito import (
    REMITO_MAX_LENGTH,
    is_canonical,
    normalize_remito,
)


# ─── Normalizacion de valores numericos (padded a 12 digitos) ──────────────


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("1", "000000000001"),
        ("11278", "000000011278"),
        ("000000011278", "000000011278"),
        ("011278", "000000011278"),
        ("21325", "000000021325"),
        ("000000000001", "000000000001"),
        ("000000021325", "000000021325"),
        ("0", "000000000000"),
        ("999999999999", "999999999999"),  # 12 digitos sin padding
    ],
)
def test_normaliza_remitos_numericos_al_formato_canonico(entrada, esperado):
    assert normalize_remito(entrada) == esperado


# ─── Normalizacion de valores alfanumericos (sin padding) ──────────────────


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("R-0001", "R-0001"),
        ("r-0001", "R-0001"),  # pasa a mayusculas
        ("D000001", "D000001"),
        ("D000001", "D000001"),
        ("A-1", "A-1"),
    ],
)
def test_normaliza_remitos_alfanumericos_sin_padding(entrada, esperado):
    assert normalize_remito(entrada) == esperado


def test_normaliza_remito_con_espacios_alrededor():
    assert normalize_remito("  11278  ") == "000000011278"
    assert normalize_remito(" R-0001 ") == "R-0001"


# ─── Rechazo de valores invalidos ───────────────────────────────────────────


def test_rechaza_remito_vacio():
    with pytest.raises(ValueError, match="vacio"):
        normalize_remito("")
    with pytest.raises(ValueError, match="vacio"):
        normalize_remito("   ")
    with pytest.raises(ValueError, match="vacio"):
        normalize_remito(None)


def test_rechaza_remito_con_caracteres_invalidos():
    with pytest.raises(ValueError, match="letras, numeros y guion"):
        normalize_remito("11.278")
    with pytest.raises(ValueError, match="letras, numeros y guion"):
        normalize_remito("11 278")
    with pytest.raises(ValueError, match="letras, numeros y guion"):
        normalize_remito("11/278")
    with pytest.raises(ValueError, match="letras, numeros y guion"):
        normalize_remito("R.0001")


def test_rechaza_remito_numerico_con_mas_de_12_digitos():
    with pytest.raises(ValueError, match="12 digitos"):
        normalize_remito("1234567890123")


def test_rechaza_remito_alfanumerico_mayor_a_12_caracteres():
    with pytest.raises(ValueError, match="12 caracteres"):
        normalize_remito("R-00012345678")  # 13 chars


# ─── Constantes y helper de consulta ───────────────────────────────────────


def test_constante_max_length_coincide_con_columna():
    # Tanto ``cargacomb.remito`` como ``tablero_produccion.remito`` son
    # ``VARCHAR(12)``; la normalizacion no puede generar valores mas largos.
    assert REMITO_MAX_LENGTH == 12


def test_is_canonical_true_para_valores_ya_normalizados():
    assert is_canonical("000000011278") is True
    assert is_canonical("R-0001") is True
    assert is_canonical("") is False
    assert is_canonical(None) is False
    assert is_canonical("11278") is False  # no paddeado
    assert is_canonical("11.278") is False  # caracter invalido
