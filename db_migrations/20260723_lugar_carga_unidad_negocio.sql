-- Issue: allow one lugar de carga to belong to multiple business units.
-- Idempotent and backward compatible with lugarcarga.unidad_negocio.
--
-- Esquema de la tabla ya existente en el server de produccion (referencia):
--   id              INT UNSIGNED AUTO_INCREMENT PK
--   idLugarCarga    INT UNSIGNED
--   unidad_negocio  INT UNSIGNED
--   prioridad       INT  DEFAULT 100
--   es_default      TINYINT(1) DEFAULT 0
--   activo          TINYINT(1) DEFAULT 1
--   UNIQUE (idLugarCarga, unidad_negocio)
--   FKs con ON DELETE RESTRICT
--
-- Este script es seguro de correr mas de una vez: si la tabla ya existe con
-- el esquema de arriba, la seccion CREATE TABLE no hace nada. Si la fila de
-- backfill para un (lugar, unidad) ya existe, el INSERT IGNORE la respeta.

CREATE TABLE IF NOT EXISTS lugar_carga_unidad_negocio (
  id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
  idLugarCarga    INT UNSIGNED NOT NULL,
  unidad_negocio  INT UNSIGNED NOT NULL,
  prioridad       INT NOT NULL DEFAULT 100,
  es_default      TINYINT(1) NOT NULL DEFAULT 0,
  activo          TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  UNIQUE KEY uq_lugar_un (idLugarCarga, unidad_negocio),
  KEY idx_un_default (unidad_negocio, es_default, activo),
  CONSTRAINT fk_lcun_lugar FOREIGN KEY (idLugarCarga)
    REFERENCES lugarcarga (idLugarCarga) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_lcun_un FOREIGN KEY (unidad_negocio)
    REFERENCES unidadnegocio (idUnidadNegocio) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO lugar_carga_unidad_negocio (idLugarCarga, unidad_negocio)
SELECT idLugarCarga, unidad_negocio
FROM lugarcarga
WHERE unidad_negocio IS NOT NULL AND unidad_negocio > 0;
