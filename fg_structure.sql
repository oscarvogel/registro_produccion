-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: fg
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `absence_reports`
--

DROP TABLE IF EXISTS `absence_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `absence_reports` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `fecha` datetime NOT NULL,
  `motivo` text NOT NULL,
  `tipo_ausencia` varchar(50) NOT NULL,
  `estado` enum('pending','approved','rejected') DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_absence_reports_id` (`id`),
  CONSTRAINT `absence_reports_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `accesos`
--

DROP TABLE IF EXISTS `accesos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accesos` (
  `acc_id` int(11) NOT NULL AUTO_INCREMENT,
  `usu_id` int(11) NOT NULL,
  `for_id` int(11) NOT NULL,
  `acc_fech` datetime DEFAULT NULL,
  PRIMARY KEY (`acc_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1055 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `actas`
--

DROP TABLE IF EXISTS `actas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `actas` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `rodal_id` int(10) unsigned NOT NULL DEFAULT 0,
  `numero` varchar(30) NOT NULL DEFAULT '0',
  `vam` decimal(12,4) NOT NULL,
  `tarifa` decimal(12,4) NOT NULL,
  `extraccion` decimal(12,4) NOT NULL,
  `carga` decimal(12,4) NOT NULL,
  `periodo` char(6) DEFAULT '''''',
  PRIMARY KEY (`id`),
  KEY `FK_acta_rodal` (`rodal_id`),
  CONSTRAINT `FK_acta_rodal` FOREIGN KEY (`rodal_id`) REFERENCES `rodales` (`idRodal`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `adjuntos_orden_servicio`
--

DROP TABLE IF EXISTS `adjuntos_orden_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `adjuntos_orden_servicio` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cabecera_id` int(11) DEFAULT NULL,
  `archivo` text NOT NULL,
  `nombre_original` varchar(255) NOT NULL,
  `mime` varchar(100) NOT NULL,
  `tamano` int(11) NOT NULL,
  `usuario` varchar(30) NOT NULL,
  `creado` datetime NOT NULL,
  `token` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `adjuntosordenservicio_cabecera_id` (`cabecera_id`),
  CONSTRAINT `adjuntos_orden_servicio_ibfk_1` FOREIGN KEY (`cabecera_id`) REFERENCES `cab_orden_servicio` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `agenda`
--

DROP TABLE IF EXISTS `agenda`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `agenda` (
  `idAgenda` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `usuario` int(11) NOT NULL,
  `fecha` date NOT NULL DEFAULT '0000-00-00',
  `anticipacion` int(10) unsigned NOT NULL DEFAULT 0,
  `tarea` text DEFAULT NULL,
  `baja` bit(1) NOT NULL DEFAULT b'0',
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fechamodi` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  PRIMARY KEY (`idAgenda`),
  KEY `FK_Agenda_Usuarios` (`usuario`),
  CONSTRAINT `FK_Agenda_Usuarios` FOREIGN KEY (`usuario`) REFERENCES `usuarios` (`USU_ID`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=283 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alicuotas_impuestos`
--

DROP TABLE IF EXISTS `alicuotas_impuestos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alicuotas_impuestos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tipo_impuesto_id` varchar(10) NOT NULL,
  `porcentaje` decimal(5,2) NOT NULL,
  `descripcion` varchar(100) NOT NULL,
  `cuenta_contable_id` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `alicuotasimpuestos_tipo_impuesto_id` (`tipo_impuesto_id`),
  KEY `alicuotasimpuestos_cuenta_contable_id` (`cuenta_contable_id`),
  CONSTRAINT `alicuotas_impuestos_ibfk_1` FOREIGN KEY (`tipo_impuesto_id`) REFERENCES `tipos_impuestos` (`codigo`) ON DELETE CASCADE,
  CONSTRAINT `alicuotas_impuestos_ibfk_2` FOREIGN KEY (`cuenta_contable_id`) REFERENCES `cuentas_contables` (`codigo`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `areas`
--

DROP TABLE IF EXISTS `areas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `areas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ubicacion` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `articulos`
--

DROP TABLE IF EXISTS `articulos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `articulos` (
  `idArticulo` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `CodigoBarra` varchar(5) NOT NULL DEFAULT '',
  `idGrupoStock` char(1) NOT NULL DEFAULT 'S',
  `Nombre` varchar(80) NOT NULL DEFAULT '',
  `Detalle` text DEFAULT NULL,
  `Stock` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Precio` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `idPaniol` int(10) unsigned NOT NULL DEFAULT 1,
  `idRubro` int(10) unsigned NOT NULL DEFAULT 1,
  `Foto` varchar(200) NOT NULL DEFAULT '',
  `idTipoIva` int(10) unsigned NOT NULL DEFAULT 1,
  `CtaGasto` varchar(8) NOT NULL DEFAULT '',
  `CtaActivo` varchar(8) NOT NULL DEFAULT '',
  `TieneStock` bit(1) NOT NULL DEFAULT b'1',
  `MueveStock` bit(1) NOT NULL DEFAULT b'1',
  `_usuario` varchar(20) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  `baja` bit(1) NOT NULL DEFAULT b'0',
  PRIMARY KEY (`idArticulo`),
  KEY `idPaniol` (`idPaniol`),
  KEY `idRubro` (`idRubro`),
  CONSTRAINT `articulos_ibfk_1` FOREIGN KEY (`idPaniol`) REFERENCES `panioles` (`idPaniol`) ON UPDATE CASCADE,
  CONSTRAINT `articulos_ibfk_2` FOREIGN KEY (`idRubro`) REFERENCES `rubros` (`idRubro`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2043 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `attendance_records`
--

DROP TABLE IF EXISTS `attendance_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attendance_records` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `tipo` enum('ingreso','egreso') NOT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  `latitud_registro` float NOT NULL,
  `longitud_registro` float NOT NULL,
  `estado` enum('present','late','invalid') DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_attendance_records_id` (`id`),
  CONSTRAINT `attendance_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auditoria`
--

DROP TABLE IF EXISTS `auditoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auditoria` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `modelo` varchar(255) NOT NULL,
  `accion` varchar(255) NOT NULL,
  `registro_id` varchar(255) NOT NULL,
  `datos_antiguos` text DEFAULT NULL,
  `datos_nuevos` text DEFAULT NULL,
  `fecha` datetime NOT NULL DEFAULT current_timestamp(),
  `usuario` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=142236 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `authorized_locations`
--

DROP TABLE IF EXISTS `authorized_locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `authorized_locations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `latitud` float NOT NULL,
  `longitud` float NOT NULL,
  `radio_metros` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_authorized_locations_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bancos`
--

DROP TABLE IF EXISTS `bancos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bancos` (
  `CODIGO` varchar(3) NOT NULL DEFAULT '',
  `NOMBRE` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`CODIGO`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bienuso`
--

DROP TABLE IF EXISTS `bienuso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bienuso` (
  `idBienUso` int(11) NOT NULL AUTO_INCREMENT,
  `PerAlta` char(6) NOT NULL DEFAULT '' COMMENT 'Mes/año de alta',
  `PerBaja` char(6) NOT NULL DEFAULT '' COMMENT 'Mes/año de baja (este campo deberia alimentarse por una transaccion distinta al alta del bien en el maestro)',
  `EjerAlta` date NOT NULL DEFAULT '0000-00-00' COMMENT 'Ejercicio de alta (si fuera hoy seria 01-07-2016 a 30-06-2017)',
  `VidaUtil` int(10) unsigned NOT NULL DEFAULT 0 COMMENT 'Vida util en meses',
  `idProveedor` int(10) unsigned NOT NULL DEFAULT 0,
  `NroFac` varchar(12) NOT NULL DEFAULT '',
  `Detalle` varchar(200) NOT NULL DEFAULT '',
  `idMovil` int(10) unsigned NOT NULL DEFAULT 0 COMMENT 'Movil (si fuera uno generico, usariamos ej AD-GEN)',
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 0,
  `CtaValor` varchar(8) NOT NULL DEFAULT '' COMMENT 'Cuenta de Valor de Origen (esta seria la del activo)',
  `CtaAmortAcum` varchar(8) NOT NULL DEFAULT '' COMMENT 'Cuenta de Amortizacion acumulada (esta es la que regulariza el activo restando lo que ya fue amortizado)',
  `CtaGasto` varchar(8) NOT NULL DEFAULT '' COMMENT 'esta es la que refleja el gasto de la amortizacion',
  `CtaCtoVta` varchar(8) NOT NULL DEFAULT '' COMMENT 'Cuenta de Cto de Vta (esta es la que por diferencia se imputa cuando se vende un bien, por ejemplo, si el bien se compro en 100 y tenia 30 ya amortizado, en este caso si este bien se vende, iria por 70 a costo de venta)',
  `FechaBaja` date NOT NULL DEFAULT '0000-00-00',
  `CompBaja` varchar(12) NOT NULL DEFAULT '',
  `MotivoBaja` varchar(200) NOT NULL DEFAULT '',
  `ValorOrigen` decimal(12,2) NOT NULL DEFAULT 0.00,
  `Cliente` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`idBienUso`),
  KEY `FK_BienUsoProv` (`idProveedor`),
  KEY `FK_BienUsoMovil` (`idMovil`),
  KEY `FK_BienUsoUN` (`UnidadNegocio`),
  CONSTRAINT `FK_BienUsoProv` FOREIGN KEY (`idProveedor`) REFERENCES `proveedores` (`idProveedor`) ON UPDATE CASCADE,
  CONSTRAINT `FK_BienUsoUN` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE,
  CONSTRAINT `FK_Movil` FOREIGN KEY (`idMovil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `biomasa`
--

DROP TABLE IF EXISTS `biomasa`;
/*!50001 DROP VIEW IF EXISTS `biomasa`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `biomasa` AS SELECT
 1 AS `fecha`,
  1 AS `anio`,
  1 AS `mes`,
  1 AS `equipo`,
  1 AS `operador`,
  1 AS `operacion`,
  1 AS `produccion`,
  1 AS `hr_dia`,
  1 AS `detalle_servicio`,
  1 AS `hr_fin` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `cab_orden_servicio`
--

DROP TABLE IF EXISTS `cab_orden_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cab_orden_servicio` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `equipo_id` int(10) unsigned NOT NULL,
  `descripcion` text NOT NULL,
  `estado` varchar(20) NOT NULL,
  `cerrado_por` varchar(30) NOT NULL,
  `externo` tinyint(1) NOT NULL,
  `proveedor` int(11) NOT NULL,
  `mecanico` int(11) NOT NULL,
  `unidad_negocio_id` int(10) unsigned NOT NULL,
  `usuario` varchar(30) NOT NULL,
  `creado` datetime NOT NULL,
  `moneda_id` int(11) NOT NULL,
  `cambio` float NOT NULL,
  `orden_servicio` varchar(12) NOT NULL,
  `planilla_trabajo` tinyint(1) NOT NULL,
  `checklist` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cabordenservicio_equipo_id` (`equipo_id`),
  KEY `cabordenservicio_unidad_negocio_id` (`unidad_negocio_id`),
  KEY `fk_cab_orden_servicio_moneda_id_refs_monedas` (`moneda_id`),
  CONSTRAINT `FK_cab_orden_servicio_moviles` FOREIGN KEY (`equipo_id`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `FK_cab_orden_servicio_unidadnegocio` FOREIGN KEY (`unidad_negocio_id`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE,
  CONSTRAINT `fk_cab_orden_servicio_moneda_id_refs_monedas` FOREIGN KEY (`moneda_id`) REFERENCES `monedas` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1373 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cabordcompra`
--

DROP TABLE IF EXISTS `cabordcompra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cabordcompra` (
  `idCabOrdCompra` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idProveedor` int(10) unsigned NOT NULL,
  `Fecha` date NOT NULL DEFAULT '0000-00-00',
  `Numero` char(12) NOT NULL DEFAULT '',
  `Autorizo` varchar(30) NOT NULL DEFAULT '',
  `Enviado` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `Obs` text DEFAULT NULL,
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  PRIMARY KEY (`idCabOrdCompra`),
  KEY `idProveedor` (`idProveedor`),
  CONSTRAINT `cabordcompra_ibfk_1` FOREIGN KEY (`idProveedor`) REFERENCES `proveedores` (`idProveedor`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cabordenservicio`
--

DROP TABLE IF EXISTS `cabordenservicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cabordenservicio` (
  `idCabOrdenServicio` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Fecha` date NOT NULL DEFAULT '0000-00-00',
  `HoraIngreso` char(5) NOT NULL DEFAULT '00:00',
  `HoraSalida` char(5) NOT NULL DEFAULT '00:00',
  `Movil` int(10) unsigned NOT NULL DEFAULT 0,
  `Estado` char(1) NOT NULL DEFAULT 'A',
  `CerradoPor` varchar(30) NOT NULL DEFAULT '',
  `DetallePreventivo` text DEFAULT NULL,
  `DetalleCorrectivo` text DEFAULT NULL,
  `Externo` bit(1) NOT NULL DEFAULT b'0',
  `idRemolque` char(17) NOT NULL DEFAULT '',
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  PRIMARY KEY (`idCabOrdenServicio`),
  KEY `Movil` (`Movil`),
  KEY `UnidadNegocio` (`UnidadNegocio`),
  CONSTRAINT `FK_Movil_OS` FOREIGN KEY (`Movil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `FK_UN_OS` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5450 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cabpedpro`
--

DROP TABLE IF EXISTS `cabpedpro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cabpedpro` (
  `idCabPedPro` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Proveedor` int(10) unsigned NOT NULL,
  `Fecha` date NOT NULL DEFAULT '0000-00-00',
  `Numero` varchar(12) NOT NULL DEFAULT '',
  `Realizado` varchar(30) NOT NULL DEFAULT '',
  `Autorizado` varchar(30) NOT NULL DEFAULT '',
  `obs` text DEFAULT NULL,
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  PRIMARY KEY (`idCabPedPro`),
  KEY `Proveedor` (`Proveedor`),
  CONSTRAINT `cabpedpro_ibfk_1` FOREIGN KEY (`Proveedor`) REFERENCES `proveedores` (`idProveedor`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cabpoliza`
--

DROP TABLE IF EXISTS `cabpoliza`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cabpoliza` (
  `idCabPoliza` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idCompSeg` int(10) unsigned NOT NULL,
  `Entidad` char(3) NOT NULL DEFAULT '',
  `NPoliza` varchar(30) NOT NULL DEFAULT '',
  `NEndoso` varchar(30) NOT NULL DEFAULT '',
  `Premio` decimal(12,2) NOT NULL DEFAULT 0.00,
  `ImpRec` decimal(12,2) NOT NULL DEFAULT 0.00,
  `Prima` decimal(12,2) NOT NULL DEFAULT 0.00,
  `CantCuotas` int(10) unsigned NOT NULL DEFAULT 0,
  `Emision` date NOT NULL DEFAULT '0000-00-00',
  `Venc1erCuota` date NOT NULL DEFAULT '0000-00-00',
  `Vencimiento` date NOT NULL DEFAULT '0000-00-00',
  `CostoSIVA` decimal(12,2) NOT NULL DEFAULT 0.00,
  `InicioCobertura` date NOT NULL DEFAULT '0000-00-00',
  `Observaciones` text DEFAULT NULL,
  `Estado` char(255) NOT NULL DEFAULT '''A''',
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`idCabPoliza`),
  KEY `FK_Poliza_Compseg` (`idCompSeg`),
  KEY `FK_Poliza_Bancos` (`Entidad`),
  CONSTRAINT `FK_Poliza_Bancos` FOREIGN KEY (`Entidad`) REFERENCES `bancos` (`CODIGO`) ON UPDATE CASCADE,
  CONSTRAINT `FK_Poliza_Compseg` FOREIGN KEY (`idCompSeg`) REFERENCES `compseguro` (`idCompSeguro`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=321 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cabprestamo`
--

DROP TABLE IF EXISTS `cabprestamo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cabprestamo` (
  `idCabPrestamo` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `banco` char(3) NOT NULL DEFAULT '',
  `modalidad` varchar(150) NOT NULL DEFAULT '',
  `moneda` char(3) NOT NULL DEFAULT '',
  `tasa` decimal(12,6) NOT NULL DEFAULT 0.000000,
  `tea` decimal(12,6) NOT NULL DEFAULT 0.000000,
  `cft` decimal(12,6) NOT NULL DEFAULT 0.000000,
  `tipotasa` char(1) NOT NULL DEFAULT '',
  `idMovil` int(10) unsigned NOT NULL DEFAULT 0,
  `nContrato` varchar(30) NOT NULL DEFAULT '',
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  `Estado` char(255) NOT NULL DEFAULT '''A''',
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`idCabPrestamo`),
  KEY `banco` (`banco`),
  KEY `idMovil` (`idMovil`),
  KEY `UnidadNegocio` (`UnidadNegocio`),
  CONSTRAINT `FK_Movil_Prestamo` FOREIGN KEY (`idMovil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `cabprestamo_ibfk_1` FOREIGN KEY (`banco`) REFERENCES `bancos` (`CODIGO`) ON UPDATE CASCADE,
  CONSTRAINT `cabprestamo_ibfk_3` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cajaherramienta`
--

DROP TABLE IF EXISTS `cajaherramienta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cajaherramienta` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Detalle` varchar(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cajas_bancos`
--

DROP TABLE IF EXISTS `cajas_bancos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cajas_bancos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `caja` tinyint(1) NOT NULL,
  `cta_banco` varchar(100) NOT NULL,
  `moneda_id` int(11) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `cuenta_contable_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cajabanco_nombre` (`nombre`),
  UNIQUE KEY `cajabanco_nombre_moneda_id` (`nombre`,`moneda_id`),
  KEY `cajabanco_moneda_id` (`moneda_id`),
  CONSTRAINT `cajas_bancos_ibfk_1` FOREIGN KEY (`moneda_id`) REFERENCES `monedas` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `cajas_bancos_chk_1` CHECK (0 <> `caja` or `cta_banco` is not null)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cargacomb`
--

DROP TABLE IF EXISTS `cargacomb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cargacomb` (
  `idCargaComb` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idMovil` int(10) unsigned NOT NULL DEFAULT 0,
  `idTipoComb` int(10) unsigned NOT NULL,
  `Fecha` date DEFAULT NULL,
  `KM` int(10) unsigned NOT NULL DEFAULT 0,
  `PreXLitro` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Litros` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `idLugarCarga` int(10) unsigned NOT NULL DEFAULT 1,
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  `idPaniol` int(10) unsigned NOT NULL DEFAULT 1,
  `personal` int(10) unsigned NOT NULL DEFAULT 1,
  `idtabla` char(12) NOT NULL DEFAULT '0',
  `remito` char(12) NOT NULL DEFAULT '0',
  `tipo_mov` char(1) NOT NULL DEFAULT '',
  `comprobante` varchar(12) NOT NULL DEFAULT '',
  `modificado` tinyint(4) NOT NULL DEFAULT 0,
  `pase` tinyint(1) NOT NULL DEFAULT 0,
  `tabla` varchar(50) NOT NULL DEFAULT '0',
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` date DEFAULT NULL,
  `_hora` char(8) NOT NULL DEFAULT '',
  `remito2` varchar(12) DEFAULT NULL,
  `remito3` varchar(12) DEFAULT NULL,
  `observaciones` varchar(200) DEFAULT '',
  `ajuste_stock` tinyint(4) DEFAULT 0,
  PRIMARY KEY (`idCargaComb`),
  KEY `idMovil` (`idMovil`),
  KEY `idTipoComb` (`idTipoComb`),
  KEY `idLugarCarga` (`idLugarCarga`),
  KEY `UnidadNegocio` (`UnidadNegocio`),
  KEY `idPaniol` (`idPaniol`),
  KEY `FK_Personal_comb` (`personal`),
  CONSTRAINT `FK_Movil_Comb` FOREIGN KEY (`idMovil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `FK_Personal_comb` FOREIGN KEY (`personal`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE,
  CONSTRAINT `cargacomb_ibfk_2` FOREIGN KEY (`idTipoComb`) REFERENCES `tipocomb` (`idTipoComb`) ON UPDATE CASCADE,
  CONSTRAINT `cargacomb_ibfk_3` FOREIGN KEY (`idLugarCarga`) REFERENCES `lugarcarga` (`idLugarCarga`) ON UPDATE CASCADE,
  CONSTRAINT `cargacomb_ibfk_4` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE,
  CONSTRAINT `cargacomb_ibfk_5` FOREIGN KEY (`idPaniol`) REFERENCES `panioles` (`idPaniol`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=97740 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `centrocostos`
--

DROP TABLE IF EXISTS `centrocostos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `centrocostos` (
  `idCentroCosto` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`idCentroCosto`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `checklist_equipo`
--

DROP TABLE IF EXISTS `checklist_equipo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `checklist_equipo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cabecera_id` int(11) DEFAULT NULL,
  `tipo_checklist_id` int(11) NOT NULL,
  `detalle_checklist_id` int(11) DEFAULT NULL,
  `bien` tinyint(1) NOT NULL,
  `mal` tinyint(1) NOT NULL,
  `regular` tinyint(1) NOT NULL,
  `observaciones` varchar(255) NOT NULL,
  `fecha_ultimo_check` date DEFAULT NULL,
  `km_hora` float NOT NULL,
  `usuario` varchar(30) NOT NULL,
  `creado` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `checklistequipo_cabecera_id` (`cabecera_id`),
  KEY `checklistequipo_tipo_checklist_id` (`tipo_checklist_id`),
  KEY `checklistequipo_detalle_checklist_id` (`detalle_checklist_id`),
  CONSTRAINT `checklist_equipo_ibfk_1` FOREIGN KEY (`cabecera_id`) REFERENCES `cab_orden_servicio` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `checklist_equipo_ibfk_2` FOREIGN KEY (`tipo_checklist_id`) REFERENCES `tipo_checklist` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `checklist_equipo_ibfk_3` FOREIGN KEY (`detalle_checklist_id`) REFERENCES `detalle_checklist` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_checklist_equipo_detalle_checklist_id_refs_detalle_checklist` FOREIGN KEY (`detalle_checklist_id`) REFERENCES `detalle_checklist` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=361 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `choferes_equipos`
--

DROP TABLE IF EXISTS `choferes_equipos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `choferes_equipos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `empleado_id` int(11) NOT NULL,
  `movil_id` int(11) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `choferequipo_empleado_id` (`empleado_id`),
  KEY `choferequipo_movil_id` (`movil_id`),
  CONSTRAINT `choferes_equipos_ibfk_1` FOREIGN KEY (`empleado_id`) REFERENCES `empleados` (`id`),
  CONSTRAINT `choferes_equipos_ibfk_2` FOREIGN KEY (`movil_id`) REFERENCES `equipos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cliente` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cuit` varchar(30) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `razon_social` varchar(50) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL DEFAULT '',
  `domicilio` varchar(50) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL DEFAULT '',
  `operaciones` tinyint(1) NOT NULL DEFAULT 1,
  `localidad` varchar(50) NOT NULL DEFAULT '',
  `telefono` varchar(50) NOT NULL DEFAULT '',
  `codigo_postal` varchar(10) NOT NULL DEFAULT '',
  `email` varchar(150) NOT NULL DEFAULT '',
  `cat_iva` varchar(10) NOT NULL DEFAULT '',
  `provincia` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `CUIT` (`cuit`)
) ENGINE=InnoDB AUTO_INCREMENT=2844 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `combustible`
--

DROP TABLE IF EXISTS `combustible`;
/*!50001 DROP VIEW IF EXISTS `combustible`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `combustible` AS SELECT
 1 AS `anio`,
  1 AS `mes`,
  1 AS `un`,
  1 AS `movil`,
  1 AS `patente`,
  1 AS `nombre`,
  1 AS `litros`,
  1 AS `KM`,
  1 AS `fecha` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `compseguro`
--

DROP TABLE IF EXISTS `compseguro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `compseguro` (
  `idCompSeguro` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(80) NOT NULL DEFAULT '',
  `Domicilio` varchar(80) NOT NULL DEFAULT '',
  `Telefono` varchar(80) NOT NULL DEFAULT '',
  `Contacto` varchar(80) NOT NULL DEFAULT '',
  `Correo` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`idCompSeguro`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `concepto_rm`
--

DROP TABLE IF EXISTS `concepto_rm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `concepto_rm` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `detalle` varchar(80) NOT NULL DEFAULT '',
  `grupo` int(10) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `conceptoliquidacion`
--

DROP TABLE IF EXISTS `conceptoliquidacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `conceptoliquidacion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `detalle` varchar(80) NOT NULL,
  `importe` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `unidad` varchar(10) NOT NULL,
  `tipo` char(1) NOT NULL DEFAULT 'F',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=824 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `configuracion_contable`
--

DROP TABLE IF EXISTS `configuracion_contable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `configuracion_contable` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `evento_tipo` varchar(50) NOT NULL,
  `pais` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `configuracion_detalle`
--

DROP TABLE IF EXISTS `configuracion_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `configuracion_detalle` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `configuracion_base_id` int(11) NOT NULL,
  `cuenta_contable_id` varchar(20) NOT NULL,
  `tipo_concepto` varchar(20) NOT NULL,
  `debe_haber` varchar(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `configuraciondetalle_configuracion_base_id_tipo_concepto` (`configuracion_base_id`,`tipo_concepto`),
  KEY `configuraciondetalle_configuracion_base_id` (`configuracion_base_id`),
  KEY `configuraciondetalle_cuenta_contable_id` (`cuenta_contable_id`),
  CONSTRAINT `configuracion_detalle_ibfk_1` FOREIGN KEY (`configuracion_base_id`) REFERENCES `configuracion_contable` (`id`),
  CONSTRAINT `configuracion_detalle_ibfk_2` FOREIGN KEY (`cuenta_contable_id`) REFERENCES `cuentas_contables` (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `consumos`
--

DROP TABLE IF EXISTS `consumos`;
/*!50001 DROP VIEW IF EXISTS `consumos`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `consumos` AS SELECT
 1 AS `anio`,
  1 AS `mes`,
  1 AS `idMovil`,
  1 AS `patente`,
  1 AS `detalle`,
  1 AS `litros`,
  1 AS `km`,
  1 AS `promedio`,
  1 AS `Nombre` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `correoprov`
--

DROP TABLE IF EXISTS `correoprov`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `correoprov` (
  `idCorreoProv` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Proveedor` int(10) unsigned NOT NULL DEFAULT 1,
  `correo` varchar(200) NOT NULL DEFAULT '',
  PRIMARY KEY (`idCorreoProv`),
  KEY `Proveedor` (`Proveedor`),
  CONSTRAINT `correoprov_ibfk_1` FOREIGN KEY (`Proveedor`) REFERENCES `proveedores` (`idProveedor`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `cosechas`
--

DROP TABLE IF EXISTS `cosechas`;
/*!50001 DROP VIEW IF EXISTS `cosechas`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `cosechas` AS SELECT
 1 AS `un`,
  1 AS `equipo`,
  1 AS `mes`,
  1 AS `anio`,
  1 AS `fecha`,
  1 AS `produccion`,
  1 AS `plantas`,
  1 AS `operador`,
  1 AS `operacion`,
  1 AS `acta`,
  1 AS `Detalle` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `costo_tango`
--

DROP TABLE IF EXISTS `costo_tango`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `costo_tango` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `articulo_id` int(11) NOT NULL,
  `tango_id` int(11) NOT NULL,
  `codigo_costo` int(11) NOT NULL,
  `precio_repo` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `costotango_articulo_id` (`articulo_id`),
  CONSTRAINT `costo_tango_ibfk_1` FOREIGN KEY (`articulo_id`) REFERENCES `repuestos` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2551 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cta_contable_crm`
--

DROP TABLE IF EXISTS `cta_contable_crm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cta_contable_crm` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_concepto_rm` int(10) unsigned NOT NULL,
  `id_cta_contable` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_concepto_rm` (`id_concepto_rm`),
  KEY `id_cta_contable` (`id_cta_contable`),
  CONSTRAINT `cta_contable_crm_ibfk_1` FOREIGN KEY (`id_concepto_rm`) REFERENCES `concepto_rm` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `cta_contable_crm_ibfk_2` FOREIGN KEY (`id_cta_contable`) REFERENCES `cuentacontable` (`codigo`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cuentacontable`
--

DROP TABLE IF EXISTS `cuentacontable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cuentacontable` (
  `codigo` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(50) DEFAULT '',
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=49101003 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cuentas_contables`
--

DROP TABLE IF EXISTS `cuentas_contables`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cuentas_contables` (
  `codigo` varchar(20) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `nivel` int(11) NOT NULL,
  `cuenta_padre_id` varchar(20) DEFAULT NULL,
  `imputable` tinyint(1) NOT NULL,
  `tipo` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`codigo`),
  KEY `cuentascontables_cuenta_padre_id` (`cuenta_padre_id`),
  CONSTRAINT `cuentas_contables_ibfk_1` FOREIGN KEY (`cuenta_padre_id`) REFERENCES `cuentas_contables` (`codigo`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datos_frente`
--

DROP TABLE IF EXISTS `datos_frente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datos_frente` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `un` varchar(20) NOT NULL DEFAULT '',
  `dato` varchar(50) NOT NULL DEFAULT '',
  `valor` varchar(50) NOT NULL DEFAULT '',
  `codigo` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `datos_gestya`
--

DROP TABLE IF EXISTS `datos_gestya`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `datos_gestya` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `movil` int(10) unsigned NOT NULL DEFAULT 0,
  `nombre_gestya` varchar(150) NOT NULL DEFAULT '',
  `fecha` date NOT NULL,
  `distancia_calculada` int(11) NOT NULL DEFAULT 0,
  `distancia_reportada` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `FK_gestya_movils` (`movil`),
  CONSTRAINT `FK_gestya_movils` FOREIGN KEY (`movil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6192 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `despacho`
--

DROP TABLE IF EXISTS `despacho`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `despacho` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `predio` int(10) unsigned NOT NULL,
  `camion` varchar(12) NOT NULL DEFAULT '',
  `fecha` date NOT NULL DEFAULT '0000-00-00',
  `hr_llegada` time NOT NULL DEFAULT '00:00:00',
  `hr_salida` time NOT NULL DEFAULT '00:00:00',
  `producto` varchar(15) NOT NULL DEFAULT '',
  `volumen` int(11) NOT NULL DEFAULT 0,
  `tcarguio` int(10) unsigned NOT NULL DEFAULT 0 COMMENT 'Tiempo de Carguio en minutos',
  `neto` int(10) unsigned NOT NULL DEFAULT 0,
  `remito` int(10) unsigned NOT NULL DEFAULT 0,
  `hr_llegada_efectiva` time NOT NULL DEFAULT '00:00:00',
  `operador` int(10) unsigned NOT NULL DEFAULT 1,
  `fuera_programa` tinyint(3) unsigned NOT NULL DEFAULT 0,
  `UN` int(10) unsigned NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `predio` (`predio`),
  KEY `operador` (`operador`),
  KEY `FK_despacho_un` (`UN`),
  CONSTRAINT `FK_despacho_un` FOREIGN KEY (`UN`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE,
  CONSTRAINT `despacho_ibfk_1` FOREIGN KEY (`predio`) REFERENCES `predios` (`idPredio`) ON UPDATE CASCADE,
  CONSTRAINT `despacho_ibfk_2` FOREIGN KEY (`operador`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1703 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `det_orden_servicio`
--

DROP TABLE IF EXISTS `det_orden_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `det_orden_servicio` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cabecera_id` int(11) NOT NULL,
  `tipo_tarea_id` int(11) NOT NULL,
  `repuesto_id` int(11) DEFAULT NULL,
  `cantidad` float NOT NULL,
  `precio_unitario` float NOT NULL,
  `preventivo` tinyint(1) NOT NULL,
  `correctivo` tinyint(1) NOT NULL,
  `realizado` tinyint(1) NOT NULL,
  `km_hora` float NOT NULL,
  `diferencia` float NOT NULL,
  `detalle` text NOT NULL,
  `fecha_realizacion` date DEFAULT NULL,
  `mecanico` int(11) NOT NULL,
  `moneda_id` int(11) NOT NULL,
  `cambio` float NOT NULL,
  `observaciones` varchar(200) NOT NULL,
  `hora_inicio` time DEFAULT NULL,
  `hora_fin` time DEFAULT NULL,
  `horas_extras` time DEFAULT NULL,
  `sector_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `detordenservicio_cabecera_id` (`cabecera_id`),
  KEY `detordenservicio_tipo_tarea_id` (`tipo_tarea_id`),
  KEY `detordenservicio_repuesto_id` (`repuesto_id`),
  KEY `fk_det_orden_servicio_moneda_id_refs_monedas` (`moneda_id`),
  CONSTRAINT `det_orden_servicio_ibfk_1` FOREIGN KEY (`cabecera_id`) REFERENCES `cab_orden_servicio` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `det_orden_servicio_ibfk_2` FOREIGN KEY (`tipo_tarea_id`) REFERENCES `tipostareas` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `det_orden_servicio_ibfk_3` FOREIGN KEY (`repuesto_id`) REFERENCES `repuestos` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_det_orden_servicio_moneda_id_refs_monedas` FOREIGN KEY (`moneda_id`) REFERENCES `monedas` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4107 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `detalle_checklist`
--

DROP TABLE IF EXISTS `detalle_checklist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `detalle_checklist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tipo_checklist_id` int(11) NOT NULL,
  `item` varchar(200) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `usuario` varchar(30) NOT NULL,
  `creado` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `detallechecklist_tipo_checklist_id` (`tipo_checklist_id`),
  CONSTRAINT `detalle_checklist_ibfk_1` FOREIGN KEY (`tipo_checklist_id`) REFERENCES `tipo_checklist` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `detalle_rem_carreton`
--

DROP TABLE IF EXISTS `detalle_rem_carreton`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `detalle_rem_carreton` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `cabecera_id` int(10) unsigned NOT NULL DEFAULT 0,
  `cliente_id` varchar(30) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL DEFAULT '0',
  `origen` varchar(30) NOT NULL,
  `destino` varchar(30) NOT NULL,
  `detalle` varchar(80) NOT NULL,
  `tarifa` decimal(12,2) NOT NULL DEFAULT 0.00,
  `tc` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `let_comp` varchar(5) NOT NULL DEFAULT '0',
  `pto_vta` varchar(5) NOT NULL DEFAULT '0',
  `numero` varchar(8) NOT NULL DEFAULT '0',
  `km_cargado` decimal(12,2) NOT NULL DEFAULT 0.00,
  `km_vacio` decimal(12,2) NOT NULL DEFAULT 0.00,
  `frente_id` int(10) unsigned NOT NULL DEFAULT 0,
  `hes` varchar(50) NOT NULL DEFAULT '0',
  `pagado` tinyint(4) NOT NULL DEFAULT 0,
  `solicitado` tinyint(4) NOT NULL DEFAULT 0,
  `black` tinyint(4) NOT NULL DEFAULT 0,
  `ptovta_recibo` varchar(5) NOT NULL,
  `numero_recibo` varchar(8) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_detalle_cliente` (`cliente_id`),
  KEY `FK_detalle_un` (`frente_id`) USING BTREE,
  CONSTRAINT `FK_detalle_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `cliente` (`cuit`) ON UPDATE CASCADE,
  CONSTRAINT `FK_detalle_un` FOREIGN KEY (`frente_id`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1687 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `detordcompra`
--

DROP TABLE IF EXISTS `detordcompra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `detordcompra` (
  `idDetOrdCompra` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idCabOrdCompra` int(10) unsigned NOT NULL DEFAULT 0,
  `idArticulo` int(10) unsigned NOT NULL DEFAULT 0,
  `Cantidad` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Unitario` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Detalle` varchar(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`idDetOrdCompra`),
  KEY `idCabOrdCompra` (`idCabOrdCompra`),
  KEY `idArticulo` (`idArticulo`),
  CONSTRAINT `detordcompra_ibfk_1` FOREIGN KEY (`idCabOrdCompra`) REFERENCES `cabordcompra` (`idCabOrdCompra`) ON UPDATE CASCADE,
  CONSTRAINT `detordcompra_ibfk_2` FOREIGN KEY (`idArticulo`) REFERENCES `articulos` (`idArticulo`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `detordservicio`
--

DROP TABLE IF EXISTS `detordservicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `detordservicio` (
  `idDetOrdServicio` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idCabOrdServicio` int(10) unsigned NOT NULL,
  `idPlanMant` int(10) unsigned NOT NULL DEFAULT 0,
  `idArticulo` int(10) unsigned NOT NULL,
  `Cantidad` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `PreUnitario` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `KMHora` int(10) unsigned NOT NULL DEFAULT 0,
  `Detalle` text DEFAULT NULL,
  `TipoOrden` char(1) NOT NULL DEFAULT '',
  `Correctivo` bit(1) NOT NULL DEFAULT b'0',
  `Preventivo` bit(1) NOT NULL DEFAULT b'0',
  `Diferencia` int(11) NOT NULL DEFAULT 0,
  `Remolque` bit(1) NOT NULL DEFAULT b'0',
  PRIMARY KEY (`idDetOrdServicio`),
  KEY `idCabOrdServicio` (`idCabOrdServicio`),
  KEY `idArticulo` (`idArticulo`),
  CONSTRAINT `detordservicio_ibfk_1` FOREIGN KEY (`idCabOrdServicio`) REFERENCES `cabordenservicio` (`idCabOrdenServicio`) ON UPDATE CASCADE,
  CONSTRAINT `detordservicio_ibfk_2` FOREIGN KEY (`idArticulo`) REFERENCES `articulos` (`idArticulo`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=30849 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `detpedpro`
--

DROP TABLE IF EXISTS `detpedpro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `detpedpro` (
  `idDetPedPro` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idCabPedPro` int(10) unsigned NOT NULL,
  `idArticulo` int(10) unsigned NOT NULL,
  `Detalle` varchar(200) NOT NULL DEFAULT '',
  `Cantidad` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Unitario` decimal(12,4) NOT NULL DEFAULT 0.0000,
  PRIMARY KEY (`idDetPedPro`),
  KEY `idCabPedPro` (`idCabPedPro`),
  KEY `idArticulo` (`idArticulo`),
  CONSTRAINT `detpedpro_ibfk_1` FOREIGN KEY (`idCabPedPro`) REFERENCES `cabpedpro` (`idCabPedPro`) ON UPDATE CASCADE,
  CONSTRAINT `detpedpro_ibfk_2` FOREIGN KEY (`idArticulo`) REFERENCES `articulos` (`idArticulo`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `detpoliza`
--

DROP TABLE IF EXISTS `detpoliza`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `detpoliza` (
  `idDetPoliza` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idCabPoliza` int(10) unsigned NOT NULL,
  `idMovil` int(10) unsigned NOT NULL DEFAULT 0,
  `ImpAsegurado` decimal(12,2) NOT NULL DEFAULT 0.00,
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  PRIMARY KEY (`idDetPoliza`),
  KEY `FK_DetPoliza_CabPoliza` (`idCabPoliza`),
  KEY `FK_DetPoliza_Movil` (`idMovil`),
  KEY `UnidadNegocio` (`UnidadNegocio`),
  CONSTRAINT `FK_DetPoliza_CabPoliza` FOREIGN KEY (`idCabPoliza`) REFERENCES `cabpoliza` (`idCabPoliza`) ON UPDATE CASCADE,
  CONSTRAINT `FK_Detpoliza_Movil` FOREIGN KEY (`idMovil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `detpoliza_ibfk_1` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=712 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `detprestamo`
--

DROP TABLE IF EXISTS `detprestamo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `detprestamo` (
  `idDetPrestamo` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idCabPrestamo` int(10) unsigned NOT NULL DEFAULT 0,
  `NCuota` int(10) unsigned NOT NULL DEFAULT 0,
  `Vence` date NOT NULL DEFAULT '0000-00-00',
  `capital` decimal(12,2) NOT NULL DEFAULT 0.00,
  `interes` decimal(12,2) NOT NULL DEFAULT 0.00,
  `impuestos` decimal(12,2) NOT NULL DEFAULT 0.00,
  `seguros` decimal(12,2) NOT NULL DEFAULT 0.00,
  `comisiones` decimal(12,2) NOT NULL DEFAULT 0.00,
  `cuota` decimal(12,2) NOT NULL DEFAULT 0.00,
  `numcheque` varchar(15) NOT NULL DEFAULT '',
  PRIMARY KEY (`idDetPrestamo`),
  KEY `idCabPrestamo` (`idCabPrestamo`),
  CONSTRAINT `detprestamo_ibfk_1` FOREIGN KEY (`idCabPrestamo`) REFERENCES `cabprestamo` (`idCabPrestamo`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4310 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK (`action_flag` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `estadoman`
--

DROP TABLE IF EXISTS `estadoman`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `estadoman` (
  `idEstadoMan` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Detalle` varchar(30) NOT NULL DEFAULT '',
  PRIMARY KEY (`idEstadoMan`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `feriados`
--

DROP TABLE IF EXISTS `feriados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `feriados` (
  `fecha` date NOT NULL,
  `detalle` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`fecha`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fichapersonal`
--

DROP TABLE IF EXISTS `fichapersonal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fichapersonal` (
  `idFichaPer` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idPersonal` int(10) unsigned NOT NULL,
  `Fecha` date NOT NULL DEFAULT '0000-00-00',
  `Detalle` varchar(200) NOT NULL DEFAULT '',
  `Debe` decimal(12,2) NOT NULL DEFAULT 0.00,
  `Haber` decimal(12,2) NOT NULL DEFAULT 0.00,
  `Periodo` char(6) NOT NULL DEFAULT '',
  `Baja` bit(1) NOT NULL DEFAULT b'0',
  `Unitario` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Toneladas` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Horas` decimal(12,2) NOT NULL DEFAULT 0.00,
  `Cambio` decimal(12,4) unsigned NOT NULL DEFAULT 0.0000,
  `concepto_liquidacion` int(11) NOT NULL DEFAULT 101,
  `acta` int(10) unsigned NOT NULL DEFAULT 0,
  `rodal` int(10) unsigned NOT NULL DEFAULT 0,
  `_usuario` varchar(20) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  `unidad_negocio` int(10) unsigned NOT NULL DEFAULT 1,
  PRIMARY KEY (`idFichaPer`),
  KEY `idPersonal` (`idPersonal`),
  KEY `concepto_liquidacion` (`concepto_liquidacion`),
  KEY `FK_ficha_un` (`unidad_negocio`),
  CONSTRAINT `FK_ficha_un` FOREIGN KEY (`unidad_negocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE,
  CONSTRAINT `fichapersonal_ibfk_1` FOREIGN KEY (`idPersonal`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE,
  CONSTRAINT `fichapersonal_ibfk_2` FOREIGN KEY (`concepto_liquidacion`) REFERENCES `conceptoliquidacion` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=66816 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `formula`
--

DROP TABLE IF EXISTS `formula`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `formula` (
  `for_id` int(11) NOT NULL AUTO_INCREMENT,
  `for_nomb` char(50) NOT NULL,
  `sis_id` smallint(6) NOT NULL,
  `tfo_id` smallint(6) NOT NULL,
  `for_orde` int(11) NOT NULL,
  `for_pare` int(11) NOT NULL DEFAULT 0,
  `for_arch` varchar(150) DEFAULT '',
  `for_valid` varchar(50) DEFAULT '',
  `for_imag` char(150) DEFAULT '',
  `gfo_id` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`for_id`)
) ENGINE=InnoDB AUTO_INCREMENT=698 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gastomovil`
--

DROP TABLE IF EXISTS `gastomovil`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gastomovil` (
  `idGastoMovil` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idMovil` int(10) unsigned NOT NULL DEFAULT 0,
  `idPaniol` int(10) unsigned NOT NULL DEFAULT 0,
  `idArticulo` int(10) unsigned NOT NULL,
  `idTipoComp` int(10) unsigned NOT NULL,
  `Numero` char(12) NOT NULL DEFAULT '',
  `Cantidad` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Unitario` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Fecha` date NOT NULL DEFAULT '0000-00-00',
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  PRIMARY KEY (`idGastoMovil`),
  KEY `idMovil` (`idMovil`),
  KEY `idPaniol` (`idPaniol`),
  KEY `idArticulo` (`idArticulo`),
  KEY `idTipoComp` (`idTipoComp`),
  KEY `UnidadNegocio` (`UnidadNegocio`),
  CONSTRAINT `FK_GastoMovil_Movil` FOREIGN KEY (`idMovil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `gastomovil_ibfk_2` FOREIGN KEY (`idPaniol`) REFERENCES `panioles` (`idPaniol`) ON UPDATE CASCADE,
  CONSTRAINT `gastomovil_ibfk_3` FOREIGN KEY (`idArticulo`) REFERENCES `articulos` (`idArticulo`) ON UPDATE CASCADE,
  CONSTRAINT `gastomovil_ibfk_4` FOREIGN KEY (`idTipoComp`) REFERENCES `tipcomp` (`Codigo`) ON UPDATE CASCADE,
  CONSTRAINT `gastomovil_ibfk_5` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=20677 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gruform`
--

DROP TABLE IF EXISTS `gruform`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gruform` (
  `gfo_id` smallint(6) NOT NULL,
  `gfo_nomb` char(30) NOT NULL,
  PRIMARY KEY (`gfo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `grupostock`
--

DROP TABLE IF EXISTS `grupostock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `grupostock` (
  `idGrupoStock` char(1) NOT NULL DEFAULT '',
  `Detalle` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`idGrupoStock`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `herramientas`
--

DROP TABLE IF EXISTS `herramientas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `herramientas` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Detalle` varchar(100) NOT NULL DEFAULT '',
  `caja_id` int(10) unsigned NOT NULL DEFAULT 1,
  `Cantidad` decimal(12,2) NOT NULL DEFAULT 0.00,
  `Precio` decimal(12,2) NOT NULL DEFAULT 0.00 COMMENT 'Precio Unitario',
  `articulo_roble` varchar(30) DEFAULT NULL,
  `fecha_compra` date NOT NULL,
  `ptovta` varchar(5) NOT NULL,
  `numero` varchar(8) NOT NULL,
  `baja` tinyint(4) NOT NULL DEFAULT 0,
  `motivo_baja` text NOT NULL,
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  `nserie` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `FK_herramienta_caja` (`caja_id`),
  CONSTRAINT `FK_herramienta_caja` FOREIGN KEY (`caja_id`) REFERENCES `cajaherramienta` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1482 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `historial_estado_orden_servicio`
--

DROP TABLE IF EXISTS `historial_estado_orden_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `historial_estado_orden_servicio` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cabecera_id` int(11) NOT NULL,
  `fecha_hora` datetime NOT NULL,
  `usuario` varchar(50) NOT NULL,
  `estado_anterior` varchar(50) NOT NULL,
  `estado_nuevo` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `historialestadoordenservicio_cabecera_id` (`cabecera_id`),
  CONSTRAINT `historial_estado_orden_servicio_ibfk_1` FOREIGN KEY (`cabecera_id`) REFERENCES `cab_orden_servicio` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=748 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `historico_conc_liq`
--

DROP TABLE IF EXISTS `historico_conc_liq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `historico_conc_liq` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_concepto_liquidacion` int(11) NOT NULL,
  `fecha` date NOT NULL DEFAULT '0000-00-00',
  `importe_viejo` decimal(14,4) NOT NULL DEFAULT 0.0000,
  `importe_nuevo` decimal(14,4) NOT NULL DEFAULT 0.0000,
  PRIMARY KEY (`id`),
  KEY `historico_conc_liq_ibfk_1` (`id_concepto_liquidacion`),
  CONSTRAINT `historico_conc_liq_ibfk_1` FOREIGN KEY (`id_concepto_liquidacion`) REFERENCES `conceptoliquidacion` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1291 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `historicoarticulo`
--

DROP TABLE IF EXISTS `historicoarticulo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `historicoarticulo` (
  `idHistoricoArticulo` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idArticulo` int(10) unsigned NOT NULL,
  `Fecha` date NOT NULL DEFAULT '0000-00-00',
  `Precio` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  PRIMARY KEY (`idHistoricoArticulo`)
) ENGINE=InnoDB AUTO_INCREMENT=9304 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `historigen`
--

DROP TABLE IF EXISTS `historigen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `historigen` (
  `idHistOrigen` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idOrigen` int(10) unsigned NOT NULL DEFAULT 0,
  `Precio` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Fecha` date NOT NULL DEFAULT '0000-00-00',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '',
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  PRIMARY KEY (`idHistOrigen`),
  KEY `idOrigen` (`idOrigen`),
  CONSTRAINT `historigen_ibfk_1` FOREIGN KEY (`idOrigen`) REFERENCES `origen` (`idOrigen`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=330 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `horas`
--

DROP TABLE IF EXISTS `horas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `horas` (
  `idHora` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idEmple` int(10) unsigned NOT NULL,
  `Fecha` date NOT NULL DEFAULT '0000-00-00',
  `Entrada` char(8) NOT NULL DEFAULT '',
  `Salida` char(8) NOT NULL DEFAULT '',
  `FotoEntrada` varchar(200) NOT NULL DEFAULT '',
  `FotoSalida` varchar(200) NOT NULL DEFAULT '',
  PRIMARY KEY (`idHora`),
  KEY `idEmple` (`idEmple`) USING BTREE,
  CONSTRAINT `horas_ibfk_1` FOREIGN KEY (`idEmple`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=24162 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `imagenes_inventario`
--

DROP TABLE IF EXISTS `imagenes_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `imagenes_inventario` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `inventario_id` int(11) NOT NULL DEFAULT 0,
  `imagen` varchar(250) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `FK_imagen_inventario` (`inventario_id`),
  CONSTRAINT `FK_imagen_inventario` FOREIGN KEY (`inventario_id`) REFERENCES `inventario` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ingegdep`
--

DROP TABLE IF EXISTS `ingegdep`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ingegdep` (
  `idIngEgDep` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idArticulo` int(10) unsigned NOT NULL,
  `Cantidad` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Saldo` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Personal` varchar(50) NOT NULL DEFAULT '',
  `Tipo` char(1) NOT NULL DEFAULT '',
  `Estado` char(1) NOT NULL DEFAULT '',
  `idMovil` varchar(17) NOT NULL DEFAULT '',
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  PRIMARY KEY (`idIngEgDep`),
  KEY `idArticulo` (`idArticulo`),
  KEY `UnidadNegocio` (`UnidadNegocio`),
  CONSTRAINT `ingegdep_ibfk_1` FOREIGN KEY (`idArticulo`) REFERENCES `articulos` (`idArticulo`) ON UPDATE CASCADE,
  CONSTRAINT `ingegdep_ibfk_2` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2132 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inventario`
--

DROP TABLE IF EXISTS `inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventario` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `detalle` varchar(255) NOT NULL DEFAULT '',
  `marca` int(11) NOT NULL,
  `tipo` int(11) NOT NULL,
  `area` int(11) NOT NULL,
  `responsable` int(10) unsigned NOT NULL,
  `codigo_tango` varchar(50) DEFAULT '',
  `observaciones` text DEFAULT NULL,
  `activo` tinyint(4) NOT NULL DEFAULT 0,
  `fecha_alta` date NOT NULL,
  `fecha_baja` date NOT NULL,
  `ubicacion` varchar(255) NOT NULL DEFAULT '',
  `antivirus` varchar(50) DEFAULT NULL,
  `sistema_operativo` varchar(50) DEFAULT NULL,
  `nombre_computador` varchar(50) DEFAULT NULL,
  `direccion_ip` varchar(20) DEFAULT NULL,
  `usuario` varchar(50) DEFAULT NULL,
  `password` varchar(50) DEFAULT NULL,
  `equipo_asociado` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_inventario_marca` (`marca`),
  KEY `FK_inventario_tipo` (`tipo`),
  KEY `FK_inventario_area` (`area`),
  KEY `FK_inventario_personal` (`responsable`),
  CONSTRAINT `FK_inventario_area` FOREIGN KEY (`area`) REFERENCES `areas` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `FK_inventario_marca` FOREIGN KEY (`marca`) REFERENCES `marca_inventario` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `FK_inventario_personal` FOREIGN KEY (`responsable`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE,
  CONSTRAINT `FK_inventario_tipo` FOREIGN KEY (`tipo`) REFERENCES `tipo_inventario` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lavados`
--

DROP TABLE IF EXISTS `lavados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lavados` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL DEFAULT '0000-00-00',
  `movil` int(10) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `FK_Lavados_Movil` (`movil`),
  CONSTRAINT `FK_Lavados_Movil` FOREIGN KEY (`movil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lugarcarga`
--

DROP TABLE IF EXISTS `lugarcarga`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lugarcarga` (
  `idLugarCarga` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Detalle` varchar(80) NOT NULL DEFAULT '',
  `activo` tinyint(4) NOT NULL DEFAULT 1,
  `unidad_negocio` int(10) unsigned NOT NULL DEFAULT 1,
  PRIMARY KEY (`idLugarCarga`),
  KEY `FK_Lugar_UN` (`unidad_negocio`),
  CONSTRAINT `FK_Lugar_UN` FOREIGN KEY (`unidad_negocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `marca_inventario`
--

DROP TABLE IF EXISTS `marca_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `marca_inventario` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `detalle` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `marcaneu`
--

DROP TABLE IF EXISTS `marcaneu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `marcaneu` (
  `idMarcaNeu` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(30) NOT NULL DEFAULT '',
  PRIMARY KEY (`idMarcaNeu`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `matafuegos`
--

DROP TABLE IF EXISTS `matafuegos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `matafuegos` (
  `idMatafuego` int(10) unsigned NOT NULL DEFAULT 0,
  `EstadoManometro` int(10) unsigned NOT NULL DEFAULT 1,
  `SegPasador` bit(1) NOT NULL DEFAULT b'0',
  `PoseeAnillo` bit(1) NOT NULL DEFAULT b'0',
  `Manguera` bit(1) NOT NULL DEFAULT b'0',
  `FacilExtraer` bit(1) NOT NULL DEFAULT b'0',
  `Vencimiento` date NOT NULL DEFAULT '0000-00-00',
  `Ubicacion` varchar(30) NOT NULL DEFAULT '',
  `Movil` int(10) unsigned NOT NULL DEFAULT 0,
  `Capacidad` varchar(8) NOT NULL DEFAULT '',
  `Reserva` bit(1) NOT NULL DEFAULT b'0',
  `ultcontrol` date NOT NULL DEFAULT '0000-00-00',
  `baja` bit(1) NOT NULL DEFAULT b'0',
  `fechabaja` date NOT NULL DEFAULT '0000-00-00',
  `motivobaja` varchar(200) NOT NULL DEFAULT '',
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  PRIMARY KEY (`idMatafuego`),
  KEY `EstadoManometro` (`EstadoManometro`),
  KEY `Movil` (`Movil`),
  KEY `UnidadNegocio` (`UnidadNegocio`),
  CONSTRAINT `FG_Matafuegos_Movil` FOREIGN KEY (`Movil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `matafuegos_ibfk_1` FOREIGN KEY (`EstadoManometro`) REFERENCES `estadoman` (`idEstadoMan`) ON UPDATE CASCADE,
  CONSTRAINT `matafuegos_ibfk_3` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `menu`
--

DROP TABLE IF EXISTS `menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `menu` (
  `Id_menu` int(11) NOT NULL DEFAULT 0,
  `Nombre` varchar(100) DEFAULT NULL,
  `logo` varchar(100) DEFAULT NULL,
  `parent_id` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`Id_menu`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `menu_lateral`
--

DROP TABLE IF EXISTS `menu_lateral`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `menu_lateral` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `for_id` int(11) NOT NULL,
  `for_pare` int(11) NOT NULL,
  `activo` bit(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `menulateral_for_id` (`for_id`),
  CONSTRAINT `menu_lateral_ibfk_1` FOREIGN KEY (`for_id`) REFERENCES `formula` (`for_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `modificaciones`
--

DROP TABLE IF EXISTS `modificaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `modificaciones` (
  `idModificacion` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Maquina` varchar(20) NOT NULL DEFAULT '',
  `tabla` varchar(20) NOT NULL DEFAULT '',
  `datos` text DEFAULT NULL,
  `db` varchar(30) NOT NULL DEFAULT 'fasa',
  `Operacion` varchar(30) NOT NULL DEFAULT '',
  `_usuario` varchar(20) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`idModificacion`)
) ENGINE=InnoDB AUTO_INCREMENT=6868 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `monedas`
--

DROP TABLE IF EXISTS `monedas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `monedas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(100) NOT NULL,
  `simbolo` varchar(10) NOT NULL,
  `cambio` decimal(10,4) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `monedas_descripcion` (`descripcion`),
  UNIQUE KEY `monedas_simbolo` (`simbolo`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `movarticulo`
--

DROP TABLE IF EXISTS `movarticulo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `movarticulo` (
  `idMovArticulo` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idArticulo` int(10) unsigned NOT NULL,
  `Fecha` date NOT NULL DEFAULT '0000-00-00',
  `idTipoComp` int(10) unsigned NOT NULL,
  `Numero` char(12) NOT NULL DEFAULT '',
  `Ingresa` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Egresa` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Movil` char(17) NOT NULL DEFAULT '',
  `Detalle` text DEFAULT NULL,
  `idProveedor` int(10) unsigned NOT NULL DEFAULT 1,
  `CargadoHolistor` bit(1) NOT NULL DEFAULT b'0',
  `Unitario` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `idPaniol` int(10) unsigned NOT NULL DEFAULT 1,
  `idReferencia` int(10) unsigned NOT NULL DEFAULT 0,
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  `_usuario` varchar(20) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  `Cotizacion` decimal(12,4) NOT NULL DEFAULT 0.0000,
  PRIMARY KEY (`idMovArticulo`),
  KEY `idTipoComp` (`idTipoComp`),
  KEY `idArticulo` (`idArticulo`),
  KEY `idProveedor` (`idProveedor`),
  KEY `UnidadNegocio` (`UnidadNegocio`),
  CONSTRAINT `movarticulo_ibfk_1` FOREIGN KEY (`idTipoComp`) REFERENCES `tipcomp` (`Codigo`) ON UPDATE CASCADE,
  CONSTRAINT `movarticulo_ibfk_2` FOREIGN KEY (`idArticulo`) REFERENCES `articulos` (`idArticulo`) ON UPDATE CASCADE,
  CONSTRAINT `movarticulo_ibfk_3` FOREIGN KEY (`idProveedor`) REFERENCES `proveedores` (`idProveedor`) ON UPDATE CASCADE,
  CONSTRAINT `movarticulo_ibfk_4` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=75594 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `movilbase`
--

DROP TABLE IF EXISTS `movilbase`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `movilbase` (
  `movilbase` varchar(17) NOT NULL DEFAULT '',
  `movilrelacionado` varchar(17) NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `moviles`
--

DROP TABLE IF EXISTS `moviles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `moviles` (
  `idMovil` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Patente` varchar(14) NOT NULL DEFAULT '',
  `Detalle` varchar(200) NOT NULL DEFAULT '',
  `idChofer` int(10) unsigned NOT NULL DEFAULT 1,
  `ult_hr_km` int(10) unsigned NOT NULL DEFAULT 0,
  `UltFecha` date DEFAULT NULL,
  `idUnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  `tipo_proceso` char(1) NOT NULL DEFAULT '1',
  `CantNeumaticos` int(10) unsigned NOT NULL DEFAULT 0,
  `CantRepuesto` int(10) unsigned NOT NULL DEFAULT 0,
  `Baja` tinyint(1) NOT NULL DEFAULT 0,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  `FechaBaja` date DEFAULT NULL,
  `fecha_alta` date DEFAULT NULL,
  `MotivoBaja` varchar(100) NOT NULL DEFAULT '',
  `Remolque` char(17) NOT NULL DEFAULT '',
  `Porcentaje` decimal(6,2) NOT NULL DEFAULT 0.00,
  `VencTecnica` date DEFAULT NULL,
  `Ruta` bit(1) NOT NULL DEFAULT b'0',
  `VencRuta` date DEFAULT NULL,
  `nvocodigo` varchar(17) NOT NULL DEFAULT '',
  `nro_chasis` varchar(80) NOT NULL,
  `nro_motor` varchar(80) NOT NULL,
  `anio_fabricacion` int(11) NOT NULL,
  `centro_costo` int(11) NOT NULL,
  `codigo_kobo` varchar(50) NOT NULL DEFAULT '',
  `codigo_bertotto` int(11) NOT NULL DEFAULT 0,
  `capacidad_tanque` int(11) NOT NULL DEFAULT 0,
  `consumo_promedio` float NOT NULL DEFAULT 0,
  `forma_actualizacion` char(1) NOT NULL DEFAULT '',
  `tipo_movil` int(11) NOT NULL DEFAULT 1,
  `estadistica` tinyint(1) NOT NULL DEFAULT 1,
  `codigo_gestya` varchar(150) NOT NULL DEFAULT '',
  `movil_asociado` int(11) NOT NULL,
  `observaciones` text DEFAULT NULL,
  PRIMARY KEY (`idMovil`),
  KEY `idChofer` (`idChofer`),
  KEY `idUnidadNegocio` (`idUnidadNegocio`),
  KEY `FK_tipo_movil` (`tipo_movil`),
  CONSTRAINT `FK_tipo_movil` FOREIGN KEY (`tipo_movil`) REFERENCES `tipodemovil` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1673 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `moviles_operadores`
--

DROP TABLE IF EXISTS `moviles_operadores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `moviles_operadores` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `operador_id` int(10) unsigned NOT NULL DEFAULT 0,
  `movil_id` char(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT '0',
  `desde` date NOT NULL DEFAULT '0000-00-00',
  `hasta` date NOT NULL DEFAULT '0000-00-00',
  PRIMARY KEY (`id`),
  KEY `FK_movil` (`movil_id`),
  KEY `FK_operador` (`operador_id`),
  CONSTRAINT `FK_operador` FOREIGN KEY (`operador_id`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `movilxunnegocio`
--

DROP TABLE IF EXISTS `movilxunnegocio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `movilxunnegocio` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idMovil` int(10) unsigned NOT NULL DEFAULT 1,
  `idUnidadNegocio` int(10) unsigned NOT NULL DEFAULT 0,
  `DesdeFecha` date NOT NULL DEFAULT '0000-00-00',
  `HastaFecha` date NOT NULL DEFAULT '0000-00-00',
  `_usuario` varchar(50) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` varchar(8) NOT NULL DEFAULT '00:00:00',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `movneu`
--

DROP TABLE IF EXISTS `movneu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `movneu` (
  `idMovNeu` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `NFuego` int(10) unsigned NOT NULL DEFAULT 1,
  `Fecha` date NOT NULL DEFAULT '0000-00-00',
  `Movil` int(10) unsigned NOT NULL DEFAULT 1,
  `Proveedor` varchar(30) NOT NULL DEFAULT '1',
  `Descripcion` text DEFAULT NULL,
  `Monto` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Status` int(10) unsigned NOT NULL DEFAULT 1,
  `kmhora` int(10) unsigned NOT NULL DEFAULT 0,
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  `Clase` char(3) NOT NULL DEFAULT '',
  `Factura` varchar(12) NOT NULL DEFAULT '',
  `pto_vta` varchar(5) NOT NULL DEFAULT '',
  `numero` varchar(8) NOT NULL DEFAULT '',
  `MontoCDesc` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `idpersonal` int(10) unsigned NOT NULL DEFAULT 1,
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  `fecha_grabacion` datetime NOT NULL,
  PRIMARY KEY (`idMovNeu`),
  KEY `NFuego` (`NFuego`),
  KEY `UnidadNegocio` (`UnidadNegocio`),
  KEY `FK_movneu_status` (`Status`),
  KEY `FK_personal` (`idpersonal`),
  KEY `FK_MovNeu_Movil` (`Movil`),
  CONSTRAINT `FK_MovNeu_Movil` FOREIGN KEY (`Movil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `FK_movneu_status` FOREIGN KEY (`Status`) REFERENCES `statusneu` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `FK_movneu_un` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE,
  CONSTRAINT `FK_personal` FOREIGN KEY (`idpersonal`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE,
  CONSTRAINT `movneu_ibfk_1` FOREIGN KEY (`NFuego`) REFERENCES `neumaticos` (`nFuego`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11622 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `movpaniol`
--

DROP TABLE IF EXISTS `movpaniol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `movpaniol` (
  `idMovPaniol` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idPaniol` int(10) unsigned NOT NULL,
  `TipoMov` char(1) NOT NULL DEFAULT '',
  `idArticulo` int(10) unsigned NOT NULL,
  `fecha` date NOT NULL DEFAULT '0000-00-00',
  `Cantidad` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Saldo` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `idTipoComp` int(10) unsigned NOT NULL,
  `Comprobante` char(12) NOT NULL DEFAULT '',
  `Movil` int(10) unsigned NOT NULL DEFAULT 0,
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  PRIMARY KEY (`idMovPaniol`),
  KEY `idPaniol` (`idPaniol`),
  KEY `idArticulo` (`idArticulo`),
  KEY `idTipoComp` (`idTipoComp`),
  KEY `Movil` (`Movil`),
  CONSTRAINT `FG_MovPaniol_Movil` FOREIGN KEY (`Movil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `movpaniol_ibfk_1` FOREIGN KEY (`idPaniol`) REFERENCES `panioles` (`idPaniol`) ON UPDATE CASCADE,
  CONSTRAINT `movpaniol_ibfk_2` FOREIGN KEY (`idArticulo`) REFERENCES `articulos` (`idArticulo`) ON UPDATE CASCADE,
  CONSTRAINT `movpaniol_ibfk_3` FOREIGN KEY (`idTipoComp`) REFERENCES `tipcomp` (`Codigo`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=33574 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `neumaticos`
--

DROP TABLE IF EXISTS `neumaticos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `neumaticos` (
  `nFuego` int(10) unsigned NOT NULL,
  `NSerie` varchar(20) NOT NULL DEFAULT '',
  `idMarca` int(10) unsigned NOT NULL,
  `idTipoNeu` int(10) unsigned NOT NULL,
  `ValorCompra` decimal(12,2) NOT NULL DEFAULT 0.00,
  `MovilAsignado` int(10) unsigned NOT NULL DEFAULT 477,
  `pto_vta` char(5) NOT NULL DEFAULT '',
  `numero` char(8) NOT NULL DEFAULT '',
  `Ubicacion` int(10) unsigned NOT NULL DEFAULT 1,
  `Orden` int(10) unsigned NOT NULL DEFAULT 0,
  `EnProveedor` tinyint(1) NOT NULL DEFAULT 0,
  `Status` int(11) NOT NULL DEFAULT 6,
  `FechaBaja` date DEFAULT NULL,
  `MotivoBaja` varchar(200) NOT NULL DEFAULT '',
  `idProveedor` int(10) unsigned NOT NULL DEFAULT 1,
  `FacturaCompra` varchar(12) NOT NULL DEFAULT '',
  `_usuario` varchar(20) NOT NULL DEFAULT '',
  `_fecha` date DEFAULT NULL,
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  `proveedor` varchar(30) NOT NULL DEFAULT '',
  PRIMARY KEY (`nFuego`),
  KEY `idTipoNeu` (`idTipoNeu`),
  KEY `idMarca` (`idMarca`),
  KEY `MovilAsignado` (`MovilAsignado`),
  KEY `idProveedor` (`idProveedor`),
  CONSTRAINT `FG_neumatico_movil` FOREIGN KEY (`MovilAsignado`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `neumaticos_ibfk_1` FOREIGN KEY (`idTipoNeu`) REFERENCES `tiponeu` (`idTipoNeu`) ON UPDATE CASCADE,
  CONSTRAINT `neumaticos_ibfk_2` FOREIGN KEY (`idMarca`) REFERENCES `marcaneu` (`idMarcaNeu`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notificaciones`
--

DROP TABLE IF EXISTS `notificaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notificaciones` (
  `idNotificacion` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idPersonal` int(10) unsigned DEFAULT NULL,
  `titulo` varchar(150) NOT NULL DEFAULT '',
  `mensaje` text NOT NULL,
  `leido` tinyint(4) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`idNotificacion`) USING BTREE,
  KEY `FK_Notif_Personal` (`idPersonal`) USING BTREE,
  CONSTRAINT `FK_Notif_Personal` FOREIGN KEY (`idPersonal`) REFERENCES `personal` (`idPersonal`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `origen`
--

DROP TABLE IF EXISTS `origen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `origen` (
  `idOrigen` int(10) unsigned NOT NULL,
  `ORIGEN` varchar(40) NOT NULL DEFAULT '',
  `DESTINO` varchar(40) NOT NULL DEFAULT '',
  `KMS` int(11) NOT NULL DEFAULT 0,
  `PRECIO` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `KMTIERRA` decimal(12,2) NOT NULL DEFAULT 0.00,
  `KMASFALTO` decimal(12,2) NOT NULL DEFAULT 0.00,
  `PRECOSECHA` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `CodigoDestino` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`idOrigen`),
  UNIQUE KEY `idOrigen` (`idOrigen`,`CodigoDestino`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `origen_destino`
--

DROP TABLE IF EXISTS `origen_destino`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `origen_destino` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cliente_id` int(11) NOT NULL,
  `desde` varchar(80) NOT NULL,
  `hasta` varchar(80) NOT NULL,
  `tipo_tarifa` varchar(1) NOT NULL,
  `tarifa` float NOT NULL,
  `tarifa_empresa` float NOT NULL,
  `vigencia` date NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `comisionista` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `origendestino_cliente_id` (`cliente_id`),
  CONSTRAINT `origen_destino_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `cliente` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `panioles`
--

DROP TABLE IF EXISTS `panioles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `panioles` (
  `idPaniol` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(80) NOT NULL DEFAULT '',
  `un` int(10) unsigned NOT NULL DEFAULT 1,
  PRIMARY KEY (`idPaniol`),
  KEY `FG_panioles_un` (`un`),
  CONSTRAINT `FG_panioles_un` FOREIGN KEY (`un`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `paramsist`
--

DROP TABLE IF EXISTS `paramsist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `paramsist` (
  `idParamSist` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Parametro` varchar(100) NOT NULL DEFAULT '',
  `Valor` text NOT NULL,
  PRIMARY KEY (`idParamSist`)
) ENGINE=InnoDB AUTO_INCREMENT=90 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `patrimonio`
--

DROP TABLE IF EXISTS `patrimonio`;
/*!50001 DROP VIEW IF EXISTS `patrimonio`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `patrimonio` AS SELECT
 1 AS `anio`,
  1 AS `mes`,
  1 AS `fecha`,
  1 AS `equipo`,
  1 AS `operacion`,
  1 AS `hr_dia`,
  1 AS `produccion`,
  1 AS `predio`,
  1 AS `unidad_produccion` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `personal`
--

DROP TABLE IF EXISTS `personal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `personal` (
  `idPersonal` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(80) NOT NULL DEFAULT '',
  `CUIT` varchar(13) NOT NULL DEFAULT '',
  `FechaAlta` date DEFAULT NULL,
  `FechaBaja` date DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `fecha_ingreso` date DEFAULT NULL,
  `idPuesto` int(10) unsigned NOT NULL DEFAULT 1,
  `EntradaM` varchar(5) NOT NULL DEFAULT '00:00',
  `SalidaM` varchar(5) NOT NULL DEFAULT '00:00',
  `EntradaT` varchar(5) NOT NULL DEFAULT '00:00',
  `SalidaT` varchar(5) NOT NULL DEFAULT '00:00',
  `CodigoArauco` varchar(10) NOT NULL DEFAULT '',
  `CodigoRoble` int(10) unsigned NOT NULL DEFAULT 0,
  `ult_liq` varchar(6) NOT NULL DEFAULT '',
  `unidad_negocio` int(10) unsigned NOT NULL DEFAULT 1,
  `expediente` tinyint(1) NOT NULL DEFAULT 0,
  `telefono` varchar(50) NOT NULL DEFAULT '',
  `domicilio` varchar(50) NOT NULL DEFAULT '',
  `concepto_sueldo` int(11) NOT NULL DEFAULT 0,
  `codigo_kobo` varchar(50) NOT NULL DEFAULT '',
  `porcentaje` float NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `dni` varchar(8) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`idPersonal`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `idPuesto` (`idPuesto`),
  KEY `unidad_negocio` (`unidad_negocio`),
  KEY `FK_concepto` (`concepto_sueldo`),
  CONSTRAINT `FK_concepto` FOREIGN KEY (`concepto_sueldo`) REFERENCES `conceptoliquidacion` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `personal_ibfk_1` FOREIGN KEY (`idPuesto`) REFERENCES `puestos` (`CODIGO`) ON UPDATE CASCADE,
  CONSTRAINT `personal_ibfk_2` FOREIGN KEY (`unidad_negocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE,
  CONSTRAINT `personal_user_id_308d5101_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=77599 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary table structure for view `personal_activo`
--

DROP TABLE IF EXISTS `personal_activo`;
/*!50001 DROP VIEW IF EXISTS `personal_activo`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `personal_activo` AS SELECT
 1 AS `idPersonal`,
  1 AS `Nombre` */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `planificacion`
--

DROP TABLE IF EXISTS `planificacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `planificacion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(150) NOT NULL,
  `cada_cuanto` float NOT NULL,
  `anticipacion` float NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `planificacionequipos`
--

DROP TABLE IF EXISTS `planificacionequipos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `planificacionequipos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `planificacion_id` int(11) NOT NULL,
  `usuario` varchar(30) NOT NULL,
  `creado` datetime NOT NULL,
  `equipo_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `planificacionequipos_planificacion_id` (`planificacion_id`),
  KEY `planificacionequipos_ibfk_2` (`equipo_id`),
  CONSTRAINT `planificacionequipos_ibfk_1` FOREIGN KEY (`planificacion_id`) REFERENCES `planificacion` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `planificacionequipos_ibfk_2` FOREIGN KEY (`equipo_id`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `planificaciontareas`
--

DROP TABLE IF EXISTS `planificaciontareas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `planificaciontareas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `planificacion_id` int(11) NOT NULL,
  `tipo_tarea_id` int(11) NOT NULL,
  `usuario` varchar(30) NOT NULL,
  `creado` datetime NOT NULL,
  `cada_cuanto` int(11) NOT NULL,
  `antelacion` int(11) NOT NULL,
  `forma_actualizacion` varchar(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `planificaciontareas_planificacion_id` (`planificacion_id`),
  KEY `planificaciontareas_tipo_tarea_id` (`tipo_tarea_id`),
  CONSTRAINT `planificaciontareas_ibfk_1` FOREIGN KEY (`planificacion_id`) REFERENCES `planificacion` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `planificaciontareas_ibfk_2` FOREIGN KEY (`tipo_tarea_id`) REFERENCES `tipostareas` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `planmant`
--

DROP TABLE IF EXISTS `planmant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `planmant` (
  `idPlanMant` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Accion` varchar(80) NOT NULL DEFAULT '',
  `idArticulo` int(10) unsigned NOT NULL DEFAULT 1,
  PRIMARY KEY (`idPlanMant`),
  KEY `idArticulo` (`idArticulo`),
  CONSTRAINT `planmant_ibfk_1` FOREIGN KEY (`idArticulo`) REFERENCES `articulos` (`idArticulo`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=575 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `planxmovil`
--

DROP TABLE IF EXISTS `planxmovil`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `planxmovil` (
  `idPlanXMovil` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idMovil` int(10) unsigned NOT NULL DEFAULT 0,
  `idPlanMant` int(10) unsigned NOT NULL DEFAULT 0,
  `Detalle` varchar(80) NOT NULL DEFAULT '',
  `Duracion` int(10) unsigned NOT NULL DEFAULT 0,
  `Antelacion` int(10) unsigned NOT NULL DEFAULT 0,
  `idArticulo` int(10) unsigned NOT NULL DEFAULT 1,
  `Insumo` varchar(80) NOT NULL DEFAULT '',
  `UltFecha` date NOT NULL DEFAULT '0000-00-00',
  `UltKMHora` int(11) NOT NULL DEFAULT 0,
  `Cantidad` decimal(12,2) unsigned NOT NULL DEFAULT 0.00,
  `ControlaHora` bit(1) NOT NULL DEFAULT b'1',
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  PRIMARY KEY (`idPlanXMovil`),
  KEY `idPlanMant` (`idPlanMant`),
  KEY `idMovil` (`idMovil`),
  KEY `idArticulo` (`idArticulo`),
  KEY `UnidadNegocio` (`UnidadNegocio`),
  CONSTRAINT `FK_Plan_Movil` FOREIGN KEY (`idMovil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `planxmovil_ibfk_2` FOREIGN KEY (`idPlanMant`) REFERENCES `planmant` (`idPlanMant`) ON UPDATE CASCADE,
  CONSTRAINT `planxmovil_ibfk_4` FOREIGN KEY (`idArticulo`) REFERENCES `articulos` (`idArticulo`) ON UPDATE CASCADE,
  CONSTRAINT `planxmovil_ibfk_5` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4385 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `precintos`
--

DROP TABLE IF EXISTS `precintos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `precintos` (
  `idPrecinto` int(10) unsigned NOT NULL,
  `MovilAsignado` int(10) unsigned NOT NULL DEFAULT 0,
  `FechaAsignacion` date NOT NULL DEFAULT '0000-00-00',
  `FechaBaja` date NOT NULL DEFAULT '0000-00-00',
  `MotivoBaja` varchar(200) NOT NULL DEFAULT '',
  `fecha` date NOT NULL DEFAULT '0000-00-00',
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  PRIMARY KEY (`idPrecinto`),
  KEY `UnidadNegocio` (`UnidadNegocio`),
  KEY `MovilAsignado` (`MovilAsignado`),
  CONSTRAINT `FK_Precinto_Movil` FOREIGN KEY (`MovilAsignado`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `precintos_ibfk_1` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `precio_combustible`
--

DROP TABLE IF EXISTS `precio_combustible`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `precio_combustible` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tipo_combustible` int(10) unsigned NOT NULL DEFAULT 0,
  `desde` date NOT NULL,
  `hasta` date NOT NULL,
  `precio` float NOT NULL DEFAULT 0,
  `usuario` varchar(30) NOT NULL DEFAULT '0',
  `fecha` date NOT NULL,
  `hora` char(8) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `FK_precio_tipoo` (`tipo_combustible`),
  CONSTRAINT `FK_precio_tipoo` FOREIGN KEY (`tipo_combustible`) REFERENCES `tipocomb` (`idTipoComb`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `predios`
--

DROP TABLE IF EXISTS `predios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `predios` (
  `idPredio` int(10) unsigned NOT NULL,
  `Nombre` varchar(100) NOT NULL DEFAULT '',
  `Carga` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `empresa` varchar(30) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` date DEFAULT NULL,
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  `km_asfalto` int(11) DEFAULT NULL,
  `km_tierra` int(11) DEFAULT NULL,
  `codigo_kobo` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`idPredio`),
  KEY `FK_predio_empresa` (`empresa`),
  CONSTRAINT `FK_predio_empresa` FOREIGN KEY (`empresa`) REFERENCES `cliente` (`cuit`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prerem`
--

DROP TABLE IF EXISTS `prerem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prerem` (
  `idPreRem` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `IdRemComb` int(10) unsigned NOT NULL DEFAULT 0,
  `idPrecinto` int(10) unsigned NOT NULL DEFAULT 0,
  `Fecha` date NOT NULL DEFAULT '0000-00-00',
  `_usuario` varchar(255) NOT NULL DEFAULT '',
  `_fecha` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`idPreRem`)
) ENGINE=InnoDB AUTO_INCREMENT=141 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci COMMENT='Tabla donde guardo la relacion entre los precintos y los remitos';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prodatransp`
--

DROP TABLE IF EXISTS `prodatransp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `prodatransp` (
  `ProdATransp` char(1) NOT NULL DEFAULT '',
  `Detalle` varchar(50) NOT NULL DEFAULT '',
  `PromCarga` int(10) unsigned NOT NULL DEFAULT 0,
  `PromDescarga` int(10) unsigned NOT NULL DEFAULT 0,
  `DetalleArauco` varchar(100) NOT NULL DEFAULT '',
  KEY `ProdATransp` (`ProdATransp`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci COMMENT='Tabla de productos a transportar, se utilizan en los remitos forestales';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `produccion`
--

DROP TABLE IF EXISTS `produccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `produccion` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `cliente_id` varchar(30) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL DEFAULT '',
  `predio_id` int(10) unsigned NOT NULL DEFAULT 0,
  `rodal_id` int(10) unsigned NOT NULL,
  `equipo_id` varchar(50) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `operador_id` int(10) unsigned NOT NULL,
  `un_id` int(10) unsigned NOT NULL DEFAULT 1,
  `fecha` date NOT NULL,
  `turno` char(1) NOT NULL DEFAULT '',
  `hora_inicio_maquina` int(10) unsigned NOT NULL DEFAULT 0,
  `hora_fin_maquina` int(10) unsigned NOT NULL DEFAULT 0,
  `horas_no_operativas` int(10) unsigned NOT NULL DEFAULT 0,
  `motivo_no_operativo` text NOT NULL,
  `acta` varchar(20) NOT NULL DEFAULT '',
  `litros_gasoil` int(11) NOT NULL DEFAULT 0,
  `produccion` int(11) NOT NULL DEFAULT 0,
  `observaciones` text NOT NULL,
  `plantas` int(10) unsigned NOT NULL DEFAULT 0,
  `tipo_proceso` char(1) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `tarifa` decimal(14,4) NOT NULL DEFAULT 0.0000,
  `mts` int(10) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `FK_produccion_cliente` (`cliente_id`) USING BTREE,
  KEY `FK_produccion_predio` (`predio_id`) USING BTREE,
  KEY `FK_produccion_rodal` (`rodal_id`) USING BTREE,
  KEY `FK_produccion_equipo` (`equipo_id`) USING BTREE,
  KEY `FK_produccion_personal` (`operador_id`),
  KEY `FK_produccion_un` (`un_id`),
  CONSTRAINT `FK_produccion_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `cliente` (`cuit`) ON UPDATE CASCADE,
  CONSTRAINT `FK_produccion_equipo` FOREIGN KEY (`equipo_id`) REFERENCES `equipo` (`patente`) ON UPDATE CASCADE,
  CONSTRAINT `FK_produccion_personal` FOREIGN KEY (`operador_id`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE,
  CONSTRAINT `FK_produccion_predio` FOREIGN KEY (`predio_id`) REFERENCES `predios` (`idPredio`) ON UPDATE CASCADE,
  CONSTRAINT `FK_produccion_rodal` FOREIGN KEY (`rodal_id`) REFERENCES `rodales` (`idRodal`) ON UPDATE CASCADE,
  CONSTRAINT `FK_produccion_un` FOREIGN KEY (`un_id`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=461 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `produccion_mensual`
--

DROP TABLE IF EXISTS `produccion_mensual`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `produccion_mensual` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `periodo` char(6) NOT NULL DEFAULT '0',
  `un` int(10) unsigned NOT NULL DEFAULT 0,
  `tipo_operacion` varchar(50) DEFAULT NULL,
  `produccion` decimal(12,2) NOT NULL DEFAULT 0.00,
  `cantidad_equipo` decimal(12,2) NOT NULL DEFAULT 0.00,
  `unidad_produccion` varchar(50) DEFAULT NULL,
  `tarifa` decimal(16,4) DEFAULT NULL,
  `equipo_id` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_unidad_negocio` (`un`),
  KEY `fk_equipo_produccion_mensual` (`equipo_id`),
  CONSTRAINT `FK_unidad_negocio` FOREIGN KEY (`un`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE,
  CONSTRAINT `fk_equipo_produccion_mensual` FOREIGN KEY (`equipo_id`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `proveedores` (
  `idProveedor` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `RazonSocial` varchar(80) NOT NULL DEFAULT '',
  `CUIT` char(13) NOT NULL DEFAULT '',
  `Domicilio` varchar(80) NOT NULL DEFAULT '',
  `telefono` varchar(100) NOT NULL DEFAULT '',
  `contacto` varchar(100) NOT NULL DEFAULT '',
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  `EMail` varchar(200) NOT NULL DEFAULT '',
  `observaciones` text NOT NULL,
  `_usuario` varchar(20) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  PRIMARY KEY (`idProveedor`)
) ENGINE=InnoDB AUTO_INCREMENT=178 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `puestos`
--

DROP TABLE IF EXISTS `puestos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `puestos` (
  `CODIGO` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `NOMBRE` varchar(40) NOT NULL,
  PRIMARY KEY (`CODIGO`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `push_subscriptions`
--

DROP TABLE IF EXISTS `push_subscriptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `push_subscriptions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `endpoint` text NOT NULL,
  `keys_p256dh` varchar(255) DEFAULT NULL,
  `keys_auth` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_push_endpoint` (`endpoint`(255)),
  KEY `idx_push_user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `remcobi`
--

DROP TABLE IF EXISTS `remcobi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `remcobi` (
  `idRemCoBi` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `idMovil` int(10) unsigned NOT NULL DEFAULT 0,
  `Periodo` char(6) NOT NULL DEFAULT '',
  `Dia` int(10) unsigned NOT NULL DEFAULT 0,
  `Numero` char(8) NOT NULL DEFAULT '',
  `idRodal` int(10) unsigned NOT NULL,
  `Precio` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `TN` double(12,2) NOT NULL DEFAULT 0.00,
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  PRIMARY KEY (`idRemCoBi`),
  KEY `idMovil` (`idMovil`),
  KEY `idRodal` (`idRodal`),
  KEY `UnidadNegocio` (`UnidadNegocio`),
  CONSTRAINT `FK_RemCoBI_Movil` FOREIGN KEY (`idMovil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `remcobi_ibfk_2` FOREIGN KEY (`idRodal`) REFERENCES `rodales` (`idRodal`) ON UPDATE CASCADE,
  CONSTRAINT `remcobi_ibfk_3` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=758 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `remcomb`
--

DROP TABLE IF EXISTS `remcomb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `remcomb` (
  `idRemComb` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Tipo` char(1) NOT NULL DEFAULT '',
  `frente` int(10) unsigned NOT NULL DEFAULT 0,
  `remito` varchar(12) NOT NULL DEFAULT '',
  `movil` int(10) unsigned NOT NULL DEFAULT 0,
  `fecha` date NOT NULL DEFAULT '0000-00-00',
  `proveedor` int(10) unsigned NOT NULL DEFAULT 1,
  `Ingreso` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Egreso` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `factura` varchar(12) NOT NULL DEFAULT '',
  `Chofer` int(10) unsigned NOT NULL DEFAULT 0,
  `Conductor` varchar(30) NOT NULL DEFAULT '',
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`idRemComb`),
  KEY `movil` (`movil`),
  KEY `proveedor` (`proveedor`),
  KEY `frente` (`frente`),
  KEY `Chofer` (`Chofer`),
  KEY `UnidadNegocio` (`UnidadNegocio`),
  CONSTRAINT `FK_RemComb_Moviles` FOREIGN KEY (`movil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `remcomb_ibfk_2` FOREIGN KEY (`proveedor`) REFERENCES `proveedores` (`idProveedor`) ON UPDATE CASCADE,
  CONSTRAINT `remcomb_ibfk_3` FOREIGN KEY (`frente`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE,
  CONSTRAINT `remcomb_ibfk_4` FOREIGN KEY (`Chofer`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE,
  CONSTRAINT `remcomb_ibfk_5` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `remforestal`
--

DROP TABLE IF EXISTS `remforestal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `remforestal` (
  `idRemForestal` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Periodo` char(6) NOT NULL DEFAULT '',
  `Dia` int(10) unsigned NOT NULL DEFAULT 0,
  `ptovta` char(4) NOT NULL DEFAULT '',
  `numero` char(8) NOT NULL DEFAULT '',
  `Origen` int(10) unsigned NOT NULL DEFAULT 0,
  `Km` int(10) unsigned NOT NULL DEFAULT 0,
  `LlegaMonte` char(5) NOT NULL DEFAULT '00:00',
  `SaleMonte` char(5) NOT NULL DEFAULT '00:00',
  `Movil` int(10) unsigned NOT NULL DEFAULT 0,
  `Chofer` int(10) unsigned NOT NULL DEFAULT 0,
  `LlegaPlanta` char(5) NOT NULL DEFAULT '00:00',
  `SalePlanta` char(5) NOT NULL DEFAULT '00:00',
  `TN` decimal(12,2) NOT NULL DEFAULT 0.00,
  `Tara` decimal(12,2) NOT NULL DEFAULT 0.00,
  `PrecioUN` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Producto` char(1) NOT NULL DEFAULT '',
  `UnidadNegocio` int(10) unsigned NOT NULL DEFAULT 1,
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  `acta_id` int(10) unsigned NOT NULL DEFAULT 0,
  `cantidad` decimal(12,4) NOT NULL DEFAULT 0.0000,
  PRIMARY KEY (`idRemForestal`),
  KEY `Movil` (`Movil`),
  KEY `Chofer` (`Chofer`),
  KEY `Producto` (`Producto`),
  KEY `UnidadNegocio` (`UnidadNegocio`),
  CONSTRAINT `FK_RemForestal_Movil` FOREIGN KEY (`Movil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `remforestal_ibfk_2` FOREIGN KEY (`Chofer`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE,
  CONSTRAINT `remforestal_ibfk_3` FOREIGN KEY (`Producto`) REFERENCES `prodatransp` (`ProdATransp`) ON UPDATE CASCADE,
  CONSTRAINT `remforestal_ibfk_4` FOREIGN KEY (`UnidadNegocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17199 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `remito_carreton`
--

DROP TABLE IF EXISTS `remito_carreton`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `remito_carreton` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pto_vta` varchar(5) NOT NULL DEFAULT '0',
  `numero` varchar(8) NOT NULL DEFAULT '0',
  `chofer_id` int(10) unsigned NOT NULL DEFAULT 0,
  `movil_id` int(10) unsigned NOT NULL DEFAULT 0,
  `fecha` date NOT NULL,
  `usuario` varchar(30) NOT NULL DEFAULT '0',
  `grabacion` timestamp NULL DEFAULT NULL,
  `observacion` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_remito_chofer` (`chofer_id`),
  KEY `FK_RemCarreton_Movil` (`movil_id`),
  CONSTRAINT `FK_RemCarreton_Movil` FOREIGN KEY (`movil_id`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `FK_remito_chofer` FOREIGN KEY (`chofer_id`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=893 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `remito_forestal`
--

DROP TABLE IF EXISTS `remito_forestal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `remito_forestal` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `cliente_id` varchar(30) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL DEFAULT '0',
  `predio_id` int(10) unsigned NOT NULL DEFAULT 0,
  `rodal_id` int(10) unsigned NOT NULL DEFAULT 0,
  `equipo_id` varchar(15) CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL DEFAULT '0',
  `operador_id` int(10) unsigned NOT NULL DEFAULT 0,
  `un_id` int(10) unsigned NOT NULL,
  `fecha` date NOT NULL DEFAULT '0000-00-00',
  `ptovta` int(11) NOT NULL DEFAULT 0,
  `numero` int(11) NOT NULL DEFAULT 0,
  `elaboracion` tinyint(4) NOT NULL DEFAULT 0,
  `extraccion` tinyint(4) NOT NULL DEFAULT 0,
  `carga` tinyint(4) NOT NULL DEFAULT 0,
  `tara` decimal(12,2) NOT NULL DEFAULT 0.00,
  `total` decimal(12,2) NOT NULL DEFAULT 0.00,
  `tarifa` decimal(12,4) NOT NULL DEFAULT 0.0000,
  PRIMARY KEY (`id`),
  KEY `FK_remito_cliente` (`cliente_id`),
  KEY `FK_remito_predio` (`predio_id`),
  KEY `FK_remito_rodal` (`rodal_id`),
  KEY `FK_remito_equipo` (`equipo_id`),
  KEY `FK_remito_operador` (`operador_id`),
  KEY `FK_remito_un` (`un_id`),
  CONSTRAINT `FK_remito_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `cliente` (`cuit`) ON UPDATE CASCADE,
  CONSTRAINT `FK_remito_equipo` FOREIGN KEY (`equipo_id`) REFERENCES `equipo` (`patente`) ON UPDATE CASCADE,
  CONSTRAINT `FK_remito_operador` FOREIGN KEY (`operador_id`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE,
  CONSTRAINT `FK_remito_predio` FOREIGN KEY (`predio_id`) REFERENCES `predios` (`idPredio`) ON UPDATE CASCADE,
  CONSTRAINT `FK_remito_rodal` FOREIGN KEY (`rodal_id`) REFERENCES `rodales` (`idRodal`) ON UPDATE CASCADE,
  CONSTRAINT `FK_remito_un` FOREIGN KEY (`un_id`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `repuesto_orden_servicio`
--

DROP TABLE IF EXISTS `repuesto_orden_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `repuesto_orden_servicio` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `orden_servicio_id` int(11) NOT NULL,
  `repuesto_id` int(11) NOT NULL,
  `cantidad` float NOT NULL,
  `moneda_id` int(11) NOT NULL,
  `cambio` float NOT NULL,
  `precio_unitario` float NOT NULL,
  PRIMARY KEY (`id`),
  KEY `repuestoordenservicio_orden_servicio_id` (`orden_servicio_id`),
  KEY `repuestoordenservicio_repuesto_id` (`repuesto_id`),
  KEY `repuestoordenservicio_moneda_id` (`moneda_id`),
  CONSTRAINT `repuesto_orden_servicio_ibfk_1` FOREIGN KEY (`orden_servicio_id`) REFERENCES `det_orden_servicio` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `repuesto_orden_servicio_ibfk_2` FOREIGN KEY (`repuesto_id`) REFERENCES `repuestos` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `repuesto_orden_servicio_ibfk_3` FOREIGN KEY (`moneda_id`) REFERENCES `monedas` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `repuestos`
--

DROP TABLE IF EXISTS `repuestos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `repuestos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(150) NOT NULL,
  `stock_actual` int(11) NOT NULL,
  `stock_minimo` int(11) NOT NULL,
  `costo_unitario` float NOT NULL,
  `unidad_medida_id` int(11) NOT NULL,
  `moneda_id` int(11) NOT NULL,
  `fecha_actualizacion` date NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `maneja_stock` tinyint(1) NOT NULL,
  `usuario` varchar(30) NOT NULL,
  `codigo_interno` varchar(30) NOT NULL,
  `creado` datetime NOT NULL,
  `id_tango` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `repuestos_unidad_medida_id` (`unidad_medida_id`),
  KEY `repuestos_moneda_id` (`moneda_id`),
  CONSTRAINT `repuestos_ibfk_1` FOREIGN KEY (`unidad_medida_id`) REFERENCES `unidadmedida` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `repuestos_ibfk_2` FOREIGN KEY (`moneda_id`) REFERENCES `monedas` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7746 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `repuestosalternativos`
--

DROP TABLE IF EXISTS `repuestosalternativos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `repuestosalternativos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `repuesto_id` int(11) NOT NULL,
  `repuesto_alternativo_id` int(11) NOT NULL,
  `usuario` varchar(30) NOT NULL,
  `creado` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `repuestosalternativos_repuesto_id` (`repuesto_id`),
  KEY `repuestosalternativos_repuesto_alternativo_id` (`repuesto_alternativo_id`),
  CONSTRAINT `repuestosalternativos_ibfk_1` FOREIGN KEY (`repuesto_id`) REFERENCES `repuestos` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `repuestosalternativos_ibfk_2` FOREIGN KEY (`repuesto_alternativo_id`) REFERENCES `repuestos` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rodales`
--

DROP TABLE IF EXISTS `rodales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rodales` (
  `idRodal` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Rodal` varchar(50) NOT NULL DEFAULT '',
  `idPredio` int(10) unsigned NOT NULL,
  `VAM` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Tarifa` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Extraccion` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `Carga` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `_usuario` varchar(30) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  PRIMARY KEY (`idRodal`),
  KEY `idPredio` (`idPredio`),
  CONSTRAINT `rodales_ibfk_1` FOREIGN KEY (`idPredio`) REFERENCES `predios` (`idPredio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=175 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `roluser`
--

DROP TABLE IF EXISTS `roluser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `roluser` (
  `Userid` varchar(255) DEFAULT NULL,
  `Id_menu` varchar(255) DEFAULT NULL,
  `idroles` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rubros`
--

DROP TABLE IF EXISTS `rubros`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rubros` (
  `idRubro` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`idRubro`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `saldo_combustible`
--

DROP TABLE IF EXISTS `saldo_combustible`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `saldo_combustible` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `periodo` char(6) NOT NULL DEFAULT '0',
  `unidad_negocio` int(10) unsigned NOT NULL DEFAULT 0,
  `saldo` int(10) unsigned NOT NULL DEFAULT 0,
  `usuario` varchar(50) NOT NULL DEFAULT '0',
  `fecha_grabacion` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_saldo_comb_un` (`unidad_negocio`),
  CONSTRAINT `FK_saldo_comb_un` FOREIGN KEY (`unidad_negocio`) REFERENCES `unidadnegocio` (`idUnidadNegocio`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sectores`
--

DROP TABLE IF EXISTS `sectores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sectores` (
  `id` int(11) NOT NULL,
  `descripcion` varchar(80) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `cantidad_empleados` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sistema`
--

DROP TABLE IF EXISTS `sistema`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sistema` (
  `sis_id` smallint(6) NOT NULL AUTO_INCREMENT,
  `sis_nomb` char(30) NOT NULL,
  `sis_nresu` char(5) DEFAULT NULL,
  `pla_id` smallint(6) DEFAULT NULL,
  `sis_dire` varchar(80) DEFAULT '',
  PRIMARY KEY (`sis_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `statusneu`
--

DROP TABLE IF EXISTS `statusneu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `statusneu` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `detalle` varchar(30) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tablero_produccion`
--

DROP TABLE IF EXISTS `tablero_produccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tablero_produccion` (
  `id` int(11) NOT NULL DEFAULT 0,
  `UN` varchar(50) NOT NULL DEFAULT '',
  `operacion` varchar(50) NOT NULL DEFAULT '',
  `fecha` date DEFAULT NULL,
  `equipo` varchar(50) NOT NULL DEFAULT '',
  `operador` varchar(50) NOT NULL DEFAULT '',
  `hr_inicio` decimal(12,2) NOT NULL DEFAULT 0.00,
  `hr_fin` decimal(12,2) NOT NULL DEFAULT 0.00,
  `combustible` int(11) NOT NULL DEFAULT 0,
  `aceite_cadena` int(11) NOT NULL DEFAULT 0,
  `acta` varchar(10) NOT NULL DEFAULT '0',
  `rodal` varchar(10) NOT NULL DEFAULT '0',
  `m3` int(11) NOT NULL DEFAULT 0,
  `carros` int(11) NOT NULL DEFAULT 0,
  `tn_despachadas` decimal(12,2) NOT NULL DEFAULT 0.00,
  `has` decimal(12,2) NOT NULL DEFAULT 0.00,
  `produccion` decimal(12,2) NOT NULL DEFAULT 0.00,
  `unitario` decimal(12,2) NOT NULL DEFAULT 0.00,
  `unidad_produccion` varchar(20) NOT NULL DEFAULT '0',
  `dist_tosquera` int(11) NOT NULL DEFAULT 0,
  `mtrs_recorridos` int(11) NOT NULL DEFAULT 0,
  `plantas` int(11) NOT NULL DEFAULT 0,
  `viaje_tosca` int(11) NOT NULL DEFAULT 0,
  `hrs_no_op` int(11) NOT NULL DEFAULT 0,
  `motivo_no_op` varchar(150) NOT NULL DEFAULT '0',
  `observaciones` varchar(150) NOT NULL DEFAULT '0',
  `stock_abc` int(11) NOT NULL DEFAULT 0,
  `aceite_hidraulico` int(11) NOT NULL DEFAULT 0,
  `aceite_motor` int(11) NOT NULL DEFAULT 0,
  `aceite_embrague` int(11) NOT NULL DEFAULT 0,
  `aceite_transmision` int(11) NOT NULL DEFAULT 0,
  `nro_parte` int(11) NOT NULL DEFAULT 0,
  `predio` varchar(50) NOT NULL DEFAULT '0',
  `cod_operador` int(11) NOT NULL DEFAULT 1,
  `cod_equipo` int(11) NOT NULL DEFAULT 1,
  `tarifa` decimal(12,2) NOT NULL DEFAULT 0.00,
  `fijo` decimal(12,2) NOT NULL DEFAULT 0.00,
  `km_carreteo` decimal(12,2) NOT NULL DEFAULT 0.00,
  `km_perfilado` decimal(12,2) NOT NULL DEFAULT 0.00,
  `hr_disposicion` decimal(12,2) NOT NULL DEFAULT 0.00,
  `km_camioneta` int(11) NOT NULL DEFAULT 0,
  `servicio_tercero` tinyint(1) NOT NULL DEFAULT 0,
  `detalle_servicio` varchar(50) NOT NULL DEFAULT '',
  `_uuid` varchar(36) NOT NULL DEFAULT '',
  `form_uuid` varchar(36) NOT NULL DEFAULT '',
  `remito` varchar(12) NOT NULL DEFAULT '',
  `remito2` varchar(12) NOT NULL DEFAULT '',
  `remito3` varchar(12) NOT NULL DEFAULT '',
  `remito_bitren` varchar(12) NOT NULL DEFAULT '',
  `cambio_cuchilla` int(11) NOT NULL DEFAULT 0,
  `lugar_carga` int(11) NOT NULL DEFAULT 0,
  `usuario` varchar(50) DEFAULT NULL,
  `cliente_camion` varchar(50) DEFAULT NULL,
  `origen_camion` varchar(50) DEFAULT NULL,
  `destino_camion` varchar(50) DEFAULT NULL,
  `fecha_hora` datetime DEFAULT NULL,
  `tarifa_empresa` float NOT NULL,
  `origen_destino_id` int(11) NOT NULL,
  `cod_un` int(11) DEFAULT NULL,
  `tabla` varchar(50) DEFAULT NULL,
  `codigo_tabla` int(11) NOT NULL,
  `espada` tinyint(4) DEFAULT NULL,
  `puntera` tinyint(4) DEFAULT NULL,
  `cadena` tinyint(4) DEFAULT NULL,
  `pinon` tinyint(4) DEFAULT NULL,
  `cantidad_cadenas` int(11) DEFAULT 0,
  `giro_pinon` tinyint(4) DEFAULT NULL,
  `origen` varchar(80) DEFAULT NULL,
  `modificado` tinyint(1) NOT NULL,
  `hora_inicio_viaje` time DEFAULT NULL,
  `hora_fin_viaje` time DEFAULT NULL,
  `remito_proveedor` varchar(20) DEFAULT NULL,
  `remito_fgpy` varchar(20) DEFAULT NULL,
  `nombre_chofer` varchar(100) DEFAULT NULL,
  `parcela` varchar(50) DEFAULT NULL,
  `bruto_destino` float NOT NULL,
  `tara_destino` float NOT NULL,
  `neto_origen` float NOT NULL,
  `neto_destino` float NOT NULL,
  `proveedor_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tarea_por_equipo`
--

DROP TABLE IF EXISTS `tarea_por_equipo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tarea_por_equipo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `kobo_id` int(11) NOT NULL DEFAULT 0,
  `equipo_id` int(10) unsigned NOT NULL DEFAULT 0,
  `tarea_id` int(11) NOT NULL DEFAULT 0,
  `mecanico_id` int(10) unsigned NOT NULL DEFAULT 1,
  `ult_hora_km` int(11) NOT NULL,
  `ult_fecha` date DEFAULT NULL,
  `tipo_mantenimiento` char(30) DEFAULT NULL,
  `obs_correctivo` varchar(250) DEFAULT NULL,
  `ubicacion` varchar(250) DEFAULT NULL,
  `uuid` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_equipo_tarea` (`equipo_id`),
  KEY `FK_tarea_tarea` (`tarea_id`),
  KEY `FK_mecanico_personal` (`mecanico_id`),
  CONSTRAINT `FK_equipo_tarea` FOREIGN KEY (`equipo_id`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  CONSTRAINT `FK_mecanico_personal` FOREIGN KEY (`mecanico_id`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE,
  CONSTRAINT `FK_tarea_tarea` FOREIGN KEY (`tarea_id`) REFERENCES `tareamantenimiento` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1396 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tareamantenimiento`
--

DROP TABLE IF EXISTS `tareamantenimiento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tareamantenimiento` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `detalle` varchar(80) NOT NULL,
  `activo` tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tareasrepuestos`
--

DROP TABLE IF EXISTS `tareasrepuestos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tareasrepuestos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tipo_tarea_id` int(11) NOT NULL,
  `repuesto_id` int(11) NOT NULL,
  `cantidad_necesaria` float NOT NULL,
  `principal` tinyint(1) NOT NULL,
  `usuario` varchar(30) NOT NULL,
  `creado` datetime NOT NULL,
  `equipo_id` int(11) DEFAULT NULL,
  `cada_cuanto` int(11) NOT NULL,
  `antelacion` int(11) NOT NULL,
  `forma_actualizacion` varchar(1) NOT NULL,
  `planificacion_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tareasrepuestos_tipo_tarea_id` (`tipo_tarea_id`),
  KEY `tareasrepuestos_repuesto_id` (`repuesto_id`),
  CONSTRAINT `tareasrepuestos_ibfk_1` FOREIGN KEY (`tipo_tarea_id`) REFERENCES `tipostareas` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `tareasrepuestos_ibfk_2` FOREIGN KEY (`repuesto_id`) REFERENCES `repuestos` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tarifa_produccion`
--

DROP TABLE IF EXISTS `tarifa_produccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tarifa_produccion` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `desde` date NOT NULL DEFAULT '0000-00-00',
  `hasta` date NOT NULL DEFAULT '0000-00-00',
  `actividad` varchar(50) NOT NULL DEFAULT '0',
  `un` int(10) unsigned NOT NULL DEFAULT 0,
  `tarifa` float NOT NULL DEFAULT 0,
  `fijo` float NOT NULL DEFAULT 0,
  `acta_id` int(10) unsigned DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `FK_UN` (`un`),
  CONSTRAINT `FK_UN` FOREIGN KEY (`un`) REFERENCES `unidadnegocio` (`idUnidadNegocio`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tipcomp`
--

DROP TABLE IF EXISTS `tipcomp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipcomp` (
  `Codigo` int(10) unsigned NOT NULL DEFAULT 0,
  `Detalle` varchar(100) NOT NULL DEFAULT '',
  `abreviatura` char(3) NOT NULL DEFAULT '',
  `letra` char(1) NOT NULL DEFAULT '',
  PRIMARY KEY (`Codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tipo_checklist`
--

DROP TABLE IF EXISTS `tipo_checklist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipo_checklist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(150) NOT NULL,
  `tipo_movil_id` int(11) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `usuario` varchar(30) NOT NULL,
  `creado` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tipochecklist_tipo_movil_id` (`tipo_movil_id`),
  CONSTRAINT `tipo_checklist_ibfk_1` FOREIGN KEY (`tipo_movil_id`) REFERENCES `tipodemovil` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tipo_de_valor`
--

DROP TABLE IF EXISTS `tipo_de_valor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipo_de_valor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `numero` int(11) NOT NULL,
  `datosadicionales` tinyint(1) NOT NULL,
  `retencion` tinyint(1) NOT NULL,
  `porcentaje` decimal(12,2) NOT NULL,
  `minimo` decimal(12,2) NOT NULL,
  `desdeoper` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tipo_inventario`
--

DROP TABLE IF EXISTS `tipo_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipo_inventario` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `detalle` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tipocomb`
--

DROP TABLE IF EXISTS `tipocomb`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipocomb` (
  `idTipoComb` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Detalle` varchar(80) NOT NULL DEFAULT '',
  `Unitario` decimal(12,4) NOT NULL DEFAULT 0.0000,
  `idArticulo` int(10) unsigned NOT NULL DEFAULT 1,
  PRIMARY KEY (`idTipoComb`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tipodemovil`
--

DROP TABLE IF EXISTS `tipodemovil`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipodemovil` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `detalle` varchar(50) NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tipofor`
--

DROP TABLE IF EXISTS `tipofor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipofor` (
  `tfo_id` smallint(6) NOT NULL,
  `tfo_nomb` char(30) NOT NULL,
  `tfo_codi` char(1) NOT NULL,
  PRIMARY KEY (`tfo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tipoiva`
--

DROP TABLE IF EXISTS `tipoiva`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipoiva` (
  `idTipoIva` int(10) unsigned NOT NULL,
  `Detalle` varchar(80) NOT NULL DEFAULT '',
  `Porcentaje` decimal(6,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`idTipoIva`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tiponeu`
--

DROP TABLE IF EXISTS `tiponeu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tiponeu` (
  `idTipoNeu` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Detalle` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`idTipoNeu`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tipos_comprobantes`
--

DROP TABLE IF EXISTS `tipos_comprobantes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipos_comprobantes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(100) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `siguiente_numero` int(11) NOT NULL,
  `debe_haber` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tipocomprobantes_descripcion` (`descripcion`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tipos_impuestos`
--

DROP TABLE IF EXISTS `tipos_impuestos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipos_impuestos` (
  `codigo` varchar(10) NOT NULL,
  `descripcion` varchar(100) NOT NULL,
  PRIMARY KEY (`codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tipos_movil`
--

DROP TABLE IF EXISTS `tipos_movil`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipos_movil` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(100) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tipodemovil_descripcion` (`descripcion`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tipostareas`
--

DROP TABLE IF EXISTS `tipostareas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipostareas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tarea` varchar(150) NOT NULL,
  `cada_cuanto` int(11) NOT NULL,
  `anticipacion` int(11) NOT NULL,
  `tipo_movil_id` int(11) NOT NULL,
  `activo` tinyint(1) NOT NULL,
  `descripcion` text NOT NULL,
  `usuario` varchar(30) NOT NULL,
  `creado` datetime NOT NULL,
  `forma_actualizacion` varchar(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tipostareas_tipo_movil_id` (`tipo_movil_id`),
  CONSTRAINT `FK_tipostareas_tipodemovil` FOREIGN KEY (`tipo_movil_id`) REFERENCES `tipodemovil` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ubicacionneumatico`
--

DROP TABLE IF EXISTS `ubicacionneumatico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ubicacionneumatico` (
  `idUbicacionNeumatico` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Detalle` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`idUbicacionNeumatico`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `unidadmedida`
--

DROP TABLE IF EXISTS `unidadmedida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `unidadmedida` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(80) NOT NULL,
  `codigo_tango` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `unidadnegocio`
--

DROP TABLE IF EXISTS `unidadnegocio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `unidadnegocio` (
  `idUnidadNegocio` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) NOT NULL DEFAULT '',
  `Prefijo` char(3) NOT NULL DEFAULT '',
  `_usuario` varchar(50) NOT NULL DEFAULT '',
  `_fecha` date NOT NULL DEFAULT '0000-00-00',
  `_hora` char(8) NOT NULL DEFAULT '00:00:00',
  `codigo_kobo` char(30) NOT NULL DEFAULT '',
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`idUnidadNegocio`)
) ENGINE=InnoDB AUTO_INCREMENT=144 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `userlev`
--

DROP TABLE IF EXISTS `userlev`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `userlev` (
  `GROUP_ID` varchar(2) DEFAULT NULL,
  `DESCRIPTIO` varchar(35) DEFAULT NULL,
  `STARTUP_AC` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('employee','admin_rrhh') DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usuarios` (
  `USUARIO` varchar(15) DEFAULT NULL,
  `NOMBRE` varchar(30) DEFAULT NULL,
  `APELLIDO` varchar(30) DEFAULT NULL,
  `GRUPO` varchar(8) DEFAULT NULL,
  `FECHAING` date DEFAULT NULL,
  `FECHABAJA` date DEFAULT NULL,
  `ACTIVO` bit(1) DEFAULT b'0',
  `CLAVE` varchar(12) DEFAULT NULL,
  `SUMCHECK` decimal(18,0) DEFAULT NULL,
  `USER_LEVEL` varchar(2) DEFAULT NULL,
  `USU_ID` int(11) NOT NULL AUTO_INCREMENT,
  `VENDEDOR` int(11) NOT NULL,
  `Correo` varchar(200) NOT NULL DEFAULT '',
  `PwdCorreo` varchar(200) NOT NULL DEFAULT '',
  `Agenda` bit(1) NOT NULL DEFAULT b'1',
  `idroles` varchar(255) NOT NULL DEFAULT '',
  `password_hash` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`USU_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vacaciones`
--

DROP TABLE IF EXISTS `vacaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vacaciones` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `empleado_id` int(10) unsigned NOT NULL DEFAULT 0,
  `desde` date NOT NULL,
  `hasta` date NOT NULL,
  `anio` int(11) NOT NULL DEFAULT 0,
  `observaciones` varchar(200) NOT NULL DEFAULT '0',
  `hora_grabacion` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  KEY `PK` (`id`),
  KEY `FK_vacaciones_personal` (`empleado_id`),
  CONSTRAINT `FK_vacaciones_personal` FOREIGN KEY (`empleado_id`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `vencimientos`
--

DROP TABLE IF EXISTS `vencimientos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vencimientos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `personal_id` int(11) DEFAULT NULL,
  `movil_id` int(11) DEFAULT NULL,
  `fecha_vencimiento` date NOT NULL,
  `descripcion` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `vencimientos_personal_id` (`personal_id`),
  KEY `vencimientos_movil_id` (`movil_id`),
  CONSTRAINT `vencimientos_ibfk_1` FOREIGN KEY (`personal_id`) REFERENCES `empleados` (`id`),
  CONSTRAINT `vencimientos_ibfk_2` FOREIGN KEY (`movil_id`) REFERENCES `equipos` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Final view structure for view `biomasa`
--

/*!50001 DROP VIEW IF EXISTS `biomasa`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `biomasa` AS select `fg`.`tablero_produccion`.`fecha` AS `fecha`,year(`fg`.`tablero_produccion`.`fecha`) AS `anio`,month(`fg`.`tablero_produccion`.`fecha`) AS `mes`,`fg`.`tablero_produccion`.`equipo` AS `equipo`,`fg`.`tablero_produccion`.`operador` AS `operador`,`fg`.`tablero_produccion`.`operacion` AS `operacion`,`fg`.`tablero_produccion`.`produccion` AS `produccion`,`fg`.`tablero_produccion`.`hr_fin` - `fg`.`tablero_produccion`.`hr_inicio` AS `hr_dia`,`fg`.`tablero_produccion`.`detalle_servicio` AS `detalle_servicio`,`fg`.`tablero_produccion`.`hr_fin` AS `hr_fin` from `tablero_produccion` where `fg`.`tablero_produccion`.`UN` = 'BIOMASA' */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `combustible`
--

/*!50001 DROP VIEW IF EXISTS `combustible`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `combustible` AS select year(`cc`.`Fecha`) AS `anio`,month(`cc`.`Fecha`) AS `mes`,`un`.`Nombre` AS `un`,`movil`.`Detalle` AS `movil`,`movil`.`Patente` AS `patente`,`fg`.`personal`.`Nombre` AS `nombre`,`cc`.`Litros` AS `litros`,`cc`.`KM` AS `KM`,`cc`.`Fecha` AS `fecha` from (((`cargacomb` `cc` join `unidadnegocio` `un` on(`cc`.`UnidadNegocio` = `un`.`idUnidadNegocio`)) join `moviles` `movil` on(`cc`.`idMovil` = `movil`.`idMovil`)) join `personal` on(`cc`.`personal` = `fg`.`personal`.`idPersonal`)) where `cc`.`tipo_mov` = 'E' and `movil`.`estadistica` = 1 */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `consumos`
--

/*!50001 DROP VIEW IF EXISTS `consumos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `consumos` AS select year(`cc`.`Fecha`) AS `anio`,month(`cc`.`Fecha`) AS `mes`,`cc`.`idMovil` AS `idMovil`,`fg`.`moviles`.`Patente` AS `patente`,`fg`.`moviles`.`Detalle` AS `detalle`,sum(`cc`.`Litros`) AS `litros`,max(`cc`.`KM`) - min(`cc`.`KM`) AS `km`,sum(`cc`.`Litros`) / (max(`cc`.`KM`) - min(`cc`.`KM`)) AS `promedio`,`fg`.`unidadnegocio`.`Nombre` AS `Nombre` from ((`cargacomb` `cc` join `moviles` on(`cc`.`idMovil` = `fg`.`moviles`.`idMovil`)) join `unidadnegocio` on(`fg`.`moviles`.`idUnidadNegocio` = `fg`.`unidadnegocio`.`idUnidadNegocio`)) where `fg`.`moviles`.`estadistica` = 1 group by year(`cc`.`Fecha`),month(`cc`.`Fecha`),`cc`.`idMovil`,`fg`.`moviles`.`Detalle` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `cosechas`
--

/*!50001 DROP VIEW IF EXISTS `cosechas`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `cosechas` AS select `fg`.`tablero_produccion`.`UN` AS `un`,`fg`.`tablero_produccion`.`equipo` AS `equipo`,month(`fg`.`tablero_produccion`.`fecha`) AS `mes`,year(`fg`.`tablero_produccion`.`fecha`) AS `anio`,`fg`.`tablero_produccion`.`fecha` AS `fecha`,`fg`.`tablero_produccion`.`produccion` AS `produccion`,`fg`.`tablero_produccion`.`plantas` AS `plantas`,`fg`.`tablero_produccion`.`operador` AS `operador`,`fg`.`tablero_produccion`.`operacion` AS `operacion`,`fg`.`tablero_produccion`.`acta` AS `acta`,`fg`.`moviles`.`Detalle` AS `Detalle` from (`tablero_produccion` join `moviles` on(`fg`.`tablero_produccion`.`cod_equipo` = `fg`.`moviles`.`idMovil`)) where `fg`.`tablero_produccion`.`operacion` in ('PROCESO','CARGA') */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `patrimonio`
--

/*!50001 DROP VIEW IF EXISTS `patrimonio`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `patrimonio` AS select year(`fg`.`tablero_produccion`.`fecha`) AS `anio`,month(`fg`.`tablero_produccion`.`fecha`) AS `mes`,`fg`.`tablero_produccion`.`fecha` AS `fecha`,`fg`.`tablero_produccion`.`equipo` AS `equipo`,`fg`.`tablero_produccion`.`operacion` AS `operacion`,`fg`.`tablero_produccion`.`hr_fin` - `fg`.`tablero_produccion`.`hr_inicio` AS `hr_dia`,`fg`.`tablero_produccion`.`produccion` AS `produccion`,`fg`.`tablero_produccion`.`predio` AS `predio`,`fg`.`tablero_produccion`.`unidad_produccion` AS `unidad_produccion` from `tablero_produccion` where `fg`.`tablero_produccion`.`UN` = 'PATRIMONIO' */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `personal_activo`
--

/*!50001 DROP VIEW IF EXISTS `personal_activo`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `personal_activo` AS select `fg`.`personal`.`idPersonal` AS `idPersonal`,`fg`.`personal`.`Nombre` AS `Nombre` from `personal` where `fg`.`personal`.`FechaBaja` = '0000-00-00' */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-10 19:35:52
