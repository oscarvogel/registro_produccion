-- Permite que un movil pertenezca a varias unidades de negocio.
-- Idempotente y compatible hacia atras con moviles.idUnidadNegocio.
--
-- El backfill inicial toma la unidad "principal" historica de cada movil
-- (columna moviles.idUnidadNegocio) y la inserta en la pivote para que
-- ningun movil quede sin unidades al activar el endpoint de produccion.
--
-- El endpoint /api/produccion/moviles pasa a filtrar por esta pivote, por
-- lo que es seguro correr este script antes de deployar el cambio de
-- codigo (no se rompe nada existente).

CREATE TABLE IF NOT EXISTS movil_unidad_negocio (
  idMovil         INT UNSIGNED NOT NULL,
  idUnidadNegocio INT UNSIGNED NOT NULL,
  PRIMARY KEY (idMovil, idUnidadNegocio),
  KEY idx_mun_un (idUnidadNegocio),
  CONSTRAINT FK_mun_movil FOREIGN KEY (idMovil)
    REFERENCES moviles (idMovil) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT FK_mun_unidad FOREIGN KEY (idUnidadNegocio)
    REFERENCES unidadnegocio (idUnidadNegocio) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO movil_unidad_negocio (idMovil, idUnidadNegocio)
SELECT idMovil, idUnidadNegocio
FROM moviles
WHERE idUnidadNegocio IS NOT NULL AND idUnidadNegocio > 0;
