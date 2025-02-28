/*!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.8-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: tt
-- ------------------------------------------------------
-- Server version	10.11.8-MariaDB-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Actividad`
--

DROP TABLE IF EXISTS `Actividad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Actividad` (
  `IdActividad` int(11) NOT NULL AUTO_INCREMENT,
  `Pregunta` text DEFAULT NULL,
  `Respuesta` text DEFAULT NULL,
  `IdGrupo` int(11) DEFAULT NULL,
  PRIMARY KEY (`IdActividad`),
  KEY `IdGrupo` (`IdGrupo`),
  CONSTRAINT `Actividad_ibfk_1` FOREIGN KEY (`IdGrupo`) REFERENCES `Grupo` (`IdGrupo`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Actividad`
--

LOCK TABLES `Actividad` WRITE;
/*!40000 ALTER TABLE `Actividad` DISABLE KEYS */;
/*!40000 ALTER TABLE `Actividad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Administrador`
--

DROP TABLE IF EXISTS `Administrador`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Administrador` (
  `CorreoAdministrador` varchar(100) NOT NULL,
  `Contraseña` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`CorreoAdministrador`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Administrador`
--

LOCK TABLES `Administrador` WRITE;
/*!40000 ALTER TABLE `Administrador` DISABLE KEYS */;
/*!40000 ALTER TABLE `Administrador` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Alumno`
--

DROP TABLE IF EXISTS `Alumno`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Alumno` (
  `IdAlumno` int(11) NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) DEFAULT NULL,
  `Apellido` varchar(100) DEFAULT NULL,
  `Foto` varchar(255) DEFAULT NULL,
  `AciertosNumeros` int(11) NOT NULL DEFAULT 0,
  `IdGrupo` int(11) DEFAULT NULL,
  `CorreoTutor` varchar(100) DEFAULT NULL,
  `AciertosLetras` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`IdAlumno`),
  UNIQUE KEY `unique_tutor` (`CorreoTutor`),
  KEY `Alumno_ibfk_1` (`IdGrupo`),
  CONSTRAINT `Alumno_ibfk_1` FOREIGN KEY (`IdGrupo`) REFERENCES `Grupo` (`IdGrupo`) ON DELETE SET NULL,
  CONSTRAINT `fk_tutor` FOREIGN KEY (`CorreoTutor`) REFERENCES `Tutor` (`CorreoTutor`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Alumno`
--

LOCK TABLES `Alumno` WRITE;
/*!40000 ALTER TABLE `Alumno` DISABLE KEYS */;
INSERT INTO `Alumno` VALUES
(4,'Carlos','López','foto_carlos.jpg',5,NULL,'t@gmail.com',0),
(7,'karla','Salinas','foto_carlos.jpg',7,2,'t1@gmail.com',7);
/*!40000 ALTER TABLE `Alumno` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Docente`
--

DROP TABLE IF EXISTS `Docente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Docente` (
  `CorreoDocente` varchar(100) NOT NULL,
  `Nombre` varchar(100) DEFAULT NULL,
  `Apellido` varchar(100) DEFAULT NULL,
  `Contraseña` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`CorreoDocente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Docente`
--

LOCK TABLES `Docente` WRITE;
/*!40000 ALTER TABLE `Docente` DISABLE KEYS */;
INSERT INTO `Docente` VALUES
('d1@gmail.com','Juan','Pérez','123'),
('d@gmail.com','Pedro','Ramirez Inzunza','123'),
('villalobosalamillaj@gmail.com','Juan Rafael','Villalobos Alamilla','123');
/*!40000 ALTER TABLE `Docente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Gestiona`
--

DROP TABLE IF EXISTS `Gestiona`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Gestiona` (
  `CorreoAdministrador` varchar(100) NOT NULL,
  `CorreoDocente` varchar(100) NOT NULL,
  PRIMARY KEY (`CorreoAdministrador`,`CorreoDocente`),
  KEY `CorreoDocente` (`CorreoDocente`),
  CONSTRAINT `Gestiona_ibfk_1` FOREIGN KEY (`CorreoAdministrador`) REFERENCES `Administrador` (`CorreoAdministrador`) ON DELETE CASCADE,
  CONSTRAINT `Gestiona_ibfk_2` FOREIGN KEY (`CorreoDocente`) REFERENCES `Docente` (`CorreoDocente`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Gestiona`
--

LOCK TABLES `Gestiona` WRITE;
/*!40000 ALTER TABLE `Gestiona` DISABLE KEYS */;
/*!40000 ALTER TABLE `Gestiona` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Grupo`
--

DROP TABLE IF EXISTS `Grupo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Grupo` (
  `IdGrupo` int(11) NOT NULL AUTO_INCREMENT,
  `Titulo` varchar(100) DEFAULT NULL,
  `Codigo` varchar(10) DEFAULT NULL,
  `NoAlumnos` int(11) DEFAULT NULL,
  `CorreoDocente` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`IdGrupo`),
  UNIQUE KEY `Codigo` (`Codigo`),
  UNIQUE KEY `unique_docente` (`CorreoDocente`),
  CONSTRAINT `Grupo_ibfk_1` FOREIGN KEY (`CorreoDocente`) REFERENCES `Docente` (`CorreoDocente`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Grupo`
--

LOCK TABLES `Grupo` WRITE;
/*!40000 ALTER TABLE `Grupo` DISABLE KEYS */;
INSERT INTO `Grupo` VALUES
(2,'grupo de tonotos','12345',1,'d1@gmail.com');
/*!40000 ALTER TABLE `Grupo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Inscribe`
--

DROP TABLE IF EXISTS `Inscribe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Inscribe` (
  `IdInscribe` int(11) NOT NULL AUTO_INCREMENT,
  `CorreoTutor` varchar(100) DEFAULT NULL,
  `IdAlumno` int(11) DEFAULT NULL,
  `IdGrupo` int(11) DEFAULT NULL,
  PRIMARY KEY (`IdInscribe`),
  KEY `CorreoTutor` (`CorreoTutor`),
  KEY `IdAlumno` (`IdAlumno`),
  KEY `IdGrupo` (`IdGrupo`),
  CONSTRAINT `Inscribe_ibfk_1` FOREIGN KEY (`CorreoTutor`) REFERENCES `Tutor` (`CorreoTutor`) ON DELETE CASCADE,
  CONSTRAINT `Inscribe_ibfk_2` FOREIGN KEY (`IdAlumno`) REFERENCES `Alumno` (`IdAlumno`) ON DELETE CASCADE,
  CONSTRAINT `Inscribe_ibfk_3` FOREIGN KEY (`IdGrupo`) REFERENCES `Grupo` (`IdGrupo`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Inscribe`
--

LOCK TABLES `Inscribe` WRITE;
/*!40000 ALTER TABLE `Inscribe` DISABLE KEYS */;
/*!40000 ALTER TABLE `Inscribe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Tutor`
--

DROP TABLE IF EXISTS `Tutor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Tutor` (
  `CorreoTutor` varchar(100) NOT NULL,
  `Contraseña` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`CorreoTutor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Tutor`
--

LOCK TABLES `Tutor` WRITE;
/*!40000 ALTER TABLE `Tutor` DISABLE KEYS */;
INSERT INTO `Tutor` VALUES
('t1@gmail.com','123'),
('t@gmail.com','123');
/*!40000 ALTER TABLE `Tutor` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-02-27 21:31:55
