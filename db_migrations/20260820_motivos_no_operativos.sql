CREATE TABLE IF NOT EXISTS motivos_no_operativos (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    codigo VARCHAR(40) NOT NULL,
    nombre VARCHAR(80) NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_motivos_no_operativos_codigo (codigo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS motivos_no_operativos_unidad_negocio (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    idMotivo INT UNSIGNED NOT NULL,
    unidad_negocio INT UNSIGNED NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (id),
    UNIQUE KEY uq_motivo_no_operativo_un (idMotivo, unidad_negocio),
    KEY idx_motivo_no_operativo_unidad (unidad_negocio, activo),
    CONSTRAINT fk_motivo_no_operativo_catalogo
        FOREIGN KEY (idMotivo) REFERENCES motivos_no_operativos(id) ON DELETE CASCADE,
    CONSTRAINT fk_motivo_no_operativo_unidad
        FOREIGN KEY (unidad_negocio) REFERENCES unidadnegocio(idUnidadNegocio) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO motivos_no_operativos (codigo, nombre, activo) VALUES
('aguardando_carreton', 'AGUARDANDO CARRETON', 1),
('condiciones_climaticas', 'CONDICIONES CLIMATICAS', 1),
('falla_mecanica', 'FALLA MECANICA', 1),
('falta_repuestos', 'FALTA REPUESTOS', 1),
('falta_operador', 'FALTA OPERADOR', 1),
('falta_unidades_materia_prima', 'FALTA UNIDADES / MATERIA PRIMA', 1),
('lavado_equipo_radiadores', 'LAVADO EQUIPO / RADIADORES', 1),
('mantenimiento_preventivo', 'MANTENIMIENTO PREVENTIVO', 1),
('otros', 'OTROS', 1),
('rotura_parte_cambio_piezas', 'ROTURA PARTE / CAMBIO PIEZAS', 1),
('traslado_mudanzas', 'TRASLADO / MUDANZAS', 1);

INSERT IGNORE INTO motivos_no_operativos_unidad_negocio (idMotivo, unidad_negocio, activo)
SELECT m.id, u.idUnidadNegocio, 1
FROM motivos_no_operativos m
CROSS JOIN unidadnegocio u;
