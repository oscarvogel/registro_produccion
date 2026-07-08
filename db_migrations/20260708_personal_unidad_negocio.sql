-- Issue #65: allow one person to belong to multiple business units.
-- Idempotent and backward compatible with personal.unidad_negocio.

CREATE TABLE IF NOT EXISTS personal_unidad_negocio (
  idPersonal INT(10) UNSIGNED NOT NULL,
  idUnidadNegocio INT(10) UNSIGNED NOT NULL,
  PRIMARY KEY (idPersonal, idUnidadNegocio),
  CONSTRAINT FK_pun_personal FOREIGN KEY (idPersonal)
    REFERENCES personal (idPersonal) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT FK_pun_unidad FOREIGN KEY (idUnidadNegocio)
    REFERENCES unidadnegocio (idUnidadNegocio) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO personal_unidad_negocio (idPersonal, idUnidadNegocio)
SELECT idPersonal, unidad_negocio
FROM personal
WHERE unidad_negocio IS NOT NULL AND unidad_negocio > 0;
