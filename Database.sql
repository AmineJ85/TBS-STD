CREATE DATABASE  IF NOT EXISTS `pfe` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `pfe`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: pfe
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `academic_calendar`
--

DROP TABLE IF EXISTS `academic_calendar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `academic_calendar` (
  `calendar_id` int NOT NULL AUTO_INCREMENT,
  `academic_year` int NOT NULL,
  `semester` tinyint NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `is_current` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`calendar_id`),
  UNIQUE KEY `academic_year` (`academic_year`,`semester`)
) ENGINE=InnoDB AUTO_INCREMENT=357 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `academic_calendar`
--

LOCK TABLES `academic_calendar` WRITE;
/*!40000 ALTER TABLE `academic_calendar` DISABLE KEYS */;
INSERT INTO `academic_calendar` VALUES (1,2025,1,'2025-05-20','2025-05-20',0),(10,2025,2,'2025-05-20','2025-05-20',0),(11,2026,1,'2025-05-20','2025-05-20',0),(12,2026,2,'2025-05-20','2025-05-20',0),(13,2027,1,'2025-05-20','2025-05-20',0),(14,2027,2,'2025-05-20','2025-05-20',0),(15,2028,1,'2025-05-20','2025-05-20',0),(16,2028,2,'2025-05-20','2025-05-20',0),(17,2029,1,'2025-05-20','2025-05-20',0),(18,2029,2,'2025-05-20','2025-05-20',0),(19,2030,1,'2025-05-20','2025-05-21',0),(20,2030,2,'2025-05-21','2025-05-21',0),(21,2031,1,'2025-05-21','2025-05-21',0),(22,2031,2,'2025-05-21','2025-05-22',0),(23,2032,1,'2025-05-22','2025-05-22',0),(24,2032,2,'2025-05-22','2025-05-22',0),(25,2033,1,'2025-05-22','2025-05-22',0),(26,2033,2,'2025-05-22','2025-05-22',0),(27,2034,1,'2025-05-22','2025-05-22',0),(28,2034,2,'2025-05-22','2025-05-22',0),(29,2035,1,'2025-05-22','2025-05-22',0),(30,2035,2,'2025-05-22','2025-05-22',0),(31,2036,1,'2025-05-22','2025-05-22',0),(32,2036,2,'2025-05-22','2025-05-22',0),(33,2037,1,'2025-05-22','2025-05-22',0),(34,2037,2,'2025-05-22','2025-05-22',0),(35,2038,1,'2025-05-22','2025-05-22',0),(36,2038,2,'2025-05-22','2025-05-22',0),(37,2039,1,'2025-05-22','2025-05-22',0),(38,2039,2,'2025-05-22','2025-05-22',0),(39,2040,1,'2025-05-22','2025-05-22',0),(40,2040,2,'2025-05-22','2025-05-22',0),(41,2041,1,'2025-05-22','2025-05-22',0),(42,2041,2,'2025-05-22','2025-05-22',0),(43,2042,1,'2025-05-22','2025-05-22',0),(44,2042,2,'2025-05-22','2025-05-22',0),(45,2043,1,'2025-05-22','2025-05-23',0),(46,2043,2,'2025-05-23','2025-05-23',0),(47,2044,1,'2025-05-23','2025-05-23',0),(48,2044,2,'2025-05-23','2025-05-24',0),(49,2045,1,'2025-05-24','2025-05-24',0),(50,2045,2,'2025-05-24','2025-05-24',0),(51,2046,1,'2025-05-24','2025-05-24',0),(52,2046,2,'2025-05-24','2025-05-24',0),(53,2047,1,'2025-05-24','2025-05-24',0),(54,2047,2,'2025-05-24','2025-05-24',0),(55,2048,1,'2025-05-24','2025-05-24',0),(56,2048,2,'2025-05-24','2025-05-24',0),(57,2049,1,'2025-05-24','2025-05-24',0),(58,2049,2,'2025-05-24','2025-05-24',0),(59,2050,1,'2025-05-24','2025-05-24',0),(60,2050,2,'2025-05-24','2025-05-25',0),(61,2051,1,'2025-05-25','2025-05-25',0),(62,2051,2,'2025-05-25','2025-05-25',0),(63,2052,1,'2025-05-25','2025-05-25',0),(64,2052,2,'2025-05-25','2025-05-25',0),(65,2053,1,'2025-05-25','2025-05-25',0),(66,2053,2,'2025-05-25','2025-05-25',0),(67,2054,1,'2025-05-25','2025-05-25',0),(68,2054,2,'2025-05-25','2025-05-26',0),(69,2055,1,'2025-05-26','2025-05-26',0),(70,2055,2,'2025-05-26','2025-05-26',0),(71,2056,1,'2025-05-26','2025-05-26',0),(72,2056,2,'2025-05-26','2025-05-26',0),(73,2057,1,'2025-05-26','2025-05-26',0),(74,2057,2,'2025-05-26','2025-05-26',0),(75,2058,1,'2025-05-26','2025-05-26',0),(76,2058,2,'2025-05-26','2025-05-26',0),(77,2059,1,'2025-05-26','2025-05-26',0),(78,2059,2,'2025-05-26','2025-05-27',0),(79,2060,1,'2025-05-27','2025-05-27',0),(80,2060,2,'2025-05-27','2025-05-27',0),(81,2061,1,'2025-05-27','2025-05-27',0),(82,2061,2,'2025-05-27','2025-05-27',0),(83,2062,1,'2025-05-27','2025-05-27',0),(84,2062,2,'2025-05-27','2025-05-27',0),(85,2063,1,'2025-05-27','2025-05-27',0),(86,2063,2,'2025-05-27','2025-05-27',0),(87,2064,1,'2025-05-27','2025-05-27',0),(88,2064,2,'2025-05-27','2025-05-27',0),(89,2065,1,'2025-05-27','2025-05-27',0),(90,2065,2,'2025-05-27','2025-05-27',0),(91,2066,1,'2025-05-27','2025-05-27',0),(92,2066,2,'2025-05-27','2025-05-27',0),(93,2067,1,'2025-05-27','2025-05-27',0),(94,2067,2,'2025-05-27','2025-05-27',0),(95,2068,1,'2025-05-27','2025-05-27',0),(96,2068,2,'2025-05-27','2025-05-27',0),(97,2069,1,'2025-05-27','2025-05-27',0),(98,2069,2,'2025-05-27','2025-05-27',0),(99,2070,1,'2025-05-27','2025-05-27',0),(100,2070,2,'2025-05-27','2025-05-27',0),(101,2071,1,'2025-05-27','2025-05-27',0),(102,2071,2,'2025-05-27','2025-05-27',0),(103,2072,1,'2025-05-27','2025-05-27',0),(104,2072,2,'2025-05-27','2025-05-27',0),(105,2073,1,'2025-05-27','2025-05-27',0),(106,2073,2,'2025-05-27','2025-05-27',0),(107,2074,1,'2025-05-27','2025-05-28',0),(108,2074,2,'2025-05-28','2025-05-30',0),(109,2075,1,'2025-05-30','2025-05-30',0),(110,2075,2,'2025-05-31','2025-05-31',0),(111,2076,1,'2025-05-31','2025-05-31',0),(112,2076,2,'2025-05-31','2025-06-01',0),(113,2077,1,'2025-06-01','2025-06-01',0),(114,2077,2,'2025-06-01','2025-06-02',0),(115,2078,1,'2025-06-02','2025-06-02',0),(116,2078,2,'2025-06-02','2025-06-02',0),(117,2079,1,'2025-06-02','2025-06-02',0),(118,2079,2,'2025-06-02','2025-06-02',0),(119,2080,1,'2025-06-02','2025-06-02',0),(120,2080,2,'2025-06-02','2025-06-02',0),(121,2081,1,'2025-06-02','2025-06-02',0),(122,2081,2,'2025-06-02','2025-06-02',0),(123,2082,1,'2025-06-02','2025-06-02',0),(124,2082,2,'2025-06-02','2025-06-04',0),(125,2083,1,'2025-06-04','2025-06-04',0),(126,2083,2,'2025-06-04','2025-06-04',0),(127,2084,1,'2025-06-04','2025-06-04',0),(128,2084,2,'2025-06-04','2025-06-04',0),(129,2085,1,'2025-06-04','2025-06-04',0),(130,2085,2,'2025-06-04','2025-06-04',0),(131,2086,1,'2025-06-04','2025-06-04',0),(132,2086,2,'2025-06-04','2025-06-05',0),(133,2087,1,'2025-06-05','2025-06-05',0),(134,2087,2,'2025-06-05','2025-06-05',0),(135,2088,1,'2025-06-05','2025-06-05',0),(136,2088,2,'2025-06-05','2025-06-05',0),(137,2089,1,'2025-06-05','2025-06-05',0),(138,2089,2,'2025-06-05','2025-06-05',0),(139,2090,1,'2025-06-05','2025-06-05',0),(140,2090,2,'2025-06-05','2025-06-05',0),(141,2091,1,'2025-06-05','2025-06-05',0),(142,2091,2,'2025-06-05','2025-06-05',0),(143,2092,1,'2025-06-05','2025-06-05',0),(144,2092,2,'2025-06-05','2025-06-05',0),(145,2093,1,'2025-06-05','2025-06-05',0),(146,2093,2,'2025-06-05','2025-06-05',0),(147,2094,1,'2025-06-05','2025-06-05',0),(148,2094,2,'2025-06-05','2025-06-05',0),(149,2095,1,'2025-06-05','2025-06-05',0),(150,2095,2,'2025-06-05','2025-06-05',0),(151,2096,1,'2025-06-05','2025-06-05',0),(152,2096,2,'2025-06-05','2025-06-05',0),(153,2097,1,'2025-06-05','2025-06-05',0),(154,2097,2,'2025-06-05','2025-06-05',0),(155,2098,1,'2025-06-05','2025-06-05',0),(156,2098,2,'2025-06-05','2025-06-05',0),(157,2099,1,'2025-06-05','2025-06-05',0),(158,2099,2,'2025-06-05','2025-06-05',0),(159,2100,1,'2025-06-05','2025-06-05',0),(160,2100,2,'2025-06-05','2025-06-05',0),(161,2101,1,'2025-06-05','2025-06-05',0),(162,2101,2,'2025-06-05','2025-06-05',0),(163,2102,1,'2025-06-05','2025-06-05',0),(164,2102,2,'2025-06-05','2025-06-05',0),(165,2103,1,'2025-06-05','2025-06-05',0),(166,2103,2,'2025-06-05','2025-06-05',0),(167,2104,1,'2025-06-05','2025-06-05',0),(168,2104,2,'2025-06-05','2025-06-05',0),(169,2105,1,'2025-06-05','2025-06-05',0),(170,2105,2,'2025-06-05','2025-06-05',0),(171,2106,1,'2025-06-05','2025-06-05',0),(172,2106,2,'2025-06-05','2025-06-05',0),(173,2107,1,'2025-06-05','2025-06-05',0),(174,2107,2,'2025-06-05','2025-06-05',0),(175,2108,1,'2025-06-05','2025-06-05',0),(176,2108,2,'2025-06-05','2025-06-05',0),(177,2109,1,'2025-06-05','2025-06-05',0),(178,2109,2,'2025-06-05','2025-06-05',0),(179,2110,1,'2025-06-05','2025-06-05',0),(180,2110,2,'2025-06-05','2025-06-05',0),(181,2111,1,'2025-06-05','2025-06-05',0),(182,2111,2,'2025-06-05','2025-06-05',0),(183,2112,1,'2025-06-05','2025-06-05',0),(184,2112,2,'2025-06-05','2025-06-06',0),(185,2113,1,'2025-06-06','2025-06-06',0),(186,2113,2,'2025-06-06','2025-06-06',0),(187,2114,1,'2025-06-06','2025-06-06',0),(188,2114,2,'2025-06-06','2025-06-07',0),(189,2115,1,'2025-06-07','2025-06-07',0),(190,2115,2,'2025-06-07','2025-06-07',0),(191,2116,1,'2025-06-07','2025-06-07',0),(192,2116,2,'2025-06-07','2025-06-07',0),(193,2117,1,'2025-06-07','2025-06-07',0),(194,2117,2,'2025-06-07','2025-06-07',0),(195,2118,1,'2025-06-07','2025-06-07',0),(196,2118,2,'2025-06-07','2025-06-07',0),(197,2119,1,'2025-06-07','2025-06-07',0),(198,2119,2,'2025-06-07','2025-06-07',0),(199,2120,1,'2025-06-07','2025-06-08',0),(200,2120,2,'2025-06-08','2025-06-08',0),(201,2121,1,'2025-06-08','2025-06-08',0),(202,2121,2,'2025-06-08','2025-06-08',0),(203,2122,1,'2025-06-08','2025-06-08',0),(204,2122,2,'2025-06-08','2025-06-08',0),(205,2123,1,'2025-06-08','2025-06-08',0),(206,2123,2,'2025-06-08','2025-06-08',0),(207,2124,1,'2025-06-08','2025-06-10',0),(208,2124,2,'2025-06-10','2025-06-10',0),(209,2125,1,'2025-06-10','2025-06-10',0),(210,2125,2,'2025-06-10','2025-06-10',0),(211,2126,1,'2025-06-10','2025-06-11',0),(212,2126,2,'2025-06-11','2025-06-11',0),(213,2127,1,'2025-06-11','2025-06-11',0),(214,2127,2,'2025-06-11','2025-06-11',0),(215,2128,1,'2025-06-11','2025-06-11',0),(216,2128,2,'2025-06-11','2025-06-11',0),(217,2129,1,'2025-06-11','2025-06-12',0),(218,2129,2,'2025-06-12','2025-06-12',0),(219,2130,1,'2025-06-12','2025-06-12',0),(220,2130,2,'2025-06-12','2025-06-12',0),(221,2131,1,'2025-06-12','2025-06-12',0),(222,2131,2,'2025-06-12','2025-06-12',0),(223,2132,1,'2025-06-12','2025-06-12',0),(224,2132,2,'2025-06-12','2025-06-12',0),(225,2133,1,'2025-06-12','2025-06-12',0),(226,2133,2,'2025-06-12','2025-06-12',0),(227,2134,1,'2025-06-12','2025-06-12',0),(228,2134,2,'2025-06-12','2025-06-12',0),(229,2135,1,'2025-06-12','2025-06-12',0),(230,2135,2,'2025-06-12','2025-06-12',0),(231,2136,1,'2025-06-12','2025-06-12',0),(232,2136,2,'2025-06-12','2025-06-12',0),(233,2137,1,'2025-06-12','2025-06-12',0),(234,2137,2,'2025-06-12','2025-06-12',0),(235,2138,1,'2025-06-12','2025-06-12',0),(236,2138,2,'2025-06-12','2025-06-12',0),(237,2139,1,'2025-06-12','2025-06-12',0),(238,2139,2,'2025-06-12','2025-06-12',0),(239,2140,1,'2025-06-12','2025-06-12',0),(240,2140,2,'2025-06-12','2025-06-12',0),(241,2141,1,'2025-06-12','2025-06-12',0),(242,2141,2,'2025-06-12','2025-06-12',0),(243,2142,1,'2025-06-12','2025-06-12',0),(244,2142,2,'2025-06-12','2025-06-12',0),(245,2143,1,'2025-06-12','2025-06-12',0),(246,2143,2,'2025-06-12','2025-06-12',0),(247,2144,1,'2025-06-12','2025-06-12',0),(248,2144,2,'2025-06-12','2025-06-12',0),(249,2145,1,'2025-06-12','2025-06-12',0),(250,2145,2,'2025-06-12','2025-06-12',0),(251,2146,1,'2025-06-12','2025-06-12',0),(252,2146,2,'2025-06-12','2025-06-12',0),(253,2147,1,'2025-06-12','2025-06-12',0),(254,2147,2,'2025-06-12','2025-06-12',0),(255,2148,1,'2025-06-12','2025-06-12',0),(256,2148,2,'2025-06-12','2025-06-12',0),(257,2149,1,'2025-06-12','2025-06-12',0),(258,2149,2,'2025-06-12','2025-06-12',0),(259,2150,1,'2025-06-12','2025-06-12',0),(260,2150,2,'2025-06-12','2025-06-12',0),(261,2151,1,'2025-06-12','2025-06-12',0),(262,2151,2,'2025-06-12','2025-06-12',0),(263,2152,1,'2025-06-12','2025-06-12',0),(264,2152,2,'2025-06-12','2025-06-12',0),(265,2153,1,'2025-06-12','2025-06-12',0),(266,2153,2,'2025-06-12','2025-06-12',0),(267,2154,1,'2025-06-12','2025-06-12',0),(268,2154,2,'2025-06-12','2025-06-12',0),(269,2155,1,'2025-06-12','2025-06-12',0),(270,2155,2,'2025-06-12','2025-06-12',0),(271,2156,1,'2025-06-12','2025-06-12',0),(272,2156,2,'2025-06-13','2025-06-13',0),(273,2157,1,'2025-06-13','2025-06-13',0),(274,2157,2,'2025-06-13','2025-06-13',0),(275,2158,1,'2025-06-13','2025-06-13',0),(276,2158,2,'2025-06-13','2025-06-14',0),(277,2159,1,'2025-06-14','2025-06-14',0),(278,2159,2,'2025-06-14','2025-06-14',0),(279,2160,1,'2025-06-14','2025-06-14',0),(280,2160,2,'2025-06-14','2025-06-14',0),(281,2161,1,'2025-06-14','2025-06-14',0),(282,2161,2,'2025-06-14','2025-06-14',0),(283,2162,1,'2025-06-14','2025-06-14',0),(284,2162,2,'2025-06-14','2025-06-14',0),(285,2163,1,'2025-06-14','2025-06-14',0),(286,2163,2,'2025-06-14','2025-06-14',0),(287,2164,1,'2025-06-14','2025-06-14',0),(288,2164,2,'2025-06-14','2025-06-14',0),(289,2165,1,'2025-06-14','2025-06-14',0),(290,2165,2,'2025-06-14','2025-06-14',0),(291,2166,1,'2025-06-14','2025-06-14',0),(292,2166,2,'2025-06-14','2025-06-20',0),(293,2167,1,'2025-06-20','2025-06-21',0),(294,2167,2,'2025-06-21','2025-06-21',0),(295,2168,1,'2025-06-21','2025-06-21',0),(296,2168,2,'2025-06-21','2025-06-21',0),(297,2169,1,'2025-06-21','2025-06-21',0),(298,2169,2,'2025-06-21','2025-06-21',0),(299,2170,1,'2025-06-21','2025-06-21',0),(300,2170,2,'2025-06-21','2025-06-21',0),(301,2171,1,'2025-06-21','2025-06-21',0),(302,2171,2,'2025-06-21','2025-06-21',0),(303,2172,1,'2025-06-21','2025-06-21',0),(304,2172,2,'2025-06-21','2025-06-21',0),(305,2173,1,'2025-06-21','2025-06-21',0),(306,2173,2,'2025-06-21','2025-06-21',0),(307,2174,1,'2025-06-21','2025-06-21',0),(308,2174,2,'2025-06-21','2025-06-21',0),(309,2175,1,'2025-06-21','2025-06-21',0),(310,2175,2,'2025-06-21','2025-06-21',0),(311,2176,1,'2025-06-21','2025-06-21',0),(312,2176,2,'2025-06-21','2025-06-21',0),(313,2177,1,'2025-06-21','2025-06-21',0),(314,2177,2,'2025-06-21','2025-06-21',0),(315,2178,1,'2025-06-21','2025-06-21',0),(316,2178,2,'2025-06-21','2025-06-21',0),(317,2179,1,'2025-06-21','2025-06-21',0),(318,2179,2,'2025-06-21','2025-06-21',0),(319,2180,1,'2025-06-21','2025-06-21',0),(320,2180,2,'2025-06-21','2025-06-21',0),(321,2181,1,'2025-06-21','2025-06-21',0),(322,2181,2,'2025-06-21','2025-06-21',0),(323,2182,1,'2025-06-21','2025-06-22',0),(324,2182,2,'2025-06-22','2025-06-22',0),(325,2183,1,'2025-06-22','2025-06-22',0),(326,2183,2,'2025-06-22','2025-06-22',0),(327,2184,1,'2025-06-22','2025-06-22',0),(328,2184,2,'2025-06-22','2025-06-25',0),(329,2185,1,'2025-06-25','2025-06-25',0),(330,2185,2,'2025-06-25','2025-06-25',0),(331,2186,1,'2025-06-25','2025-06-26',0),(332,2186,2,'2025-06-26','2025-06-26',0),(333,2187,1,'2025-06-26','2025-06-26',0),(334,2187,2,'2025-06-26','2025-06-27',0),(335,2188,1,'2025-06-27','2025-06-27',0),(337,2188,2,'2025-06-29','2025-07-02',0),(347,2189,1,'2025-07-02','2025-07-02',0),(348,2189,2,'2025-07-02','2025-07-02',0),(349,2190,1,'2025-07-02','2025-07-02',0),(350,2190,2,'2025-07-02','2025-07-02',0),(351,2191,1,'2025-07-02','2025-07-02',0),(352,2191,2,'2025-07-02','2025-07-04',0),(353,2192,1,'2025-07-04','2025-07-04',0),(354,2192,2,'2025-07-04','2025-07-09',0),(355,2193,1,'2025-07-09','2025-07-09',0),(356,2193,2,'2025-07-09',NULL,1);
/*!40000 ALTER TABLE `academic_calendar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `add_course`
--

DROP TABLE IF EXISTS `add_course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `add_course` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `course_code` varchar(20) DEFAULT NULL,
  `year` int NOT NULL,
  `semester` int NOT NULL,
  `status` enum('enrolled','passed','failed','notenrolled') NOT NULL,
  `date` date DEFAULT NULL,
  `letter_grade` varchar(2) DEFAULT NULL,
  `grade_point` decimal(2,1) DEFAULT NULL,
  `retake` tinyint DEFAULT NULL,
  `forgiveness` tinyint DEFAULT NULL,
  `lecture_study_group` varchar(50) DEFAULT NULL,
  `tutorial_study_group` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_add_course_student` (`student_id`),
  KEY `fk_add_course_course_code` (`course_code`),
  CONSTRAINT `fk_add_course_course_code` FOREIGN KEY (`course_code`) REFERENCES `courses` (`course_code`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_add_course_student` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=828 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `add_course`
--

LOCK TABLES `add_course` WRITE;
/*!40000 ALTER TABLE `add_course` DISABLE KEYS */;
INSERT INTO `add_course` VALUES (1,3,'BCOR 100',1,1,'passed','2025-07-02','C',2.0,0,NULL,NULL,NULL),(2,3,'BCOR 110',1,1,'passed','2025-07-02','D',1.0,0,NULL,NULL,NULL),(3,3,'BCOR 120',1,1,'passed','2025-07-02','D',1.0,0,NULL,NULL,NULL),(4,3,'NBC 100',1,1,'passed','2025-07-02','D',1.0,0,NULL,NULL,NULL),(5,3,'NBC 101',1,1,'passed','2025-07-02','C',2.0,0,NULL,NULL,NULL),(6,3,'CS 100',1,1,'passed','2025-07-02','C',2.0,0,NULL,NULL,NULL),(7,3,'BCOR 111',1,2,'passed','2025-07-02','C',2.0,0,NULL,NULL,NULL),(8,3,'BCOR 130',1,2,'passed','2025-07-02','C',2.0,0,NULL,NULL,NULL),(9,3,'BCOR 140',1,2,'failed','2025-07-02','F',0.0,0,NULL,NULL,NULL),(10,3,'BCOR 150',1,2,'passed','2025-07-02','C',2.0,0,NULL,NULL,NULL),(11,3,'NBC 120',1,2,'passed','2025-07-02','D+',1.3,0,NULL,NULL,NULL),(12,3,'CS 120',1,2,'passed','2025-07-02','C',2.0,0,NULL,NULL,NULL),(13,3,'BCOR 225',2,1,'passed','2025-07-02','A-',3.7,0,NULL,NULL,NULL),(14,3,'BCOR 240',2,1,'passed','2025-07-02','C',2.0,0,NULL,NULL,NULL),(15,3,'BCOR 250',2,1,'passed','2025-07-02','C',2.0,0,NULL,NULL,NULL),(16,3,'BCOR 270',2,1,'passed','2025-07-02','C',2.0,0,NULL,NULL,NULL),(17,3,'NBC 200',2,1,'passed','2025-07-02','C',2.0,0,NULL,NULL,NULL),(18,3,'CS 200',2,1,'passed','2025-07-02','C',2.0,0,NULL,NULL,NULL),(776,3,'BCOR 140',2,2,'passed','2025-07-04','B',3.0,0,NULL,NULL,NULL),(777,3,'BCOR 200',2,2,'passed','2025-07-04','B',3.0,0,NULL,NULL,NULL),(778,3,'BCOR 210',2,2,'passed','2025-07-04','B',3.0,0,NULL,NULL,NULL),(779,3,'BCOR 230',2,2,'passed','2025-07-04','B',3.0,0,NULL,NULL,NULL),(780,3,'BCOR 260',2,2,'passed','2025-07-04','B',3.0,0,NULL,NULL,NULL),(781,3,'NBC 210',2,2,'passed','2025-07-04','B',3.0,0,NULL,NULL,NULL),(782,3,'CS 220',2,2,'passed','2025-07-04','B',3.0,0,NULL,NULL,NULL),(795,3,'ACCT 310',3,1,'passed','2025-07-04','B',3.0,0,NULL,NULL,NULL),(796,3,'BA 305',3,1,'passed','2025-07-04','B',3.0,0,NULL,NULL,NULL),(797,3,'BA 340',3,1,'passed','2025-07-04','B',3.0,0,NULL,NULL,NULL),(798,3,'BA 350',3,1,'passed','2025-07-04','B',3.0,0,NULL,NULL,NULL),(799,3,'FIN 300',3,1,'passed','2025-07-04','B',3.0,0,NULL,NULL,NULL),(800,3,'FIN 350',3,1,'passed','2025-07-04','B',3.0,0,NULL,NULL,NULL),(812,3,'NBC 300',3,2,'passed','2025-07-09','B',3.0,0,NULL,NULL,NULL),(813,3,'BA 360',3,2,'passed','2025-07-09','B',3.0,0,NULL,NULL,NULL),(814,3,'FIN 320',3,2,'passed','2025-07-09','B',3.0,0,NULL,NULL,NULL),(815,3,'FIN 330',3,2,'passed','2025-07-09','B',3.0,0,NULL,NULL,NULL),(816,3,'FIN 360',3,2,'passed','2025-07-09','B',3.0,0,NULL,NULL,NULL),(817,3,'FIN 310',3,2,'passed','2025-07-09','B',3.0,0,NULL,NULL,NULL),(823,3,'BA 420',4,1,'passed','2025-07-09','B',3.0,0,NULL,NULL,NULL),(824,3,'FIN 410',4,1,'passed','2025-07-09','B',3.0,0,NULL,NULL,NULL),(825,3,'FIN 420',4,1,'passed','2025-07-09','B',3.0,0,NULL,NULL,NULL),(826,3,'FIN 440',4,1,'passed','2025-07-09','B',3.0,0,NULL,NULL,NULL),(827,3,'FIN 450',4,1,'passed','2025-07-09','B',3.0,0,NULL,NULL,NULL);
/*!40000 ALTER TABLE `add_course` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_add_course_insert` AFTER INSERT ON `add_course` FOR EACH ROW BEGIN
    -- Call the procedure to update the summary
    CALL update_semester_summary(NEW.student_id, NEW.year, NEW.semester);
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `update_grade_fields` BEFORE UPDATE ON `add_course` FOR EACH ROW BEGIN
    DECLARE gp DECIMAL(2,1);
    DECLARE lg VARCHAR(2);
    DECLARE st VARCHAR(10);

    -- Case: grade_point is being updated
    IF NEW.grade_point IS NOT NULL AND (NEW.grade_point != OLD.grade_point OR NEW.letter_grade IS NULL) THEN
        SELECT letter_grade, status
        INTO lg, st
        FROM grade_policy
        WHERE grade_point = ROUND(NEW.grade_point, 1)
        LIMIT 1;

        SET NEW.letter_grade = lg;
        SET NEW.status = st;

    -- Case: letter_grade is being updated
    ELSEIF NEW.letter_grade IS NOT NULL AND (NEW.letter_grade != OLD.letter_grade OR NEW.grade_point IS NULL) THEN

        -- Handle 'P' and 'TC' explicitly
        IF NEW.letter_grade IN ('P', 'TC') THEN
            SET NEW.grade_point = NULL;
            SET NEW.status = 'passed';
        ELSE
            SELECT grade_point, status
            INTO gp, st
            FROM grade_policy
            WHERE letter_grade = NEW.letter_grade
            LIMIT 1;

            SET NEW.grade_point = gp;
            SET NEW.status = st;
        END IF;

    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `after_add_course_update` AFTER UPDATE ON `add_course` FOR EACH ROW BEGIN
    -- Only trigger if status or grade point changed
    IF (OLD.status != NEW.status OR OLD.grade_point != NEW.grade_point) THEN
        -- Call the procedure to update the summary
        CALL update_semester_summary(NEW.student_id, NEW.year, NEW.semester);
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `admin_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(40) NOT NULL,
  `last_name` varchar(40) NOT NULL,
  `email_address` varchar(80) NOT NULL,
  `password` varchar(255) NOT NULL,
  `profile_image` longblob,
  `phone` varchar(20) DEFAULT NULL,
  `national_id` int DEFAULT NULL,
  PRIMARY KEY (`admin_id`),
  UNIQUE KEY `email_address` (`email_address`),
  UNIQUE KEY `national_id` (`national_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (1,'tbs','tbs','tbs@tbs.tbs','scrypt:32768:8:1$q1FeRjIK1RW3yOA2$4058690bb07e783f286bcc8532e8328cb531cadf10b95b71ce68ab7013809575ceb0eb609896df9ed493d67c093b83116a320797e4a64c4ecff661409aeb6da3',NULL,'555-123-4567',NULL);
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `board_probation_extension`
--

DROP TABLE IF EXISTS `board_probation_extension`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `board_probation_extension` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `status` enum('pending','approved','rejected') NOT NULL DEFAULT 'pending',
  `handled_by_admin` int DEFAULT NULL,
  `decision_date` datetime DEFAULT NULL,
  `board_comments` text,
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`),
  KEY `handled_by_admin` (`handled_by_admin`),
  CONSTRAINT `board_probation_extension_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`),
  CONSTRAINT `board_probation_extension_ibfk_2` FOREIGN KEY (`handled_by_admin`) REFERENCES `admin` (`admin_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `board_probation_extension`
--

LOCK TABLES `board_probation_extension` WRITE;
/*!40000 ALTER TABLE `board_probation_extension` DISABLE KEYS */;
INSERT INTO `board_probation_extension` VALUES (3,3,'pending',NULL,NULL,NULL);
/*!40000 ALTER TABLE `board_probation_extension` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_elective_groups`
--

DROP TABLE IF EXISTS `course_elective_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_elective_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `elective_group_number` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `course_elective_groups_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_elective_groups`
--

LOCK TABLES `course_elective_groups` WRITE;
/*!40000 ALTER TABLE `course_elective_groups` DISABLE KEYS */;
INSERT INTO `course_elective_groups` VALUES (1,96,1),(2,101,1),(3,97,2),(4,102,2),(5,98,3),(6,103,3),(7,99,4),(8,104,4),(9,100,5),(10,105,5),(11,46,6),(12,50,6),(13,106,6),(14,94,7),(15,95,7),(16,50,7),(17,106,7),(18,84,7);
/*!40000 ALTER TABLE `course_elective_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_prerequisites`
--

DROP TABLE IF EXISTS `course_prerequisites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_prerequisites` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `prerequisite_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_id` (`course_id`,`prerequisite_id`),
  KEY `prerequisite_id` (`prerequisite_id`),
  CONSTRAINT `course_prerequisites_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE,
  CONSTRAINT `course_prerequisites_ibfk_2` FOREIGN KEY (`prerequisite_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=72 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_prerequisites`
--

LOCK TABLES `course_prerequisites` WRITE;
/*!40000 ALTER TABLE `course_prerequisites` DISABLE KEYS */;
INSERT INTO `course_prerequisites` VALUES (2,12,4),(1,13,6),(5,15,9),(6,17,11),(3,19,12),(4,25,19),(7,28,15),(8,29,9),(9,30,9),(10,31,9),(11,32,29),(12,33,15),(13,34,9),(14,34,20),(15,35,31),(16,37,2),(17,38,17),(18,39,17),(19,40,23),(20,41,39),(21,42,39),(22,43,38),(23,44,24),(24,45,24),(25,46,16),(26,47,24),(27,48,24),(28,49,24),(29,50,24),(30,51,20),(31,52,14),(32,53,26),(33,55,54),(34,56,54),(35,57,52),(36,59,22),(37,60,22),(38,61,22),(39,62,22),(40,63,22),(41,64,22),(42,65,22),(43,66,10),(44,66,16),(45,69,21),(46,69,22),(47,69,23),(48,69,24),(49,70,58),(50,71,56),(51,72,55),(57,74,23),(58,76,21),(59,76,23),(53,77,17),(52,77,22),(54,78,22),(55,79,22),(56,80,22),(65,81,32),(66,82,32),(67,83,32),(68,84,35),(60,85,24),(61,86,44),(62,87,44),(63,88,17),(64,88,48),(69,89,10),(70,89,16),(71,95,24);
/*!40000 ALTER TABLE `course_prerequisites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_sessions`
--

DROP TABLE IF EXISTS `course_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_sessions` (
  `course_code` varchar(20) NOT NULL,
  `lecture_sessions` int NOT NULL DEFAULT '0',
  `tutorial_sessions` int NOT NULL DEFAULT '0',
  `total_sessions` int GENERATED ALWAYS AS ((`lecture_sessions` + `tutorial_sessions`)) STORED,
  PRIMARY KEY (`course_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_sessions`
--

LOCK TABLES `course_sessions` WRITE;
/*!40000 ALTER TABLE `course_sessions` DISABLE KEYS */;
INSERT INTO `course_sessions` (`course_code`, `lecture_sessions`, `tutorial_sessions`) VALUES ('BA 350',2,1),('BCOR 111',2,1),('BCOR 130',2,1),('BCOR 140',2,1),('BCOR 150',2,1),('BCOR 200',2,0),('BCOR 210',2,0),('BCOR 230',2,1),('BCOR 260',2,1),('CS 120',2,0),('CS 220',2,0),('NBC 120',2,0),('NBC 130',1,0),('NBC 210',2,0);
/*!40000 ALTER TABLE `course_sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_code` varchar(20) NOT NULL,
  `course_name` varchar(100) NOT NULL,
  `coefficient` int NOT NULL,
  `semester` int NOT NULL,
  `year` int NOT NULL,
  `for_major` varchar(100) DEFAULT NULL,
  `for_minor` varchar(100) DEFAULT NULL,
  `for_minor_if_major_is` varchar(100) DEFAULT NULL,
  `minor_study_year` int DEFAULT NULL,
  `description` text,
  `has_lecture` tinyint NOT NULL DEFAULT '1',
  `has_tutorial` tinyint NOT NULL DEFAULT '0',
  `in_curriculum` tinyint NOT NULL DEFAULT '1',
  `requires_french` tinyint(1) DEFAULT '0',
  `eligible_for_makeup` tinyint(1) DEFAULT '1',
  `as_extra` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_code` (`course_code`)
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
INSERT INTO `courses` VALUES (1,'BCOR 100','TBS Organization Seminar',0,1,1,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(2,'BCOR 110','Calculus for Business',3,1,1,NULL,NULL,NULL,NULL,'This course explores key topics in differential and integral calculus, including limits and continuity, differentials and arithmetic & geometric sequences.',1,0,1,0,1,1),(3,'BCOR 120','Principles of Management',3,1,1,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(4,'NBC 100','Intensive General English',3,1,1,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(5,'NBC 101','Debating Skills',1,1,1,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(6,'NBC 110','French I',1,1,1,NULL,NULL,NULL,NULL,NULL,1,0,1,1,1,1),(7,'CS 100','Algorithms and Initiation to Programming',3,1,1,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(8,'BCOR 111','Linear Algebra for Business',3,2,1,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(9,'BCOR 130','Financial Accounting',3,2,1,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(10,'BCOR 140','Introduction to Microeconomics',3,2,1,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(11,'BCOR 150','Probability & Statistics for Business I',3,2,1,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(12,'NBC 120','English Communication Skills',2,2,1,NULL,NULL,NULL,NULL,NULL,1,1,1,0,1,1),(13,'NBC 130','French II',1,2,1,NULL,NULL,NULL,NULL,NULL,1,0,1,1,1,1),(14,'CS 120','Database Design and Management',3,2,1,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(15,'BCOR 225','Managerial Accounting',3,1,2,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(16,'BCOR 240','Introduction to Macroeconomics',3,1,2,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(17,'BCOR 250','Probability and Statistics for Business II',3,1,2,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(18,'BCOR 270','Business Law',3,1,2,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(19,'NBC 200','Business English',2,1,2,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(20,'CS 200','Web Development',3,1,2,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(21,'BCOR 200','Introduction to Management of Information Systems',3,2,2,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(22,'BCOR 210','Fundamentals of Marketing',3,2,2,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(23,'BCOR 230','Business Optimization',3,2,2,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(24,'BCOR 260','Principles of Finance',3,2,2,NULL,NULL,NULL,NULL,'Principles of Finance introduces core financial concepts such as the time value of money, capital budgeting, valuation of stocks and bonds, and financial statement analysis.',1,0,1,0,1,1),(25,'NBC 210','Technical Writing',2,2,2,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(26,'CS 220','Advanced Web Development',3,2,2,NULL,NULL,NULL,NULL,NULL,1,0,1,0,1,1),(27,'NBC 300','Reporting Skills',1,2,3,'NBC','BA,MRK,IT,FIN,ACCT',NULL,NULL,NULL,1,0,1,0,1,1),(28,'ACCT 300','Advanced Managerial Accounting',3,1,3,'ACCT','ACCT',NULL,4,NULL,1,0,1,0,1,1),(29,'ACCT 305','Intermediate Accounting I',3,1,3,'ACCT','ACCT',NULL,NULL,NULL,1,0,1,0,1,1),(30,'ACCT 310','Financial Statements Analysis',3,1,3,'ACCT,FIN','FIN','BA',4,NULL,1,0,1,0,1,1),(31,'ACCT 335','Taxation I',3,1,3,'ACCT','ACCT',NULL,NULL,NULL,1,0,1,0,1,1),(32,'ACCT 320','Intermediate Accounting II',3,2,3,'ACCT','ACCT',NULL,NULL,NULL,1,0,1,0,1,1),(33,'ACCT 330','Accounting Information Systems',3,2,3,'ACCT',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(34,'ACCT 340','Accounting Technology and Bookkeeping',3,2,3,'ACCT',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(35,'ACCT 370','Taxation II',3,2,3,'ACCT',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(36,'BA 300','Decision and Game Theory',3,1,3,'BA','BA','ACCT,IT,MRK',4,NULL,1,0,1,0,1,1),(37,'BA 305','Production and Operations Management',3,1,3,'BA,MRK','BA',NULL,NULL,NULL,1,0,1,0,1,1),(38,'BA 340','Data Analysis',3,1,3,'BA','BA',NULL,NULL,NULL,1,0,1,0,1,1),(39,'BA 350','Econometrics',3,1,3,'BA,FIN','BA',NULL,NULL,NULL,1,0,1,0,1,1),(40,'BA 310','Operations Research',3,2,3,'BA',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(41,'BA 320','Time Series Analysis',3,2,3,'BA','BA','ACCT,IT',NULL,NULL,1,0,1,0,1,1),(42,'BA 351','Advanced Econometrics',3,2,3,'BA',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(43,'BA 360','Business Data Mining',3,2,3,'BA','BA','FIN,MRK',NULL,NULL,1,0,1,0,1,1),(44,'FIN 300','Corporate Finance',3,1,3,'FIN','FIN',NULL,NULL,NULL,1,0,1,0,1,1),(45,'FIN 350','Financial Markets',3,1,3,'FIN','FIN',NULL,NULL,NULL,1,0,1,0,1,1),(46,'FIN 310','Money and Banking',3,2,3,'FIN',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(47,'FIN 320','Management of Financial Institutions',3,2,3,'FIN',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(48,'FIN 330','Derivative Securities',3,2,3,'FIN',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(49,'FIN 360','Investments and Portfolio Management',3,2,3,'FIN','FIN',NULL,NULL,NULL,1,0,1,0,1,1),(50,'FIN 380','Ethical and Professional Standards',3,2,3,'FIN',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(51,'IT 300','Business Intelligence and Database Administration',3,1,3,'IT','IT',NULL,NULL,NULL,1,0,1,0,1,1),(52,'IT 320','Object-Oriented Programming',3,1,3,'IT','IT','MRK,ACCT,FIN',4,NULL,1,0,1,0,1,1),(53,'IT 325','Web Services',3,1,3,'IT','IT','BA',4,NULL,1,0,1,0,1,1),(54,'IT 350','System Administration',3,1,3,'IT','IT',NULL,NULL,NULL,1,0,1,0,1,1),(55,'IT 310','Networking Fundamentals',3,2,3,'IT',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(56,'IT 360','Information Systems Assurance and Security',3,2,3,'IT','IT',NULL,NULL,NULL,1,0,1,0,1,1),(57,'IT 370','Advanced Programming',3,2,3,'IT',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(58,'IT 385','Artificial Intelligence',3,2,3,'IT',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(59,'MRK 300','Consumer Behavior',3,1,3,'MRK','MRK',NULL,NULL,NULL,1,0,1,0,1,1),(60,'MRK 310','Marketing Communication',3,1,3,'MRK',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(61,'MRK 320','International Marketing',3,1,3,'MRK','MRK',NULL,NULL,NULL,1,0,1,0,1,1),(62,'MRK 305','Product Management',3,2,3,'MRK',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(63,'MRK 330','Marketing Channels',3,2,3,'MRK',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(64,'MRK 340','Digital Marketing',3,2,3,'MRK','MRK',NULL,NULL,NULL,1,0,1,0,1,1),(65,'MRK 370','Sales Management',3,2,3,'MRK',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(66,'ECO 300','International Trade Theory and Policy',3,1,3,NULL,'IBE',NULL,NULL,NULL,1,0,1,0,1,1),(67,'ECO 310','International and Global Politics',3,1,3,NULL,'IBE',NULL,NULL,NULL,1,0,1,0,1,1),(68,'ECO 320','Political Economy of Development',3,2,3,NULL,'IBE',NULL,NULL,NULL,1,0,1,0,1,1),(69,'IT 400','Project Management',3,1,4,'IT','IT',NULL,NULL,NULL,1,1,1,0,1,1),(70,'IT 430','Machine Learning',3,1,4,'IT',NULL,NULL,NULL,NULL,1,1,1,0,1,1),(71,'IT 440','Blockchain Development',3,1,4,'IT',NULL,NULL,NULL,NULL,1,1,1,0,1,1),(72,'IT 460','Cloud Computing Technologies and Economic Models',3,1,4,'IT',NULL,NULL,NULL,NULL,1,1,1,0,1,1),(73,'BA 400','Project Management',3,1,4,'BA',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(74,'BA 410','Network Analysis',3,1,4,'BA',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(75,'BA 420','Supply Chain Management',3,1,4,'BA','BA',NULL,NULL,NULL,1,0,1,0,1,1),(76,'BA 450','Decision Support Systems',3,1,4,'BA',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(77,'MRK 400','Marketing Research',3,1,4,'MRK','MRK',NULL,NULL,NULL,1,0,1,0,1,1),(78,'MRK 420','Services Marketing',3,1,4,'MRK','MRK',NULL,NULL,NULL,1,0,1,0,1,1),(79,'MRK 430','Brand Management',3,1,4,'MRK',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(80,'MRK 440','Strategic Marketing Management',3,1,4,'MRK',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(81,'ACCT 400','Advanced Accounting',3,1,4,'ACCT','ACCT',NULL,NULL,NULL,1,0,1,0,1,1),(82,'ACCT 410','Auditing',3,1,4,'ACCT',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(83,'ACCT 425','Special Topics in Accounting',3,1,4,'ACCT',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(84,'ACCT 430','Advanced Fisc',3,1,4,'ACCT',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(85,'FIN 410','International Financial Management',3,1,4,'FIN','FIN','BA,ACCT,IT',NULL,NULL,1,0,1,0,1,1),(86,'FIN 420','Financial Modeling in Excel',3,1,4,'FIN','FIN','IT',NULL,NULL,1,0,1,0,1,1),(87,'FIN 440','Advanced Corporate Finance',3,1,4,'FIN','FIN','ACCT',NULL,NULL,1,0,1,0,1,1),(88,'FIN 450','Financial Risk Management',3,1,4,'FIN',NULL,NULL,NULL,NULL,1,0,1,0,1,1),(89,'ECO 400','International Political Economy',3,2,4,'','IBE','',NULL,'',1,0,1,0,1,1),(90,'ECO 410','International Financial Economics',3,2,4,NULL,'IBE',NULL,NULL,NULL,1,0,1,0,1,1),(94,'FIN 480','Dynamic Asset Pricing Theory',3,2,3,'FIN',NULL,NULL,NULL,NULL,1,1,1,0,1,1),(95,'FIN 430','Islamic Finance',3,2,3,'FIN',NULL,NULL,NULL,NULL,1,1,1,0,1,1),(96,'BA 498','Mini Senior Project',6,2,4,'BA',NULL,NULL,NULL,NULL,1,0,1,0,0,0),(97,'ACCT 498','Mini Senior Project',6,2,4,'ACCT',NULL,NULL,NULL,NULL,1,0,1,0,0,0),(98,'FIN 498','Mini Senior Project',6,2,4,'FIN',NULL,NULL,NULL,NULL,1,0,1,0,0,0),(99,'MRK 498','Mini Senior Project',6,2,4,'MRK',NULL,NULL,NULL,NULL,1,0,1,0,0,0),(100,'IT 498','Mini Senior Project',6,2,4,'IT',NULL,NULL,NULL,NULL,1,0,1,0,0,0),(101,'BA 499','Senior Project',12,2,4,'BA',NULL,NULL,NULL,NULL,1,0,1,0,0,0),(102,'ACCT 499','Senior Project',12,2,4,'ACCT',NULL,NULL,NULL,NULL,1,0,1,0,0,0),(103,'FIN 499','Senior Project',12,2,4,'FIN',NULL,NULL,NULL,NULL,1,0,1,0,0,0),(104,'MRK 499','Senior Project',12,2,4,'MRK',NULL,NULL,NULL,NULL,1,0,1,0,0,0),(105,'IT 499','Senior Project',12,2,4,'IT',NULL,NULL,NULL,NULL,1,0,1,0,0,0),(106,'FIN 490','Private Equity',3,2,3,'FIN',NULL,NULL,NULL,NULL,1,0,1,0,1,1);
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drop_course_requests`
--

DROP TABLE IF EXISTS `drop_course_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drop_course_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int DEFAULT NULL,
  `course_code` varchar(20) DEFAULT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `handled_by_admin` int DEFAULT NULL,
  `request_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `type` enum('Retake','Extra','Skipped','Current') DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`),
  KEY `handled_by_admin` (`handled_by_admin`),
  CONSTRAINT `drop_course_requests_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `drop_course_requests_ibfk_2` FOREIGN KEY (`handled_by_admin`) REFERENCES `admin` (`admin_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drop_course_requests`
--

LOCK TABLES `drop_course_requests` WRITE;
/*!40000 ALTER TABLE `drop_course_requests` DISABLE KEYS */;
INSERT INTO `drop_course_requests` VALUES (8,3,'BCOR 200','rejected',NULL,'2025-06-01 16:06:42','Current'),(10,3,'BCOR 200','approved',NULL,'2025-06-01 19:28:10','Current'),(11,3,'BCOR 260','rejected',NULL,'2025-06-01 19:42:47','Current'),(12,3,'BCOR 230','rejected',NULL,'2025-06-01 19:43:17','Current'),(13,3,'BCOR 260','rejected',NULL,'2025-06-01 19:44:02','Current'),(14,3,'BCOR 210','rejected',NULL,'2025-06-01 19:44:23','Current'),(15,3,'BCOR 260','rejected',NULL,'2025-06-01 19:46:08','Current'),(16,3,'CS 220','pending',NULL,'2025-06-01 19:47:08','Current'),(17,3,'NBC 210','pending',NULL,'2025-06-01 20:07:20','Current'),(18,3,'BA 410','pending',NULL,'2025-06-21 20:50:03','Current');
/*!40000 ALTER TABLE `drop_course_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elective_group_requirements`
--

DROP TABLE IF EXISTS `elective_group_requirements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `elective_group_requirements` (
  `id` int NOT NULL AUTO_INCREMENT,
  `elective_group_number` int NOT NULL,
  `required_picks` int NOT NULL,
  `follows_major_pick` tinyint(1) DEFAULT '0',
  `related_to_course` varchar(80) DEFAULT NULL,
  `maximum_picks` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `elective_group_number` (`elective_group_number`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elective_group_requirements`
--

LOCK TABLES `elective_group_requirements` WRITE;
/*!40000 ALTER TABLE `elective_group_requirements` DISABLE KEYS */;
INSERT INTO `elective_group_requirements` VALUES (1,6,1,1,NULL,NULL),(2,1,1,1,NULL,NULL),(3,2,1,1,NULL,NULL),(4,3,1,1,NULL,NULL),(5,4,1,1,NULL,NULL),(6,7,2,1,'96,97,98,99,100',3),(7,5,1,1,NULL,1);
/*!40000 ALTER TABLE `elective_group_requirements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `forgiveness_requests`
--

DROP TABLE IF EXISTS `forgiveness_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `forgiveness_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `course_code` varchar(20) NOT NULL,
  `status` enum('pending','approved','rejected') NOT NULL DEFAULT 'pending',
  `handled_by_admin` int DEFAULT NULL,
  `request_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `handling_date` datetime DEFAULT NULL,
  `forgiven_grade` decimal(2,1) DEFAULT NULL,
  `new_grade` decimal(2,1) DEFAULT NULL,
  `academic_year` int NOT NULL,
  `add_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`),
  KEY `handled_by_admin` (`handled_by_admin`),
  KEY `course_code` (`course_code`),
  KEY `fk_forgiveness_add_course` (`add_id`),
  CONSTRAINT `forgiveness_requests_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`),
  CONSTRAINT `forgiveness_requests_ibfk_2` FOREIGN KEY (`handled_by_admin`) REFERENCES `admin` (`admin_id`),
  CONSTRAINT `forgiveness_requests_ibfk_3` FOREIGN KEY (`course_code`) REFERENCES `courses` (`course_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `forgiveness_requests`
--

LOCK TABLES `forgiveness_requests` WRITE;
/*!40000 ALTER TABLE `forgiveness_requests` DISABLE KEYS */;
/*!40000 ALTER TABLE `forgiveness_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grade_policy`
--

DROP TABLE IF EXISTS `grade_policy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grade_policy` (
  `id` int NOT NULL AUTO_INCREMENT,
  `letter_grade` varchar(3) DEFAULT NULL,
  `grade_point` decimal(2,1) DEFAULT NULL,
  `status` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grade_policy`
--

LOCK TABLES `grade_policy` WRITE;
/*!40000 ALTER TABLE `grade_policy` DISABLE KEYS */;
INSERT INTO `grade_policy` VALUES (1,'F',0.0,'failed'),(2,'D',1.0,'passed'),(3,'D+',1.3,'passed'),(4,'C-',1.7,'passed'),(5,'C',2.0,'passed'),(6,'C+',2.3,'passed'),(7,'B-',2.7,'passed'),(8,'B',3.0,'passed'),(9,'B+',3.3,'passed'),(10,'A-',3.7,'passed'),(11,'A',4.0,'passed'),(12,'P',NULL,'passed'),(13,'TC',NULL,'passed');
/*!40000 ALTER TABLE `grade_policy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `major_course_requirements`
--

DROP TABLE IF EXISTS `major_course_requirements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `major_course_requirements` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_code` varchar(10) NOT NULL,
  `course_name` varchar(100) NOT NULL,
  `weight` decimal(4,2) NOT NULL,
  `minimum_grade_point` decimal(3,2) DEFAULT NULL,
  `major_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_sgr_course` (`course_code`),
  KEY `major_id` (`major_id`),
  CONSTRAINT `fk_sgr_course` FOREIGN KEY (`course_code`) REFERENCES `courses` (`course_code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `major_course_requirements_ibfk_1` FOREIGN KEY (`major_id`) REFERENCES `majors` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `major_course_requirements`
--

LOCK TABLES `major_course_requirements` WRITE;
/*!40000 ALTER TABLE `major_course_requirements` DISABLE KEYS */;
INSERT INTO `major_course_requirements` VALUES (1,'BCOR 130','Financial Accounting',3.00,NULL,1),(2,'BCOR 225','Managerial Accounting',3.00,NULL,1),(3,'BCOR 110','Calculus for Business',3.00,NULL,2),(4,'BCOR 111','Linear Algebra for Business',3.00,NULL,2),(5,'BCOR 150','Probability & Statistics for Business I',3.00,NULL,2),(6,'BCOR 230','Business Optimization',3.00,NULL,2),(7,'BCOR 250','Probability and Statistics for Business II',3.00,NULL,2),(8,'BCOR 130','Financial Accounting',3.00,NULL,3),(9,'BCOR 150','Probability & Statistics for Business I',3.00,NULL,3),(10,'BCOR 250','Probability and Statistics for Business II',3.00,NULL,3),(11,'BCOR 260','Principles of Finance',3.00,NULL,3),(12,'BCOR 200','Introduction to Management of Information Systems (MIS)',3.00,NULL,4),(13,'CS 100','Algorithms and Initiation to Programming',3.00,NULL,4),(14,'CS 120','Database Design and Management',3.00,NULL,4),(15,'CS 200','Information System Analysis and Databases',3.00,NULL,4),(16,'CS 220','Advanced Web Development',3.00,NULL,4),(17,'BCOR 120','English Communication Skills',2.00,NULL,5),(18,'BCOR 150','Probability & Statistics for Business I',3.00,NULL,5),(19,'BCOR 210','Fundamentals of Marketing',3.00,2.00,5);
/*!40000 ALTER TABLE `major_course_requirements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `major_minor_requests`
--

DROP TABLE IF EXISTS `major_minor_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `major_minor_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `major` enum('ACCT','BA','FIN','IT','MRK','NONE') DEFAULT NULL,
  `second_major` enum('ACCT','BA','FIN','IT','MRK') DEFAULT NULL,
  `minor` enum('ACCT','BA','FIN','IT','MRK','IBE') DEFAULT NULL,
  `second_minor` enum('ACCT','BA','FIN','IT','MRK','IBE') DEFAULT NULL,
  `submission_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('pending','accepted','rejected') NOT NULL DEFAULT 'pending',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `major_minor_requests`
--

LOCK TABLES `major_minor_requests` WRITE;
/*!40000 ALTER TABLE `major_minor_requests` DISABLE KEYS */;
INSERT INTO `major_minor_requests` VALUES (3,4,'ACCT',NULL,'IBE',NULL,'2023-09-17 08:15:00','pending'),(4,5,'MRK',NULL,'IBE',NULL,'2023-09-18 13:20:00','pending'),(5,6,'FIN',NULL,'IT',NULL,'2023-09-19 15:30:00','pending'),(6,8,'BA','ACCT',NULL,NULL,'2023-09-20 09:10:00','pending'),(7,9,'IT',NULL,'FIN',NULL,'2023-09-21 10:25:00','pending'),(8,10,'NONE',NULL,NULL,NULL,'2023-09-22 12:40:00','pending'),(9,12,'MRK',NULL,'IT',NULL,'2023-09-23 14:55:00','pending'),(10,13,'FIN',NULL,'ACCT',NULL,'2023-09-24 08:05:00','pending'),(11,14,'IT','MRK',NULL,NULL,'2023-09-25 09:20:00','pending'),(12,16,'BA',NULL,'IBE',NULL,'2023-09-26 11:35:00','pending'),(13,17,'ACCT',NULL,'FIN',NULL,'2023-09-27 13:50:00','pending'),(14,18,'MRK',NULL,'BA',NULL,'2023-09-28 15:05:00','pending'),(15,19,'FIN',NULL,'MRK',NULL,'2023-09-29 08:15:00','pending'),(16,21,'IT',NULL,'BA',NULL,'2023-09-30 10:30:00','pending'),(17,22,'ACCT','FIN',NULL,NULL,'2023-10-01 12:45:00','pending'),(18,23,'FIN',NULL,'IBE',NULL,'2023-10-02 14:00:00','pending'),(19,24,'ACCT',NULL,'MRK',NULL,'2023-10-03 09:10:00','pending'),(20,26,'MRK',NULL,'IT',NULL,'2023-10-04 11:25:00','pending'),(21,27,'BA',NULL,'FIN',NULL,'2023-10-05 13:40:00','pending'),(22,28,'FIN',NULL,'ACCT',NULL,'2023-10-06 15:55:00','pending'),(23,29,'IT','BA',NULL,NULL,'2023-10-07 08:05:00','pending'),(24,31,'BA',NULL,'IBE',NULL,'2023-10-08 10:20:00','pending'),(25,32,'ACCT',NULL,'IBE',NULL,'2023-10-09 12:35:00','pending'),(26,33,'MRK',NULL,'FIN',NULL,'2023-10-10 14:50:00','pending'),(27,34,'FIN',NULL,'MRK',NULL,'2023-10-11 09:00:00','pending'),(28,36,'IT',NULL,'BA',NULL,'2023-10-12 11:15:00','pending'),(29,37,'ACCT','FIN',NULL,NULL,'2023-10-13 13:30:00','pending'),(30,38,'FIN',NULL,'ACCT',NULL,'2023-10-14 15:45:00','pending'),(31,39,'ACCT',NULL,'MRK',NULL,'2023-10-15 08:55:00','pending'),(32,41,'MRK',NULL,'IT',NULL,'2023-10-16 11:10:00','pending'),(33,42,'BA',NULL,'IBE',NULL,'2023-10-17 13:25:00','pending'),(34,43,'FIN',NULL,'IBE',NULL,'2023-10-18 15:40:00','pending'),(35,44,'IT','MRK',NULL,NULL,'2023-10-19 09:50:00','pending'),(36,46,'BA',NULL,'IBE',NULL,'2023-10-20 12:05:00','pending'),(37,47,'ACCT',NULL,'FIN',NULL,'2023-10-21 14:20:00','pending'),(38,48,'MRK',NULL,'BA',NULL,'2023-10-22 08:30:00','pending'),(39,49,'MRK',NULL,'BA',NULL,'2023-10-23 10:45:00','pending'),(52,3,'FIN',NULL,'BA',NULL,'2025-07-03 23:00:00','accepted');
/*!40000 ALTER TABLE `major_minor_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `major_minor_selection_window`
--

DROP TABLE IF EXISTS `major_minor_selection_window`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `major_minor_selection_window` (
  `id` int NOT NULL AUTO_INCREMENT,
  `status` enum('open','closed','scheduled') NOT NULL DEFAULT 'scheduled',
  `opened_by_admin` int DEFAULT NULL,
  `opened_at` timestamp NULL DEFAULT NULL,
  `start_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `closed_by_admin` int DEFAULT NULL,
  `closed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_opened_by_admin` (`opened_by_admin`),
  KEY `fk_closed_by_admin` (`closed_by_admin`),
  CONSTRAINT `fk_closed_by_admin` FOREIGN KEY (`closed_by_admin`) REFERENCES `admin` (`admin_id`),
  CONSTRAINT `fk_opened_by_admin` FOREIGN KEY (`opened_by_admin`) REFERENCES `admin` (`admin_id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `major_minor_selection_window`
--

LOCK TABLES `major_minor_selection_window` WRITE;
/*!40000 ALTER TABLE `major_minor_selection_window` DISABLE KEYS */;
INSERT INTO `major_minor_selection_window` VALUES (1,'closed',1,'2025-05-26 01:18:35','2025-05-27 02:18:00','2025-05-28 02:18:00',1,'2025-05-26 01:18:49'),(2,'closed',1,'2025-05-26 01:19:05','2025-05-26 02:18:00','2025-05-27 02:19:00',1,'2025-05-26 01:21:27'),(3,'closed',1,'2025-05-26 01:31:22','2025-05-26 02:31:00','2025-05-27 02:31:00',1,'2025-05-26 01:36:55'),(4,'closed',1,'2025-05-26 01:47:07','2025-05-26 04:47:00','2025-05-28 02:47:00',1,'2025-05-26 14:24:33'),(5,'closed',1,'2025-05-26 14:25:49','2025-05-26 15:25:00','2025-05-27 15:25:00',1,'2025-05-26 14:29:02'),(6,'closed',1,'2025-05-26 14:31:54','2025-05-26 15:31:00','2025-06-01 15:31:00',1,'2025-05-26 14:32:45'),(7,'closed',1,'2025-05-26 14:39:32','2025-05-27 15:39:00','2025-05-29 15:39:00',1,'2025-05-26 14:39:44'),(8,'closed',1,'2025-05-26 14:39:50','2025-05-26 15:39:00','2025-05-27 15:39:00',1,'2025-05-26 14:41:54'),(9,'closed',1,'2025-05-26 14:42:17','2025-05-26 15:42:00','2025-05-27 15:42:00',1,'2025-05-26 14:50:32'),(10,'closed',1,'2025-05-26 14:55:42','2025-05-26 15:55:00','2025-05-27 15:55:00',1,'2025-05-26 14:55:53'),(11,'closed',1,'2025-05-26 15:15:18','2025-05-26 16:15:00','2025-05-27 16:15:00',1,'2025-05-26 15:20:20'),(12,'closed',1,'2025-05-26 15:30:23','2025-05-26 16:30:00','2025-05-27 16:30:00',1,'2025-05-26 15:35:08'),(13,'closed',1,'2025-05-26 15:35:54','2025-05-26 16:35:00','2025-05-27 16:35:00',1,'2025-05-26 15:52:45'),(14,'closed',1,'2025-05-26 16:07:47','2025-05-26 17:07:00','2025-05-28 17:07:00',1,'2025-05-26 16:22:50'),(15,'closed',1,'2025-05-26 16:37:47','2025-05-26 17:37:00','2025-05-28 17:37:00',1,'2025-05-27 02:54:07'),(16,'closed',1,'2025-05-28 14:01:28','2025-05-28 15:01:00','2025-05-29 15:01:00',NULL,'2025-05-30 22:39:58'),(17,'closed',1,'2025-06-01 20:38:52','2025-06-01 21:38:00','2025-06-02 21:38:00',NULL,'2025-06-02 20:38:17'),(18,'closed',1,'2025-06-05 15:51:40','2025-06-05 16:51:00','2025-06-06 16:51:00',NULL,'2025-06-06 16:07:44'),(19,'closed',1,'2025-06-10 17:10:58','2025-06-10 18:10:00','2025-06-13 18:10:00',1,'2025-06-11 20:09:21'),(20,'closed',1,'2025-06-12 23:25:36','2025-06-13 00:25:00','2025-06-17 00:25:00',1,'2025-06-14 04:41:29'),(21,'closed',1,'2025-06-21 06:35:35','2025-06-21 07:35:00','2025-06-22 07:35:00',1,'2025-06-21 06:35:40'),(22,'closed',1,'2025-06-21 06:35:46','2025-06-22 07:35:00','2025-06-29 07:35:00',1,'2025-06-21 06:36:55'),(23,'closed',1,'2025-06-21 06:37:25','2025-06-21 07:37:00','2025-06-28 07:37:00',1,'2025-06-22 00:58:57'),(24,'closed',1,'2025-07-02 07:55:25','2025-07-02 08:55:00','2025-07-05 08:55:00',1,'2025-07-02 12:53:02'),(25,'closed',1,'2025-07-02 13:33:38','2025-07-02 14:33:00','2025-07-05 14:33:00',1,'2025-07-02 13:58:41'),(26,'closed',1,'2025-07-02 14:03:35','2025-07-02 15:03:00','2025-07-05 15:03:00',1,'2025-07-02 14:05:21'),(27,'closed',1,'2025-07-02 14:07:04','2025-07-02 15:07:00','2025-07-05 15:07:00',NULL,'2025-07-07 05:00:17');
/*!40000 ALTER TABLE `major_minor_selection_window` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `majors`
--

DROP TABLE IF EXISTS `majors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `majors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `major` varchar(10) DEFAULT NULL,
  `full_name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `short_name` (`major`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `majors`
--

LOCK TABLES `majors` WRITE;
/*!40000 ALTER TABLE `majors` DISABLE KEYS */;
INSERT INTO `majors` VALUES (1,'ACCT','Accounting'),(2,'BA','Business Analytics'),(3,'FIN','Finance'),(4,'IT','Information Technology'),(5,'MRK','Marketing');
/*!40000 ALTER TABLE `majors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `makeup_session`
--

DROP TABLE IF EXISTS `makeup_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `makeup_session` (
  `id` int NOT NULL AUTO_INCREMENT,
  `status` enum('scheduled','open','closed') NOT NULL,
  `open_date` datetime DEFAULT NULL,
  `opened_by_admin` int DEFAULT NULL,
  `close_date` datetime DEFAULT NULL,
  `closed_by_admin` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `opened_by_admin` (`opened_by_admin`),
  KEY `closed_by_admin` (`closed_by_admin`),
  CONSTRAINT `makeup_session_ibfk_1` FOREIGN KEY (`opened_by_admin`) REFERENCES `admin` (`admin_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `makeup_session_ibfk_2` FOREIGN KEY (`closed_by_admin`) REFERENCES `admin` (`admin_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `makeup_session`
--

LOCK TABLES `makeup_session` WRITE;
/*!40000 ALTER TABLE `makeup_session` DISABLE KEYS */;
INSERT INTO `makeup_session` VALUES (1,'closed','2025-06-06 05:07:52',1,NULL,NULL),(2,'closed','2025-06-07 03:10:00',1,'2025-06-08 03:10:00',1),(3,'closed','2025-06-26 02:14:00',1,'2025-06-27 02:14:00',NULL);
/*!40000 ALTER TABLE `makeup_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `minors`
--

DROP TABLE IF EXISTS `minors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `minors` (
  `id` int NOT NULL AUTO_INCREMENT,
  `minor` varchar(10) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `minors`
--

LOCK TABLES `minors` WRITE;
/*!40000 ALTER TABLE `minors` DISABLE KEYS */;
INSERT INTO `minors` VALUES (1,'ACCT','Accounting'),(2,'BA','Business Analytics'),(3,'FIN','Finance'),(4,'IT','Information Technology'),(5,'MRK','Marketing'),(6,'IBE','International Business Economics');
/*!40000 ALTER TABLE `minors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parameter_changes_log`
--

DROP TABLE IF EXISTS `parameter_changes_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parameter_changes_log` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `changed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `changed_by_admin` int DEFAULT NULL,
  `change_type` enum('system','student') DEFAULT NULL,
  `student_id` int DEFAULT NULL,
  `column_name` varchar(50) DEFAULT NULL,
  `old_value` text,
  `new_value` text,
  PRIMARY KEY (`log_id`),
  KEY `changed_by_admin` (`changed_by_admin`),
  CONSTRAINT `parameter_changes_log_ibfk_1` FOREIGN KEY (`changed_by_admin`) REFERENCES `admin` (`admin_id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parameter_changes_log`
--

LOCK TABLES `parameter_changes_log` WRITE;
/*!40000 ALTER TABLE `parameter_changes_log` DISABLE KEYS */;
INSERT INTO `parameter_changes_log` VALUES (1,'2025-05-25 13:16:49',1,'system',NULL,'min_gpa_acct','2.0','2.01'),(2,'2025-05-25 13:16:57',1,'system',NULL,'min_gpa_ba','2.0','2.01'),(3,'2025-05-25 13:16:57',1,'system',NULL,'min_gpa_fin','2.0','2.01'),(4,'2025-05-25 13:17:15',1,'system',NULL,'min_gpa_acct','2.01','2'),(5,'2025-05-25 13:17:15',1,'system',NULL,'min_gpa_ba','2.01','2'),(6,'2025-05-25 13:17:15',1,'system',NULL,'min_gpa_fin','2.01','2'),(7,'2025-05-25 13:18:59',1,'system',NULL,'min_cumulative_gpa','2.0','2.01'),(8,'2025-05-25 13:19:07',1,'system',NULL,'min_cumulative_gpa','2.01','2'),(9,'2025-05-25 13:55:48',1,'system',NULL,'min_credit_percentage_major','85.0','84'),(10,'2025-05-25 14:05:43',1,'system',NULL,'min_credit_percentage_major','84.0','85'),(11,'2025-05-25 14:07:06',1,'student',37,'min_credit_percentage_major',NULL,'2'),(12,'2025-05-25 14:07:34',1,'student',37,'min_credit_percentage_major','2.0',NULL),(13,'2025-05-25 14:07:49',1,'student',37,'min_credit_percentage_major',NULL,'1'),(14,'2025-05-25 14:08:04',1,'student',37,'min_credit_percentage_major','1.0',NULL),(15,'2025-05-25 14:11:43',1,'student',37,'min_credit_percentage_major',NULL,'2'),(16,'2025-05-25 14:11:55',1,'student',37,'min_credit_percentage_major','2.0',NULL),(17,'2025-05-25 17:32:17',1,'system',NULL,'max_probation_total','3','4'),(18,'2025-05-25 17:46:36',1,'student',31,'max_forgiveness_uses',NULL,'5'),(19,'2025-05-25 17:48:42',1,'system',NULL,'max_probation_total','4','5'),(20,'2025-05-25 17:48:45',1,'system',NULL,'max_probation_total','5','4'),(21,'2025-05-27 13:16:37',1,'student',3,'max_forgiveness_uses',NULL,'6'),(22,'2025-05-27 13:16:56',1,'student',3,'max_forgiveness_uses','6','0'),(23,'2025-05-27 13:21:14',1,'student',3,'max_forgiveness_uses','0','4'),(24,'2025-05-27 13:33:12',1,'student',3,'max_forgiveness_uses','4','0'),(25,'2025-05-27 13:35:06',1,'student',3,'max_forgiveness_uses','0','4'),(26,'2025-06-10 22:34:49',1,'student',3,'max_courses_per_semester',NULL,'8'),(27,'2025-06-10 22:37:36',1,'student',3,'max_courses_per_semester','8',NULL),(28,'2025-06-10 23:30:29',1,'student',3,'min_gpa_fin',NULL,'1'),(29,'2025-06-10 23:30:38',1,'student',3,'min_gpa_fin','1.0',NULL),(30,'2025-06-11 20:44:03',1,'system',NULL,'minimum_forgive_grade','1.7','2'),(31,'2025-06-11 20:50:12',1,'system',NULL,'minimum_forgive_grade','2.0','1.7'),(32,'2025-06-14 00:12:24',1,'student',3,'min_gpa_acct',NULL,'0.01'),(33,'2025-06-14 00:21:52',1,'student',3,'min_gpa_acct','0.01',NULL);
/*!40000 ALTER TABLE `parameter_changes_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `priority_preferences`
--

DROP TABLE IF EXISTS `priority_preferences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `priority_preferences` (
  `student_id` int DEFAULT NULL,
  `priority` char(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `priority_preferences`
--

LOCK TABLES `priority_preferences` WRITE;
/*!40000 ALTER TABLE `priority_preferences` DISABLE KEYS */;
INSERT INTO `priority_preferences` VALUES (3,'a');
/*!40000 ALTER TABLE `priority_preferences` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `professor_preferences`
--

DROP TABLE IF EXISTS `professor_preferences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `professor_preferences` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `course_code` varchar(20) DEFAULT NULL,
  `session_type` int NOT NULL COMMENT '1 for lecture, 2 for tutorial',
  `professor_index` int DEFAULT NULL,
  `ranked` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_preference` (`student_id`,`course_code`,`session_type`,`professor_index`),
  KEY `student_id` (`student_id`),
  KEY `course_id` (`course_code`,`session_type`,`professor_index`)
) ENGINE=InnoDB AUTO_INCREMENT=141 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `professor_preferences`
--

LOCK TABLES `professor_preferences` WRITE;
/*!40000 ALTER TABLE `professor_preferences` DISABLE KEYS */;
INSERT INTO `professor_preferences` VALUES (121,3,'BCOR 140',1,1,1,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(122,3,'BCOR 140',1,3,2,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(123,3,'BCOR 140',1,4,3,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(124,3,'BCOR 140',2,1,1,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(125,3,'BCOR 140',2,2,2,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(126,3,'BCOR 200',1,1,1,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(127,3,'BCOR 200',1,2,2,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(128,3,'BCOR 200',1,3,3,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(129,3,'BCOR 200',1,4,4,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(130,3,'BCOR 210',1,1,1,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(131,3,'BCOR 210',1,2,2,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(132,3,'BCOR 210',1,3,3,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(133,3,'BCOR 230',1,1,1,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(134,3,'BCOR 230',2,2,1,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(135,3,'BCOR 230',2,1,2,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(136,3,'BCOR 260',1,1,1,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(137,3,'NBC 210',1,1,1,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(138,3,'NBC 210',1,2,2,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(139,3,'NBC 210',1,3,3,'2025-07-03 10:26:05','2025-07-03 10:26:05'),(140,3,'NBC 210',1,4,4,'2025-07-03 10:26:05','2025-07-03 10:26:05');
/*!40000 ALTER TABLE `professor_preferences` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registration_config`
--

DROP TABLE IF EXISTS `registration_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registration_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `status` enum('open','closed','scheduled') NOT NULL DEFAULT 'closed',
  `opened_by_admin` int NOT NULL,
  `opened_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `start_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `closed_by_admin` int DEFAULT NULL,
  `closed_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `opened_by_admin` (`opened_by_admin`),
  KEY `closed_by_admin` (`closed_by_admin`),
  CONSTRAINT `registration_config_ibfk_1` FOREIGN KEY (`opened_by_admin`) REFERENCES `admin` (`admin_id`),
  CONSTRAINT `registration_config_ibfk_2` FOREIGN KEY (`closed_by_admin`) REFERENCES `admin` (`admin_id`)
) ENGINE=InnoDB AUTO_INCREMENT=236 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registration_config`
--

LOCK TABLES `registration_config` WRITE;
/*!40000 ALTER TABLE `registration_config` DISABLE KEYS */;
INSERT INTO `registration_config` VALUES (1,'closed',1,'2025-05-26 01:54:34','2025-05-27 02:54:00','2025-05-28 02:54:00',1,'2025-05-26 01:54:37'),(2,'closed',1,'2025-05-26 01:54:49','2025-05-28 02:54:00','2025-05-30 02:54:00',1,'2025-05-26 02:02:58'),(3,'closed',1,'2025-05-30 23:45:51','2025-05-31 00:45:00','2025-06-01 00:45:00',1,'2025-05-31 00:49:47'),(4,'closed',1,'2025-05-31 00:51:01','2025-06-01 01:49:00','2025-06-03 01:50:00',1,'2025-05-31 01:13:18'),(5,'closed',1,'2025-05-31 01:13:25','2025-05-31 02:13:00','2025-06-01 02:13:00',1,'2025-05-31 01:32:23'),(6,'closed',1,'2025-05-31 01:32:45','2025-06-01 02:32:00','2025-06-07 02:32:00',1,'2025-05-31 01:32:59'),(7,'closed',1,'2025-05-31 01:33:09','2025-05-31 02:33:00','2025-06-01 02:33:00',1,'2025-05-31 01:33:22'),(8,'closed',1,'2025-05-31 01:51:35','2025-06-01 02:51:00','2025-06-04 02:51:00',1,'2025-05-31 01:52:46'),(9,'closed',1,'2025-05-31 01:52:52','2025-05-31 02:52:00','2025-06-01 02:52:00',1,'2025-05-31 02:01:13'),(10,'closed',1,'2025-05-31 02:04:10','2025-05-31 03:04:00','2025-05-31 03:06:00',1,'2025-05-31 02:06:05'),(11,'closed',1,'2025-05-31 02:12:25','2025-05-31 03:12:00','2025-05-31 03:13:00',1,'2025-05-31 02:13:00'),(12,'closed',1,'2025-05-31 02:13:41','2025-05-31 03:13:00','2025-05-31 03:14:00',1,'2025-05-31 02:14:00'),(13,'closed',1,'2025-05-31 02:14:40','2025-05-31 03:14:00','2025-06-01 03:14:00',1,'2025-05-31 03:09:10'),(14,'closed',1,'2025-05-31 03:32:07','2025-05-31 04:31:00','2025-05-31 04:33:00',1,'2025-05-31 03:33:00'),(15,'closed',1,'2025-05-31 15:40:14','2025-05-31 16:40:00','2025-06-01 16:40:00',1,'2025-05-31 15:44:49'),(16,'closed',1,'2025-05-31 15:45:06','2025-05-31 16:45:00','2025-06-01 16:45:00',1,'2025-06-01 12:10:15'),(17,'closed',1,'2025-06-01 12:26:17','2025-06-01 13:26:00','2025-06-02 13:26:00',1,'2025-06-01 12:26:33'),(18,'closed',1,'2025-06-01 12:27:31','2025-06-01 13:27:00','2025-06-02 13:27:00',1,'2025-06-01 12:48:27'),(19,'closed',1,'2025-06-01 13:22:47','2025-06-01 14:22:00','2025-06-02 14:22:00',1,'2025-06-01 13:22:54'),(20,'closed',1,'2025-06-01 13:59:58','2025-06-01 14:59:00','2025-06-02 14:59:00',1,'2025-06-01 14:01:08'),(21,'closed',1,'2025-06-01 14:37:12','2025-06-01 15:37:00','2025-06-02 15:37:00',1,'2025-06-01 14:38:15'),(22,'closed',1,'2025-06-01 14:40:00','2025-06-01 15:39:00','2025-06-03 15:39:00',1,'2025-06-01 14:40:27'),(23,'closed',1,'2025-06-01 20:34:53','2025-06-01 21:34:00','2025-06-02 21:34:00',1,'2025-06-01 20:36:47'),(24,'closed',1,'2025-06-01 20:37:40','2025-06-01 21:37:00','2025-06-02 21:37:00',1,'2025-06-01 20:41:11'),(25,'closed',1,'2025-06-01 20:41:20','2025-06-01 21:41:00','2025-06-02 21:41:00',1,'2025-06-02 00:31:44'),(26,'closed',1,'2025-06-02 00:31:55','2025-06-02 01:31:00','2025-06-03 01:31:00',1,'2025-06-02 01:49:27'),(27,'closed',1,'2025-06-02 01:50:30','2025-06-02 02:50:00','2025-06-03 02:50:00',1,'2025-06-02 01:52:08'),(28,'closed',1,'2025-06-02 01:52:14','2025-06-02 02:52:00','2025-06-03 02:52:00',1,'2025-06-02 01:52:59'),(29,'closed',1,'2025-06-02 01:53:05','2025-06-02 02:53:00','2025-06-04 02:53:00',1,'2025-06-02 01:54:03'),(30,'closed',1,'2025-06-02 01:54:13','2025-06-02 02:54:00','2025-06-03 02:54:00',1,'2025-06-02 01:54:58'),(31,'closed',1,'2025-06-02 01:55:06','2025-06-02 02:55:00','2025-06-03 02:55:00',1,'2025-06-02 04:48:41'),(32,'closed',1,'2025-06-02 04:48:59','2025-06-02 05:48:00','2025-06-03 05:48:00',1,'2025-06-02 19:56:16'),(33,'closed',1,'2025-06-02 19:56:24','2025-06-02 20:56:00','2025-06-03 20:56:00',1,'2025-06-02 19:57:24'),(34,'closed',1,'2025-06-02 19:57:30','2025-06-02 20:57:00','2025-06-03 20:57:00',NULL,'2025-06-03 19:57:15'),(35,'closed',1,'2025-06-04 19:23:25','2025-06-04 20:23:00','2025-06-13 20:23:00',1,'2025-06-04 21:02:50'),(36,'closed',1,'2025-06-04 21:07:57','2025-06-04 22:07:00','2025-06-26 22:07:00',1,'2025-06-04 21:30:36'),(37,'closed',1,'2025-06-04 21:30:47','2025-06-04 22:30:00','2025-06-06 22:30:00',1,'2025-06-04 22:21:50'),(38,'closed',1,'2025-06-04 22:21:59','2025-06-04 23:21:00','2025-06-05 23:21:00',1,'2025-06-04 22:37:38'),(39,'closed',1,'2025-06-04 22:38:04','2025-06-04 23:37:00','2025-06-06 23:38:00',1,'2025-06-04 22:54:59'),(40,'closed',1,'2025-06-04 22:55:05','2025-06-04 23:55:00','2025-06-06 23:55:00',1,'2025-06-04 23:06:32'),(41,'closed',1,'2025-06-04 23:06:44','2025-06-05 00:06:00','2025-06-06 00:06:00',1,'2025-06-04 23:16:46'),(42,'closed',1,'2025-06-04 23:16:51','2025-06-05 00:16:00','2025-06-07 00:16:00',1,'2025-06-04 23:17:40'),(43,'closed',1,'2025-06-04 23:19:08','2025-06-05 00:19:00','2025-06-06 00:19:00',1,'2025-06-04 23:19:22'),(44,'closed',1,'2025-06-04 23:19:31','2025-06-05 00:19:00','2025-06-06 00:19:00',1,'2025-06-04 23:19:58'),(45,'closed',1,'2025-06-04 23:20:04','2025-06-05 00:20:00','2025-06-06 00:20:00',1,'2025-06-04 23:26:25'),(46,'closed',1,'2025-06-04 23:26:46','2025-06-05 00:26:00','2025-06-06 00:26:00',1,'2025-06-04 23:27:13'),(47,'closed',1,'2025-06-04 23:27:31','2025-06-05 00:27:00','2025-06-14 00:27:00',1,'2025-06-04 23:27:40'),(48,'closed',1,'2025-06-04 23:27:48','2025-06-05 00:27:00','2025-06-07 00:27:00',1,'2025-06-04 23:27:59'),(49,'closed',1,'2025-06-04 23:28:05','2025-06-05 00:28:00','2025-06-21 00:28:00',1,'2025-06-04 23:35:06'),(50,'closed',1,'2025-06-04 23:35:33','2025-06-05 00:35:00','2025-06-06 00:35:00',1,'2025-06-04 23:35:47'),(51,'closed',1,'2025-06-04 23:35:54','2025-06-05 00:35:00','2025-06-06 00:35:00',1,'2025-06-04 23:36:21'),(52,'closed',1,'2025-06-04 23:36:28','2025-06-05 00:36:00','2025-06-06 00:36:00',1,'2025-06-04 23:39:42'),(53,'closed',1,'2025-06-04 23:40:05','2025-06-05 00:40:00','2025-06-14 00:40:00',1,'2025-06-04 23:40:47'),(54,'closed',1,'2025-06-04 23:40:52','2025-06-05 00:40:00','2025-06-13 00:40:00',1,'2025-06-04 23:42:11'),(55,'closed',1,'2025-06-04 23:42:16','2025-06-05 00:42:00','2025-06-06 00:42:00',1,'2025-06-04 23:52:50'),(56,'closed',1,'2025-06-04 23:55:47','2025-06-05 00:55:00','2025-06-13 00:55:00',1,'2025-06-04 23:57:31'),(57,'closed',1,'2025-06-04 23:57:44','2025-06-05 00:57:00','2025-06-25 00:57:00',1,'2025-06-04 23:58:58'),(58,'closed',1,'2025-06-04 23:59:03','2025-06-05 00:59:00','2025-06-14 00:59:00',1,'2025-06-05 00:11:33'),(59,'closed',1,'2025-06-05 00:12:04','2025-06-05 01:12:00','2025-06-28 01:12:00',1,'2025-06-05 00:12:40'),(60,'closed',1,'2025-06-05 00:13:09','2025-06-05 01:13:00','2025-06-28 01:13:00',1,'2025-06-05 00:14:40'),(61,'closed',1,'2025-06-05 00:15:49','2025-06-05 01:15:00','2025-06-22 01:15:00',1,'2025-06-05 00:16:01'),(62,'closed',1,'2025-06-05 00:16:07','2025-06-05 01:16:00','2025-06-06 01:16:00',1,'2025-06-05 00:17:15'),(63,'closed',1,'2025-06-05 01:08:55','2025-06-05 02:08:00','2025-06-12 02:08:00',1,'2025-06-05 01:15:36'),(64,'closed',1,'2025-06-05 01:16:41','2025-06-05 02:16:00','2025-06-06 02:16:00',1,'2025-06-05 01:21:09'),(65,'closed',1,'2025-06-05 01:21:15','2025-06-05 02:21:00','2025-06-19 02:21:00',1,'2025-06-05 01:22:13'),(66,'closed',1,'2025-06-05 01:31:37','2025-06-05 02:31:00','2025-06-21 02:31:00',1,'2025-06-05 01:33:05'),(67,'closed',1,'2025-06-05 01:33:11','2025-06-05 02:33:00','2025-06-13 02:33:00',1,'2025-06-05 01:33:26'),(68,'closed',1,'2025-06-05 01:33:34','2025-06-05 02:33:00','2025-06-06 02:33:00',1,'2025-06-05 01:34:35'),(69,'closed',1,'2025-06-05 01:35:13','2025-06-05 02:35:00','2025-06-06 02:35:00',1,'2025-06-05 01:36:49'),(70,'closed',1,'2025-06-05 01:36:59','2025-06-05 02:36:00','2025-06-13 02:36:00',1,'2025-06-05 15:04:20'),(71,'closed',1,'2025-06-05 15:05:15','2025-06-05 16:05:00','2025-06-06 16:05:00',1,'2025-06-05 15:06:32'),(72,'closed',1,'2025-06-05 15:06:45','2025-06-05 16:06:00','2025-06-20 16:06:00',1,'2025-06-05 15:06:58'),(73,'closed',1,'2025-06-05 15:07:12','2025-06-05 16:07:00','2025-06-06 16:07:00',1,'2025-06-05 15:12:05'),(74,'closed',1,'2025-06-05 15:12:15','2025-06-05 16:12:00','2025-06-13 16:12:00',1,'2025-06-05 15:52:25'),(75,'closed',1,'2025-06-05 15:52:31','2025-06-05 16:52:00','2025-06-12 16:52:00',1,'2025-06-05 15:53:10'),(76,'closed',1,'2025-06-05 15:53:15','2025-06-05 16:53:00','2025-06-14 16:53:00',1,'2025-06-05 18:25:58'),(77,'closed',1,'2025-06-05 18:26:04','2025-06-05 19:26:00','2025-06-06 19:26:00',1,'2025-06-05 18:29:36'),(78,'closed',1,'2025-06-05 18:29:42','2025-06-05 19:29:00','2025-06-10 19:29:00',1,'2025-06-06 01:57:50'),(79,'closed',1,'2025-06-06 02:04:53','2025-06-06 03:04:00','2025-06-12 03:04:00',1,'2025-06-06 02:04:55'),(80,'closed',1,'2025-06-06 04:04:34','2025-06-06 05:04:00','2025-06-07 05:04:00',1,'2025-06-06 04:51:46'),(81,'closed',1,'2025-06-06 16:09:27','2025-06-06 17:09:00','2025-06-07 17:09:00',1,'2025-06-06 16:14:22'),(82,'closed',1,'2025-06-06 16:14:38','2025-06-06 17:14:00','2025-06-07 17:14:00',1,'2025-06-06 16:15:44'),(83,'closed',1,'2025-06-06 16:15:51','2025-06-06 17:15:00','2025-06-07 17:15:00',1,'2025-06-06 16:17:20'),(84,'closed',1,'2025-06-06 16:17:29','2025-06-06 17:17:00','2025-06-07 17:17:00',1,'2025-06-07 03:06:14'),(85,'closed',1,'2025-06-07 03:06:25','2025-06-07 04:06:00','2025-06-08 04:06:00',1,'2025-06-07 03:06:43'),(86,'closed',1,'2025-06-07 03:06:52','2025-06-07 04:06:00','2025-06-08 04:06:00',1,'2025-06-07 03:09:07'),(87,'closed',1,'2025-06-07 03:09:34','2025-06-07 04:09:00','2025-06-08 04:09:00',1,'2025-06-07 03:10:03'),(88,'closed',1,'2025-06-07 03:10:25','2025-06-07 04:10:00','2025-06-08 04:10:00',1,'2025-06-07 03:10:38'),(89,'closed',1,'2025-06-07 03:47:06','2025-06-07 04:47:00','2025-06-13 04:47:00',1,'2025-06-07 03:57:10'),(90,'closed',1,'2025-06-07 03:57:24','2025-06-07 04:57:00','2025-06-08 04:57:00',1,'2025-06-07 22:33:11'),(91,'closed',1,'2025-06-07 22:33:37','2025-06-07 23:33:00','2025-06-08 23:33:00',1,'2025-06-07 22:34:42'),(92,'closed',1,'2025-06-07 22:38:49','2025-06-07 23:38:00','2025-06-08 23:38:00',1,'2025-06-07 22:40:34'),(93,'closed',1,'2025-06-07 22:41:20','2025-06-07 23:41:00','2025-06-08 23:41:00',1,'2025-06-07 22:41:40'),(94,'closed',1,'2025-06-07 22:41:52','2025-06-07 23:41:00','2025-06-08 23:41:00',1,'2025-06-07 22:43:43'),(95,'closed',1,'2025-06-07 22:44:26','2025-06-07 23:44:00','2025-06-08 23:44:00',1,'2025-06-07 23:09:44'),(96,'closed',1,'2025-06-07 23:10:03','2025-06-08 00:09:00','2025-06-20 00:10:00',1,'2025-06-07 23:10:25'),(97,'closed',1,'2025-06-07 23:10:32','2025-06-08 00:10:00','2025-06-15 00:10:00',1,'2025-06-07 23:20:49'),(98,'closed',1,'2025-06-07 23:20:56','2025-06-08 00:20:00','2025-06-14 00:20:00',1,'2025-06-07 23:21:28'),(99,'closed',1,'2025-06-07 23:35:53','2025-06-08 00:35:00','2025-06-14 00:35:00',1,'2025-06-07 23:36:53'),(100,'closed',1,'2025-06-07 23:37:12','2025-06-08 00:37:00','2025-06-10 00:37:00',1,'2025-06-07 23:46:05'),(101,'closed',1,'2025-06-07 23:49:08','2025-06-08 00:49:00','2025-06-20 00:49:00',1,'2025-06-07 23:49:13'),(102,'closed',1,'2025-06-07 23:49:20','2025-06-08 00:49:00','2025-06-20 00:49:00',1,'2025-06-07 23:49:30'),(103,'closed',1,'2025-06-07 23:49:39','2025-06-08 00:49:00','2025-06-10 00:49:00',NULL,'2025-06-10 17:07:19'),(104,'closed',1,'2025-06-10 17:10:39','2025-06-10 18:10:00','2025-06-11 18:10:00',1,'2025-06-10 22:31:49'),(105,'closed',1,'2025-06-10 22:31:56','2025-06-10 23:31:00','2025-06-11 23:31:00',1,'2025-06-10 22:32:22'),(106,'closed',1,'2025-06-10 22:32:29','2025-06-10 23:32:00','2025-06-21 23:32:00',1,'2025-06-10 22:52:34'),(107,'closed',1,'2025-06-10 22:52:59','2025-06-10 23:52:00','2025-06-13 23:52:00',1,'2025-06-11 01:30:46'),(108,'closed',1,'2025-06-11 01:33:09','2025-06-11 02:33:00','2025-06-18 02:33:00',1,'2025-06-11 01:35:43'),(109,'closed',1,'2025-06-11 01:35:52','2025-06-12 02:35:00','2025-06-13 02:35:00',1,'2025-06-11 01:35:56'),(110,'closed',1,'2025-06-11 01:36:01','2025-06-11 02:35:00','2025-06-18 02:36:00',1,'2025-06-11 16:53:28'),(111,'closed',1,'2025-06-11 16:53:42','2025-06-11 17:53:00','2025-06-28 17:53:00',1,'2025-06-11 17:50:05'),(112,'closed',1,'2025-06-11 17:53:47','2025-06-11 18:53:00','2025-07-02 18:53:00',1,'2025-06-12 05:02:58'),(113,'closed',1,'2025-06-12 05:03:15','2025-06-12 06:03:00','2025-06-20 06:03:00',1,'2025-06-12 15:03:00'),(114,'closed',1,'2025-06-12 15:03:43','2025-06-12 16:03:00','2025-06-21 16:03:00',1,'2025-06-12 15:05:06'),(115,'closed',1,'2025-06-12 15:05:16','2025-06-12 16:05:00','2025-06-18 16:05:00',1,'2025-06-12 15:08:41'),(116,'closed',1,'2025-06-12 15:10:08','2025-06-12 16:10:00','2025-06-20 16:10:00',1,'2025-06-12 15:11:08'),(117,'closed',1,'2025-06-12 16:18:02','2025-06-12 17:17:00','2025-06-28 17:18:00',1,'2025-06-12 16:18:38'),(118,'closed',1,'2025-06-12 16:18:53','2025-06-12 17:18:00','2025-06-15 17:18:00',1,'2025-06-12 16:19:30'),(119,'closed',1,'2025-06-12 16:19:42','2025-06-12 17:19:00','2025-06-18 17:19:00',1,'2025-06-12 16:20:57'),(120,'closed',1,'2025-06-12 16:21:17','2025-06-12 17:21:00','2025-06-20 17:21:00',1,'2025-06-12 16:22:00'),(121,'closed',1,'2025-06-12 16:22:44','2025-06-12 17:22:00','2025-06-19 17:22:00',1,'2025-06-12 16:24:16'),(122,'closed',1,'2025-06-12 16:24:24','2025-06-12 17:24:00','2025-06-21 17:24:00',1,'2025-06-12 16:24:52'),(123,'closed',1,'2025-06-12 16:25:38','2025-06-12 17:25:00','2025-06-21 17:25:00',1,'2025-06-12 16:25:53'),(124,'closed',1,'2025-06-12 16:34:28','2025-06-12 17:34:00','2025-06-20 17:34:00',1,'2025-06-12 16:34:43'),(125,'closed',1,'2025-06-12 16:35:05','2025-06-12 17:35:00','2025-06-13 17:35:00',1,'2025-06-12 16:38:13'),(126,'closed',1,'2025-06-12 16:38:46','2025-06-12 17:38:00','2025-07-03 17:38:00',1,'2025-06-12 16:38:57'),(127,'closed',1,'2025-06-12 16:39:41','2025-06-12 17:39:00','2025-06-15 17:39:00',1,'2025-06-12 16:40:46'),(128,'closed',1,'2025-06-12 16:40:53','2025-06-12 17:40:00','2025-06-22 17:40:00',1,'2025-06-12 16:42:14'),(129,'closed',1,'2025-06-12 16:43:09','2025-06-12 17:43:00','2025-06-13 17:43:00',1,'2025-06-12 16:47:21'),(130,'closed',1,'2025-06-12 16:47:27','2025-06-12 17:47:00','2025-06-13 17:47:00',1,'2025-06-12 16:51:55'),(131,'closed',1,'2025-06-12 16:52:10','2025-06-12 17:52:00','2025-06-13 17:52:00',1,'2025-06-12 17:15:15'),(132,'closed',1,'2025-06-12 17:17:07','2025-06-12 18:17:00','2025-06-13 18:17:00',1,'2025-06-12 17:17:19'),(133,'closed',1,'2025-06-12 17:17:29','2025-06-12 18:17:00','2025-06-13 18:17:00',1,'2025-06-12 17:21:44'),(134,'closed',1,'2025-06-12 17:23:01','2025-06-12 18:22:00','2025-06-14 18:23:00',1,'2025-06-12 17:23:55'),(135,'closed',1,'2025-06-12 17:24:04','2025-06-12 18:24:00','2025-06-13 18:24:00',1,'2025-06-12 17:24:13'),(136,'closed',1,'2025-06-12 17:24:19','2025-06-12 18:24:00','2025-06-28 18:24:00',1,'2025-06-12 17:24:30'),(137,'closed',1,'2025-06-12 17:55:34','2025-06-12 18:55:00','2025-06-22 18:55:00',1,'2025-06-12 17:56:38'),(138,'closed',1,'2025-06-12 18:27:25','2025-06-12 19:27:00','2025-06-21 19:27:00',1,'2025-06-12 18:33:35'),(139,'closed',1,'2025-06-12 18:34:06','2025-06-12 19:34:00','2025-06-20 19:34:00',1,'2025-06-12 18:46:07'),(140,'closed',1,'2025-06-12 19:00:59','2025-06-12 20:00:00','2025-06-28 20:00:00',1,'2025-06-12 19:15:05'),(141,'closed',1,'2025-06-12 19:15:51','2025-06-12 20:15:00','2025-06-21 20:15:00',1,'2025-06-12 19:30:58'),(142,'closed',1,'2025-06-12 19:31:44','2025-06-12 20:31:00','2025-06-13 20:31:00',1,'2025-06-12 19:43:36'),(143,'closed',1,'2025-06-12 19:44:34','2025-06-12 20:44:00','2025-06-13 20:44:00',1,'2025-06-12 20:04:00'),(144,'closed',1,'2025-06-12 20:04:29','2025-06-12 21:04:00','2025-06-15 21:04:00',1,'2025-06-12 20:05:58'),(145,'closed',1,'2025-06-12 20:06:05','2025-06-12 21:06:00','2025-06-15 21:06:00',1,'2025-06-12 20:06:17'),(146,'closed',1,'2025-06-12 20:06:23','2025-06-12 21:06:00','2025-06-14 21:06:00',1,'2025-06-12 20:06:37'),(147,'closed',1,'2025-06-12 20:06:44','2025-06-12 21:06:00','2025-06-14 21:06:00',1,'2025-06-12 20:33:52'),(148,'closed',1,'2025-06-12 20:34:07','2025-06-12 21:34:00','2025-06-13 21:34:00',1,'2025-06-12 20:34:40'),(149,'closed',1,'2025-06-12 20:34:47','2025-06-12 21:34:00','2025-06-14 21:34:00',1,'2025-06-12 20:36:29'),(150,'closed',1,'2025-06-12 20:36:40','2025-06-12 21:36:00','2025-06-26 21:36:00',1,'2025-06-12 21:23:30'),(151,'closed',1,'2025-06-12 23:25:04','2025-06-13 00:24:00','2025-06-28 00:25:00',1,'2025-06-12 23:55:31'),(152,'closed',1,'2025-06-12 23:59:52','2025-06-13 00:59:00','2025-06-22 00:59:00',1,'2025-06-13 00:00:05'),(153,'closed',1,'2025-06-13 00:08:13','2025-06-13 01:08:00','2025-06-28 01:08:00',1,'2025-06-13 22:37:05'),(154,'closed',1,'2025-06-13 22:38:11','2025-06-13 23:38:00','2025-06-15 23:38:00',1,'2025-06-13 22:54:16'),(155,'closed',1,'2025-06-13 22:54:27','2025-06-13 23:54:00','2025-06-22 23:54:00',1,'2025-06-13 23:12:10'),(156,'closed',1,'2025-06-13 23:12:20','2025-06-14 00:12:00','2025-06-17 00:12:00',1,'2025-06-13 23:14:21'),(157,'closed',1,'2025-06-13 23:15:16','2025-06-14 00:15:00','2025-06-29 00:15:00',1,'2025-06-13 23:15:48'),(158,'closed',1,'2025-06-13 23:16:19','2025-06-14 00:16:00','2025-06-21 00:16:00',1,'2025-06-13 23:17:09'),(159,'closed',1,'2025-06-13 23:17:19','2025-06-14 00:17:00','2025-06-22 00:17:00',1,'2025-06-13 23:18:20'),(160,'closed',1,'2025-06-13 23:18:30','2025-06-14 00:18:00','2025-06-28 00:18:00',1,'2025-06-13 23:44:18'),(161,'closed',1,'2025-06-13 23:45:32','2025-06-14 00:45:00','2025-06-28 00:45:00',1,'2025-06-13 23:47:05'),(162,'closed',1,'2025-06-13 23:47:18','2025-06-14 00:47:00','2025-06-21 00:47:00',1,'2025-06-14 04:42:08'),(163,'closed',1,'2025-06-14 04:42:23','2025-06-14 05:42:00','2025-06-28 05:42:00',1,'2025-06-14 04:47:51'),(164,'closed',1,'2025-06-14 04:48:00','2025-06-14 05:47:00','2025-06-15 05:47:00',1,'2025-06-14 04:48:30'),(165,'closed',1,'2025-06-14 04:49:02','2025-06-14 05:48:00','2025-06-21 05:49:00',1,'2025-06-14 22:05:32'),(166,'closed',1,'2025-06-14 22:06:44','2025-06-14 23:06:00','2025-06-15 23:06:00',1,'2025-06-14 22:07:59'),(167,'closed',1,'2025-06-14 22:08:10','2025-06-14 23:08:00','2025-06-15 23:08:00',1,'2025-06-14 22:08:59'),(168,'closed',1,'2025-06-14 22:09:22','2025-06-14 23:09:00','2025-06-25 23:09:00',1,'2025-06-14 22:10:51'),(169,'closed',1,'2025-06-14 22:11:00','2025-06-14 23:10:00','2025-06-22 23:10:00',1,'2025-06-20 04:59:27'),(170,'closed',1,'2025-06-20 05:00:14','2025-06-20 06:00:00','2025-06-21 06:00:00',1,'2025-06-20 05:55:16'),(171,'closed',1,'2025-06-20 05:57:07','2025-06-20 06:57:00','2025-06-28 06:57:00',1,'2025-06-20 21:06:22'),(172,'closed',1,'2025-06-20 22:31:30','2025-06-20 23:31:00','2025-06-21 23:31:00',1,'2025-06-20 22:31:37'),(173,'closed',1,'2025-06-20 22:31:45','2025-06-20 23:31:00','2025-06-29 23:31:00',1,'2025-06-20 23:04:25'),(174,'closed',1,'2025-06-20 23:04:56','2025-06-21 00:04:00','2025-06-29 00:04:00',1,'2025-06-20 23:15:47'),(175,'closed',1,'2025-06-20 23:15:54','2025-06-21 00:15:00','2025-06-29 00:15:00',1,'2025-06-20 23:24:16'),(176,'closed',1,'2025-06-20 23:24:22','2025-06-21 00:24:00','2025-06-29 00:24:00',1,'2025-06-20 23:24:58'),(177,'closed',1,'2025-06-20 23:25:11','2025-06-21 00:25:00','2025-06-29 00:25:00',1,'2025-06-20 23:26:39'),(178,'closed',1,'2025-06-20 23:26:49','2025-06-21 00:26:00','2025-06-29 00:26:00',1,'2025-06-21 01:48:35'),(179,'closed',1,'2025-06-21 01:48:50','2025-06-21 02:48:00','2025-06-29 02:48:00',1,'2025-06-21 02:06:37'),(180,'closed',1,'2025-06-21 02:07:12','2025-06-21 03:07:00','2025-06-28 03:07:00',1,'2025-06-21 02:07:36'),(181,'closed',1,'2025-06-21 02:14:34','2025-06-21 03:14:00','2025-06-22 03:14:00',1,'2025-06-21 02:14:55'),(182,'closed',1,'2025-06-21 02:15:07','2025-06-21 03:15:00','2025-06-22 03:15:00',1,'2025-06-21 02:16:07'),(183,'closed',1,'2025-06-21 02:20:15','2025-06-21 03:20:00','2025-08-03 03:20:00',1,'2025-06-21 02:23:31'),(184,'closed',1,'2025-06-21 02:23:39','2025-06-21 03:23:00','2025-06-22 03:23:00',1,'2025-06-21 02:23:47'),(185,'closed',1,'2025-06-21 02:23:55','2025-06-21 03:23:00','2025-06-22 03:23:00',1,'2025-06-21 02:24:16'),(186,'closed',1,'2025-06-21 02:24:25','2025-06-21 03:24:00','2025-07-06 03:24:00',1,'2025-06-21 02:25:43'),(187,'closed',1,'2025-06-21 02:36:02','2025-06-21 03:35:00','2025-06-28 03:36:00',1,'2025-06-21 02:36:29'),(188,'closed',1,'2025-06-21 02:36:37','2025-06-21 03:36:00','2025-06-29 03:36:00',1,'2025-06-21 02:36:49'),(189,'closed',1,'2025-06-21 02:36:58','2025-06-21 03:36:00','2025-06-29 03:36:00',1,'2025-06-21 02:37:10'),(190,'closed',1,'2025-06-21 03:10:25','2025-06-21 04:10:00','2025-06-29 04:10:00',1,'2025-06-21 03:12:07'),(191,'closed',1,'2025-06-21 03:12:17','2025-06-21 04:12:00','2025-06-22 04:12:00',1,'2025-06-21 03:48:33'),(192,'closed',1,'2025-06-21 03:55:02','2025-06-21 04:54:00','2025-06-22 04:55:00',1,'2025-06-21 03:56:10'),(193,'closed',1,'2025-06-21 03:56:17','2025-06-21 04:56:00','2025-06-22 04:56:00',1,'2025-06-21 03:56:46'),(194,'closed',1,'2025-06-21 04:09:01','2025-06-21 05:08:00','2025-06-29 05:08:00',1,'2025-06-21 05:06:33'),(195,'closed',1,'2025-06-21 05:06:44','2025-06-21 06:06:00','2025-06-29 06:06:00',1,'2025-06-21 05:08:13'),(196,'closed',1,'2025-06-21 05:10:34','2025-06-21 06:10:00','2025-06-26 06:10:00',1,'2025-06-21 19:01:09'),(197,'closed',1,'2025-06-21 19:01:19','2025-06-21 20:01:00','2025-06-29 20:01:00',1,'2025-06-21 19:04:54'),(198,'closed',1,'2025-06-21 19:05:04','2025-06-21 20:05:00','2025-06-28 20:05:00',1,'2025-06-21 19:34:23'),(199,'closed',1,'2025-06-21 19:49:34','2025-06-21 20:49:00','2025-06-29 20:49:00',1,'2025-06-21 19:49:42'),(200,'closed',1,'2025-06-21 23:48:57','2025-06-22 00:48:00','2025-07-05 00:48:00',1,'2025-06-21 23:49:14'),(201,'closed',1,'2025-06-21 23:49:19','2025-06-22 00:49:00','2025-06-29 00:49:00',1,'2025-06-21 23:53:09'),(202,'closed',1,'2025-06-21 23:53:15','2025-06-22 00:53:00','2025-06-28 00:53:00',1,'2025-06-22 03:22:59'),(203,'closed',1,'2025-06-22 03:40:04','2025-06-22 04:40:00','2025-07-05 04:40:00',1,'2025-06-22 03:40:31'),(204,'closed',1,'2025-06-22 03:40:41','2025-06-22 04:40:00','2025-06-26 04:40:00',1,'2025-06-22 03:40:53'),(205,'closed',1,'2025-06-22 03:41:00','2025-06-22 04:40:00','2025-06-28 04:40:00',1,'2025-06-22 03:41:12'),(206,'closed',1,'2025-06-22 03:41:20','2025-06-22 04:41:00','2025-06-26 04:41:00',1,'2025-06-24 11:33:08'),(207,'closed',1,'2025-06-24 11:34:10','2025-06-24 12:34:00','2025-07-06 12:34:00',1,'2025-06-25 07:31:11'),(208,'closed',1,'2025-06-25 07:31:23','2025-06-25 08:31:00','2025-06-27 08:31:00',1,'2025-06-25 08:08:26'),(209,'closed',1,'2025-06-25 08:08:40','2025-06-25 09:08:00','2025-06-26 09:08:00',1,'2025-06-25 08:09:29'),(210,'closed',1,'2025-06-25 08:09:54','2025-06-25 09:09:00','2025-07-12 09:09:00',1,'2025-06-26 01:58:07'),(211,'closed',1,'2025-06-26 01:58:15','2025-06-26 02:58:00','2025-06-27 02:58:00',1,'2025-06-26 02:03:08'),(212,'closed',1,'2025-06-26 02:07:17','2025-06-26 03:07:00','2025-06-28 03:07:00',1,'2025-06-26 02:14:37'),(213,'closed',1,'2025-06-26 15:41:18','2025-06-26 16:41:00','2025-07-05 16:41:00',1,'2025-06-26 22:30:22'),(214,'closed',1,'2025-06-26 22:30:30','2025-06-26 23:30:00','2025-06-27 23:30:00',1,'2025-06-27 03:30:49'),(215,'closed',1,'2025-06-27 03:31:00','2025-06-27 04:30:00','2025-06-28 04:30:00',1,'2025-06-27 18:17:14'),(216,'closed',1,'2025-06-27 18:17:27','2025-06-27 19:17:00','2025-07-04 19:17:00',1,'2025-07-02 05:58:08'),(217,'closed',1,'2025-07-02 07:54:20','2025-07-02 08:54:00','2025-07-12 08:54:00',1,'2025-07-02 12:54:41'),(218,'closed',1,'2025-07-02 12:54:54','2025-07-02 13:54:00','2025-07-05 13:54:00',1,'2025-07-02 12:57:41'),(219,'closed',1,'2025-07-02 13:26:56','2025-07-02 14:26:00','2025-07-12 14:26:00',1,'2025-07-02 13:27:55'),(220,'closed',1,'2025-07-02 13:28:31','2025-07-02 14:28:00','2025-07-12 14:28:00',1,'2025-07-02 13:29:02'),(221,'closed',1,'2025-07-02 13:30:45','2025-07-02 14:30:00','2025-07-19 14:30:00',1,'2025-07-02 13:32:11'),(222,'closed',1,'2025-07-02 13:33:05','2025-07-02 14:33:00','2025-07-12 14:33:00',1,'2025-07-02 13:43:23'),(224,'closed',1,'2025-07-02 14:06:39','2025-07-02 15:06:00','2025-07-12 15:06:00',1,'2025-07-02 14:20:49'),(225,'closed',1,'2025-07-02 14:25:49','2025-07-02 15:25:00','2025-07-05 15:25:00',1,'2025-07-02 14:30:52'),(226,'closed',1,'2025-07-02 14:30:59','2025-07-02 15:30:00','2025-07-12 15:30:00',1,'2025-07-02 14:31:20'),(227,'closed',1,'2025-07-02 14:31:28','2025-07-02 15:31:00','2025-07-12 15:31:00',1,'2025-07-02 14:31:39'),(228,'closed',1,'2025-07-02 14:31:48','2025-07-02 15:31:00','2025-07-11 15:31:00',1,'2025-07-03 10:27:09'),(229,'closed',1,'2025-07-03 12:07:17','2025-07-03 13:07:00','2025-07-11 13:07:00',1,'2025-07-04 07:34:04'),(230,'closed',1,'2025-07-04 07:34:11','2025-07-04 08:34:00','2025-07-05 08:34:00',1,'2025-07-04 13:36:12'),(231,'closed',1,'2025-07-04 13:36:19','2025-07-04 14:36:00','2025-07-12 14:36:00',1,'2025-07-04 13:38:22'),(232,'closed',1,'2025-07-04 13:38:31','2025-07-04 14:38:00','2025-07-12 14:38:00',1,'2025-07-07 05:00:31'),(233,'closed',1,'2025-07-09 03:53:49','2025-07-09 04:53:00','2025-07-26 04:53:00',1,'2025-07-09 08:36:30'),(234,'closed',1,'2025-07-09 08:36:40','2025-07-09 09:36:00','2025-07-18 09:36:00',1,'2025-07-09 08:36:58'),(235,'open',1,'2025-07-09 08:37:09','2025-07-09 09:37:00','2025-07-23 09:37:00',NULL,NULL);
/*!40000 ALTER TABLE `registration_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rejected_combinations`
--

DROP TABLE IF EXISTS `rejected_combinations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rejected_combinations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `major` enum('ACCT','BA','FIN','IT','MRK','NONE') DEFAULT NULL,
  `second_major` enum('ACCT','BA','FIN','IT','MRK') DEFAULT NULL,
  `minor` enum('ACCT','BA','FIN','IT','MRK','IBE') DEFAULT NULL,
  `second_minor` enum('ACCT','BA','FIN','IT','MRK','IBE') DEFAULT NULL,
  `rejection_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rejected_combinations`
--

LOCK TABLES `rejected_combinations` WRITE;
/*!40000 ALTER TABLE `rejected_combinations` DISABLE KEYS */;
INSERT INTO `rejected_combinations` VALUES (1,'IT',NULL,'IBE',NULL,'2025-07-02 14:07:52');
/*!40000 ALTER TABLE `rejected_combinations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schedule`
--

DROP TABLE IF EXISTS `schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schedule` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_code` varchar(20) NOT NULL,
  `week_day` enum('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `professor` varchar(100) NOT NULL,
  `classroom` varchar(50) NOT NULL,
  `group` varchar(50) NOT NULL,
  `session_type` enum('lecture','tutorial') NOT NULL,
  `course_index` int DEFAULT NULL,
  `session_number_index` int DEFAULT NULL,
  `time_slot_index` int DEFAULT NULL,
  `professor_index` int DEFAULT NULL,
  `Tutprof_index` int DEFAULT NULL,
  `lect_prof_index` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=500 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schedule`
--

LOCK TABLES `schedule` WRITE;
/*!40000 ALTER TABLE `schedule` DISABLE KEYS */;
INSERT INTO `schedule` VALUES (1,'BCOR 150','Monday','08:30:00','10:00:00','D. Myriam','S32','F.1','tutorial',4,3,1,1,1,NULL),(2,'CS 120','Monday','10:00:00','11:30:00','M.Ilahi+chalghoun','Lab1+2','F.1','lecture',9,1,2,6,NULL,6),(3,'CS 120','Monday','11:30:00','13:00:00','M.Ilahi+chalghoun','Lab1+2','F.1','lecture',9,2,3,6,NULL,6),(4,'BCOR 130','Tuesday','10:00:00','11:30:00','Marwa Tlili','A9','F.1','tutorial',2,3,7,2,1,NULL),(5,'NBC 130','Tuesday','11:30:00','13:00:00','Ben alaya K.','S10','F.1','lecture',12,1,8,1,NULL,1),(6,'NBC 120','Tuesday','13:30:00','15:00:00','L. Mezghani','S11','F.1','lecture',11,1,9,3,NULL,3),(7,'NBC 120','Tuesday','15:00:00','16:30:00','L. Mezghani','S11','F.1','lecture',11,2,10,3,NULL,3),(8,'BCOR 111','Wednesday','10:00:00','11:30:00','I. Rassas','A8','F.1','lecture',1,1,12,3,NULL,3),(9,'BCOR 111','Wednesday','11:30:00','13:00:00','I. Rassas','A8','F.1','lecture',1,2,13,3,NULL,3),(10,'BCOR 150','Thursday','11:30:00','13:00:00','A. Dridi','A6','F.1','lecture',4,1,18,1,NULL,1),(11,'BCOR 140','Thursday','13:30:00','15:00:00','H. Medyouni','S10','F.1','tutorial',3,3,19,1,1,NULL),(12,'BCOR 111','Thursday','15:00:00','16:30:00','F. Fourati','S13','F.1','tutorial',1,3,20,1,1,NULL),(13,'BCOR 140','Friday','08:30:00','10:00:00','N. Khraief','A5','F.1','lecture',3,1,21,2,NULL,2),(14,'BCOR 140','Friday','10:00:00','11:30:00','N. Khraief','A5','F.1','lecture',3,2,22,2,NULL,2),(15,'BCOR 150','Friday','11:30:00','13:00:00','A. Dridi','A6','F.1','lecture',4,2,23,1,NULL,1),(16,'BCOR 130','Friday','13:30:00','15:00:00','Nejia Moumen','A6','F.1','lecture',2,1,24,4,NULL,4),(17,'BCOR 130','Friday','15:00:00','16:30:00','Nejia Moumen','A6','F.1','lecture',2,2,25,4,NULL,4),(18,'BCOR 140','Thursday','08:30:00','10:00:00','H. Medyouni','S11','F.2','tutorial',3,3,16,1,1,NULL),(19,'CS 120','Thursday','10:00:00','11:30:00','K.Safi+H.Alaya','Lab1+Lab6','F.2','lecture',9,1,17,3,NULL,3),(20,'CS 120','Thursday','11:30:00','13:00:00','K.Safi+H.Alaya','Lab1+Lab6','F.2','lecture',9,2,18,3,NULL,3),(21,'BCOR 130','Thursday','13:30:00','15:00:00','Marwa Tlili','S6','F.2','tutorial',2,3,19,2,1,NULL),(22,'BCOR 150','Monday','10:00:00','11:30:00','D. Myriam','S12','F.2','tutorial',4,3,2,1,1,NULL),(23,'BCOR 111','Monday','11:30:00','13:00:00','R. Ammar Ayachi','S8','F.2','tutorial',1,3,3,4,19,NULL),(24,'NBC 120','Monday','13:30:00','15:00:00','L. Mezghani','S5','F.2','lecture',11,1,4,3,NULL,3),(25,'NBC 120','Monday','15:00:00','16:30:00','L. Mezghani','S5','F.2','lecture',11,2,5,3,NULL,3),(26,'BCOR 140','Tuesday','10:00:00','11:30:00','S. Jouini','A4','F.2','lecture',3,1,7,4,NULL,4),(27,'BCOR 140','Tuesday','11:30:00','13:00:00','S. Jouini','A4','F.2','lecture',3,2,8,4,NULL,4),(28,'NBC 130','Tuesday','13:30:00','15:00:00','Eva Gmati','S2','F.2','lecture',12,1,9,3,NULL,3),(29,'BCOR 150','Wednesday','10:00:00','11:30:00','A. Messaoud','A7','F.2','lecture',4,1,12,2,NULL,2),(30,'BCOR 150','Wednesday','11:30:00','13:00:00','A. Messaoud','A7','F.2','lecture',4,2,13,2,NULL,2),(31,'BCOR 111','Friday','08:30:00','10:00:00','I. Rassas','A8','F.2','lecture',1,1,21,3,NULL,3),(32,'BCOR 111','Friday','10:00:00','11:30:00','I. Rassas','A8','F.2','lecture',1,2,22,3,NULL,3),(33,'BCOR 130','Friday','13:30:00','15:00:00','Nejia Moumen','A9','F.2','lecture',2,1,24,4,NULL,4),(34,'BCOR 130','Friday','15:00:00','16:30:00','Nejia Moumen','A9','F.2','lecture',2,2,25,4,NULL,4),(35,'BCOR 130','Monday','08:30:00','10:00:00','A. ZRIBI','A9','F.3','tutorial',2,3,1,1,1,NULL),(36,'BCOR 140','Monday','10:00:00','11:30:00','S. Asma','S9','F.3','tutorial',3,3,2,2,13,NULL),(37,'BCOR 150','Monday','11:30:00','13:00:00','R. Aloui','A4','F.3','lecture',4,1,3,3,NULL,3),(38,'NBC 120','Monday','13:30:00','15:00:00','A. Mejri','S7','F.3','lecture',11,1,4,1,NULL,1),(39,'BCOR 111','Tuesday','11:30:00','13:00:00','R. Ammar Ayachi','S3','F.3','tutorial',1,3,8,4,19,NULL),(40,'BCOR 150','Tuesday','13:30:00','15:00:00','R. Aloui','A3','F.3','lecture',4,2,9,3,NULL,3),(41,'NBC 120','Tuesday','15:00:00','16:30:00','A. Mejri','S13','F.3','lecture',11,2,10,1,NULL,1),(42,'CS 120','Wednesday','08:30:00','10:00:00','Ons+S.Omri','Lab1+Lab2','F.3','lecture',9,1,11,10,NULL,10),(43,'CS 120','Wednesday','10:00:00','11:30:00','Ons+S.Omri','Lab1+Lab2','F.3','lecture',9,2,12,10,NULL,10),(44,'BCOR 130','Thursday','08:30:00','10:00:00','A. ZRIBI','A6','F.3','lecture',2,1,16,1,NULL,1),(45,'BCOR 130','Thursday','10:00:00','11:30:00','A. ZRIBI','A6','F.3','lecture',2,2,17,1,NULL,1),(46,'BCOR 150','Thursday','11:30:00','13:00:00','Y. Msakni','S12','F.3','tutorial',4,3,18,3,49,NULL),(47,'NBC 130','Friday','08:30:00','10:00:00','Ben alaya K.','S10','F.3','lecture',12,1,21,1,NULL,1),(48,'BCOR 111','Friday','10:00:00','11:30:00','I. Khemir','A4','F.3','lecture',1,1,22,2,NULL,2),(49,'BCOR 111','Friday','11:30:00','13:00:00','I. Khemir','A4','F.3','lecture',1,2,23,2,NULL,2),(50,'BCOR 140','Friday','13:30:00','15:00:00','N. Khraief','A4','F.3','lecture',3,1,24,2,NULL,2),(51,'BCOR 140','Friday','15:00:00','16:30:00','N. Khraief','A4','F.3','lecture',3,2,25,2,NULL,2),(52,'BCOR 111','Monday','08:30:00','10:00:00','R. Ammar Ayachi','S4','F.4','tutorial',1,3,1,4,19,NULL),(53,'NBC 120','Monday','10:00:00','11:30:00','L. Mezghani','S11','F.4','lecture',11,1,2,3,NULL,3),(54,'NBC 120','Monday','11:30:00','13:00:00','L. Mezghani','S11','F.4','lecture',11,2,3,3,NULL,3),(55,'BCOR 130','Monday','13:30:00','15:00:00','A. ZRIBI','A9','F.4','tutorial',2,3,4,1,1,NULL),(56,'NBC 130','Tuesday','10:00:00','11:30:00','Kenz','S10','F.4','lecture',12,1,7,4,NULL,4),(57,'BCOR 140','Tuesday','11:30:00','13:00:00','S. Asma','S6','F.4','tutorial',3,3,8,2,13,NULL),(58,'CS 120','Tuesday','13:30:00','15:00:00','hem+S.Chalghou','Lab1+Lab2','F.4','lecture',9,1,9,2,NULL,2),(59,'CS 120','Tuesday','15:00:00','16:30:00','Sihem+S.Chalghou','Lab1+Lab2','F.4','lecture',9,2,10,11,NULL,11),(60,'BCOR 130','Thursday','08:30:00','10:00:00','A. ZRIBI','A6','F.4','lecture',2,1,16,1,NULL,1),(61,'BCOR 130','Thursday','10:00:00','11:30:00','A. ZRIBI','A6','F.4','lecture',2,2,17,1,NULL,1),(62,'BCOR 150','Thursday','11:30:00','13:00:00','A. Messaoud','A10','F.4','lecture',4,1,18,2,NULL,2),(63,'BCOR 150','Thursday','13:30:00','15:00:00','A. Messaoud','A10','F.4','lecture',4,2,19,2,NULL,2),(64,'BCOR 150','Thursday','15:00:00','16:30:00','Y. Msakni','S12','F.4','tutorial',4,3,20,3,49,NULL),(65,'BCOR 111','Friday','10:00:00','11:30:00','I. Khemir','A4','F.4','lecture',1,1,22,2,NULL,2),(66,'BCOR 111','Friday','11:30:00','13:00:00','I. Khemir','A4','F.4','lecture',1,2,23,2,NULL,2),(67,'BCOR 140','Friday','13:30:00','15:00:00','B. Guizani','A1','F.4','lecture',3,1,24,1,NULL,1),(68,'BCOR 140','Friday','15:00:00','16:30:00','B. Guizani','A1','F.4','lecture',3,2,25,1,NULL,1),(69,'BCOR 130','Monday','10:00:00','11:30:00','Karim Mhedhbi','A5','F.5','lecture',2,1,2,3,NULL,3),(70,'BCOR 130','Monday','11:30:00','13:00:00','Karim Mhedhbi','A5','F.5','lecture',2,2,3,3,NULL,3),(71,'CS 120','Monday','13:30:00','15:00:00','M.Ilahi+S.Chalghoumi','Lab1+4','F.5','lecture',9,1,4,7,NULL,7),(72,'CS 120','Monday','15:00:00','16:30:00','M.Ilahi+S.Chalghoumi','Lab1+4','F.5','lecture',9,2,5,7,NULL,7),(73,'NBC 120','Tuesday','08:30:00','10:00:00','A. Mejri','S1','F.5','lecture',11,1,6,1,NULL,1),(74,'NBC 120','Tuesday','10:00:00','11:30:00','A. Mejri','S1','F.5','lecture',11,2,7,1,NULL,1),(75,'BCOR 140','Tuesday','11:30:00','13:00:00','H. Medyouni','S32','F.5','tutorial',3,3,8,1,1,NULL),(76,'BCOR 130','Tuesday','13:30:00','15:00:00','Yosr Guirat','S9','F.5','tutorial',2,3,9,3,1,NULL),(77,'BCOR 150','Wednesday','10:00:00','11:30:00','A. Messaoud','A7','F.5','lecture',4,1,12,2,NULL,2),(78,'BCOR 150','Wednesday','11:30:00','13:00:00','A. Messaoud','A7','F.5','lecture',4,2,13,2,NULL,2),(79,'BCOR 150','Thursday','10:00:00','11:30:00','H. Bennour','S8','F.5','tutorial',4,3,17,2,17,NULL),(80,'BCOR 111','Thursday','11:30:00','13:00:00','I. Khemir','A4','F.5','lecture',1,1,18,2,NULL,2),(81,'BCOR 111','Thursday','13:30:00','15:00:00','I. Khemir','A4','F.5','lecture',1,2,19,2,NULL,2),(82,'BCOR 140','Friday','08:30:00','10:00:00','N. Khraief','A5','F.5','lecture',3,1,21,2,NULL,2),(83,'BCOR 140','Friday','10:00:00','11:30:00','N. Khraief','A5','F.5','lecture',3,2,22,2,NULL,2),(84,'BCOR 111','Friday','11:30:00','13:00:00','I. Rassas','S12','F.5','tutorial',1,3,23,3,1,NULL),(85,'NBC 130','Friday','13:30:00','15:00:00','Kenz','S10','F.5','lecture',12,1,24,4,NULL,4),(86,'BCOR 130','Monday','10:00:00','11:30:00','Karim Mhedhbi','A5','F.6','lecture',2,1,2,3,NULL,3),(87,'BCOR 130','Monday','11:30:00','13:00:00','Karim Mhedhbi','A5','F.6','lecture',2,2,3,3,NULL,3),(88,'BCOR 130','Monday','13:30:00','15:00:00','Yosr Guirat','S3','F.6','tutorial',2,3,4,3,1,NULL),(89,'NBC 120','Tuesday','10:00:00','11:30:00','L. Mezghani','S4','F.6','lecture',11,1,7,3,NULL,3),(90,'NBC 120','Tuesday','11:30:00','13:00:00','L. Mezghani','S4','F.6','lecture',11,2,8,3,NULL,3),(91,'BCOR 140','Tuesday','13:30:00','15:00:00','S. Asma','S12','F.6','tutorial',3,3,9,2,13,NULL),(92,'BCOR 111','Tuesday','15:00:00','16:30:00','R. Ayachi','S8','F.6','tutorial',1,3,10,5,121,NULL),(93,'BCOR 150','Wednesday','10:00:00','11:30:00','A. Messaoud','A7','F.6','lecture',4,1,12,2,NULL,2),(94,'BCOR 150','Wednesday','11:30:00','13:00:00','A. Messaoud','A7','F.6','lecture',4,2,13,2,NULL,2),(95,'BCOR 150','Thursday','08:30:00','10:00:00','H. Bennour','S13','F.6','tutorial',4,3,16,2,17,NULL),(96,'BCOR 140','Thursday','10:00:00','11:30:00','S. Jouini','A8','F.6','lecture',3,1,17,4,NULL,4),(97,'BCOR 140','Thursday','11:30:00','13:00:00','S. Jouini','A8','F.6','lecture',3,2,18,4,NULL,4),(98,'CS 120','Thursday','13:30:00','15:00:00','Khouloud+Sourour','Lab3+Lab6','F.6','lecture',9,1,19,5,NULL,5),(99,'CS 120','Thursday','15:00:00','16:30:00','Khouloud+Sourour','Lab3+Lab6','F.6','lecture',9,2,20,5,NULL,5),(100,'BCOR 111','Friday','08:30:00','10:00:00','I. Rassas','A8','F.6','lecture',1,1,21,3,NULL,3),(101,'BCOR 111','Friday','10:00:00','11:30:00','I. Rassas','A8','F.6','lecture',1,2,22,3,NULL,3),(102,'NBC 130','Friday','11:30:00','13:00:00','Kenz','S10','F.6','lecture',12,1,23,4,NULL,4),(137,'BCOR 140','Monday','08:30:00','10:00:00','S. Asma','S11','F.7','tutorial',3,3,1,2,13,NULL),(138,'BCOR 111','Monday','10:00:00','11:30:00','R. Ammar Ayachi','S10','F.7','tutorial',1,3,2,4,19,NULL),(139,'BCOR 150','Monday','11:30:00','13:00:00','D. Myriam','S10','F.7','tutorial',4,3,3,1,1,NULL),(140,'NBC 120','Monday','13:30:00','15:00:00','F. Lamloumi','S2','F.7','lecture',11,1,4,2,NULL,2),(141,'NBC 120','Monday','15:00:00','16:30:00','F. Lamloumi','S2','F.7','lecture',11,2,5,2,NULL,2),(142,'NBC 130','Tuesday','10:00:00','11:30:00','Eva Gmati','S2','F.7','lecture',12,1,7,3,NULL,3),(143,'BCOR 130','Tuesday','11:30:00','13:00:00','Marwa Tlili','A8','F.7','tutorial',2,3,8,2,1,NULL),(144,'BCOR 111','Wednesday','10:00:00','11:30:00','I. Rassas','A8','F.7','lecture',1,1,12,3,NULL,3),(145,'BCOR 111','Wednesday','11:30:00','13:00:00','I. Rassas','A8','F.7','lecture',1,2,13,3,NULL,3),(146,'BCOR 140','Thursday','10:00:00','11:30:00','N. Khraief','A8','F.7','lecture',3,1,17,2,NULL,2),(147,'BCOR 140','Thursday','11:30:00','13:00:00','N. Khraief','A8','F.7','lecture',3,2,18,2,NULL,2),(148,'BCOR 150','Thursday','13:30:00','15:00:00','A. Dridi','A6','F.7','lecture',4,1,19,1,NULL,1),(149,'BCOR 150','Thursday','15:00:00','16:30:00','A. Dridi','A6','F.7','lecture',4,2,20,1,NULL,1),(150,'CS 120','Friday','10:00:00','11:30:00','O.Dridi+H.Alaya','Lab1+Lab3','F.7','lecture',9,1,22,9,NULL,9),(151,'CS 120','Friday','11:30:00','13:00:00','O.Dridi+H.Alaya','Lab1+Lab3','F.7','lecture',9,2,23,9,NULL,9),(152,'BCOR 130','Friday','13:30:00','15:00:00','Nejia Moumen','A8','F.7','lecture',2,1,24,4,NULL,4),(153,'BCOR 130','Friday','15:00:00','16:30:00','Nejia Moumen','A8','F.7','lecture',2,2,25,4,NULL,4),(154,'BCOR 111','Monday','10:00:00','11:30:00','F.B.Yahya','A6','F.8','lecture',1,1,2,1,NULL,1),(155,'BCOR 111','Monday','11:30:00','13:00:00','F.B.Yahya','A6','F.8','lecture',1,2,3,1,NULL,1),(156,'BCOR 150','Monday','13:30:00','15:00:00','R. Aloui','A5','F.8','lecture',4,1,4,3,NULL,3),(157,'NBC 130','Tuesday','08:30:00','10:00:00','Kenz','S10','F.8','lecture',12,1,6,4,NULL,4),(158,'BCOR 150','Tuesday','10:00:00','11:30:00','R. Aloui','A3','F.8','lecture',4,2,7,3,NULL,3),(159,'BCOR 150','Tuesday','11:30:00','13:00:00','D. Myriam','S1','F.8','tutorial',4,3,8,1,1,NULL),(160,'BCOR 130','Tuesday','13:30:00','15:00:00','Marwa Tlili','A6','F.8','tutorial',2,3,9,2,1,NULL),(161,'NBC 120','Wednesday','10:00:00','11:30:00','F. Lamloumi','S5','F.8','lecture',11,1,12,2,NULL,2),(162,'NBC 120','Wednesday','11:30:00','13:00:00','F. Lamloumi','S5','F.8','lecture',11,2,13,2,NULL,2),(163,'BCOR 130','Thursday','08:30:00','10:00:00','Anas Ksontini','A8','F.8','lecture',2,1,16,2,NULL,2),(164,'BCOR 130','Thursday','10:00:00','11:30:00','Anas Ksontini','A8','F.8','lecture',2,2,17,2,NULL,2),(165,'BCOR 140','Thursday','11:30:00','13:00:00','H. Medyouni','S7','F.8','tutorial',3,3,18,1,1,NULL),(166,'BCOR 140','Friday','08:30:00','10:00:00','N. Khraief','A5','F.8','lecture',3,1,21,2,NULL,2),(167,'BCOR 140','Friday','10:00:00','11:30:00','N. Khraief','A5','F.8','lecture',3,2,22,2,NULL,2),(168,'BCOR 111','Friday','11:30:00','13:00:00','F.B.Yahya','S3','F.8','tutorial',1,3,23,2,1,NULL),(169,'CS 120','Friday','13:30:00','15:00:00','O.Dridi+H.Alaya','Lab1+Lab3','F.8','lecture',9,1,24,9,NULL,9),(170,'CS 120','Friday','15:00:00','16:30:00','O.Dridi+H.Alaya','Lab1+Lab3','F.8','lecture',9,2,25,9,NULL,9),(171,'NBC 120','Monday','08:30:00','10:00:00','F. Lamloumi','S5','F.9','lecture',11,1,1,2,NULL,2),(172,'BCOR 150','Monday','11:30:00','13:00:00','R. Aloui','A4','F.9','lecture',4,1,3,3,NULL,3),(173,'CS 120','Monday','13:30:00','15:00:00','Sourour+olfa+S.Benz','Lab1+5','F.9','lecture',9,1,4,12,NULL,12),(174,'CS 120','Monday','15:00:00','16:30:00','Sourour+olfa+S.Benz','Lab1+5','F.9','lecture',9,2,5,12,NULL,12),(175,'NBC 130','Tuesday','08:30:00','10:00:00','E. Gmati','S2','F.9','lecture',12,1,6,2,NULL,2),(176,'BCOR 140','Tuesday','10:00:00','11:30:00','S. Jouini','A4','F.9','lecture',3,1,7,4,NULL,4),(177,'BCOR 140','Tuesday','11:30:00','13:00:00','S. Jouini','A4','F.9','lecture',3,2,8,4,NULL,4),(178,'BCOR 150','Tuesday','13:30:00','15:00:00','R. Aloui','A3','F.9','lecture',4,2,9,3,NULL,3),(179,'BCOR 140','Tuesday','15:00:00','16:30:00','S. Asma','S2','F.9','tutorial',3,3,10,2,13,NULL),(180,'NBC 120','Wednesday','08:30:00','10:00:00','F. Lamloumi','S5','F.9','lecture',11,2,11,2,NULL,2),(181,'BCOR 111','Wednesday','10:00:00','11:30:00','I. Rassas','A8','F.9','lecture',1,1,12,3,NULL,3),(182,'BCOR 111','Wednesday','11:30:00','13:00:00','I. Rassas','A8','F.9','lecture',1,2,13,3,NULL,3),(183,'BCOR 150','Thursday','10:00:00','11:30:00','H. Bennour','S8','F.9','tutorial',4,3,17,2,17,NULL),(184,'BCOR 130','Thursday','11:30:00','13:00:00','Marwa Tlili','S6','F.9','tutorial',2,3,18,2,1,NULL),(185,'BCOR 111','Thursday','13:30:00','15:00:00','F. Fourati','S12','F.9','tutorial',1,3,19,1,1,NULL),(186,'BCOR 130','Friday','13:30:00','15:00:00','Nejia Moumen','A9','F.9','lecture',2,1,24,4,NULL,4),(187,'BCOR 130','Friday','15:00:00','16:30:00','Nejia Moumen','A9','F.9','lecture',2,2,25,4,NULL,4),(188,'NBC 120','Monday','11:30:00','13:00:00','A. Mejri','S13','F.10','lecture',11,1,3,1,NULL,1),(190,'BCOR 150','Tuesday','08:30:00','10:00:00','D. Myriam','S32','F.10','tutorial',4,3,6,1,1,NULL),(191,'BCOR 140','Tuesday','10:00:00','11:30:00','S. Asma','S7','F.10','tutorial',3,3,7,2,13,NULL),(192,'NBC 120','Tuesday','11:30:00','13:00:00','A. Mejri','S13','F.10','lecture',11,2,8,1,NULL,1),(193,'NBC 130','Tuesday','13:30:00','15:00:00','Kenz','S10','F.10','lecture',12,1,9,4,NULL,4),(194,'BCOR 130','Tuesday','15:00:00','16:30:00','Yosr Guirat','S1','F.10','tutorial',2,3,10,3,1,NULL),(195,'BCOR 130','Wednesday','10:00:00','11:30:00','Karim Mhedhbi','A5','F.10','lecture',2,1,12,3,NULL,3),(196,'BCOR 130','Wednesday','11:30:00','13:00:00','Karim Mhedhbi','A5','F.10','lecture',2,2,13,3,NULL,3),(197,'CS 120','Thursday','10:00:00','11:30:00','M.Nakouri+Sourour','Lab2+Lab3','F.10','lecture',9,1,17,8,NULL,8),(198,'CS 120','Thursday','11:30:00','13:00:00','M.Nakouri+Sourour','Lab2+Lab3','F.10','lecture',9,2,18,8,NULL,8),(199,'BCOR 150','Thursday','13:30:00','15:00:00','A. Dridi','A6','F.10','lecture',4,1,19,1,NULL,1),(200,'BCOR 150','Thursday','15:00:00','16:30:00','A. Dridi','A6','F.10','lecture',4,2,20,1,NULL,1),(201,'BCOR 111','Friday','10:00:00','11:30:00','I. Khemir','A4','F.10','lecture',1,1,22,2,NULL,2),(202,'BCOR 111','Friday','11:30:00','13:00:00','I. Khemir','A4','F.10','lecture',1,2,23,2,NULL,2),(203,'BCOR 140','Friday','13:30:00','15:00:00','B. Guizani','A1','F.10','lecture',3,1,24,1,NULL,1),(204,'BCOR 140','Friday','15:00:00','16:30:00','B. Guizani','A1','F.10','lecture',3,2,25,1,NULL,1),(205,'BCOR 111','Monday','10:00:00','11:30:00','F.B.Yahya','A6','F.11','lecture',1,1,2,1,NULL,1),(206,'BCOR 111','Monday','11:30:00','13:00:00','F.B.Yahya','A6','F.11','lecture',1,2,3,1,NULL,1),(207,'NBC 120','Monday','15:00:00','16:30:00','A. Mejri','S6','F.11','lecture',11,1,5,1,NULL,1),(208,'BCOR 150','Tuesday','10:00:00','11:30:00','D. Myriam','S6','F.11','tutorial',4,3,7,1,1,NULL),(209,'BCOR 130','Tuesday','11:30:00','13:00:00','Yosr Guirat','S10','F.11','tutorial',2,3,8,3,1,NULL),(210,'NBC 120','Tuesday','13:30:00','15:00:00','A. Mejri','S13','F.11','lecture',11,2,9,1,NULL,1),(211,'NBC 130','Tuesday','15:00:00','16:30:00','Kenz','S10','F.11','lecture',12,1,10,4,NULL,4),(212,'BCOR 130','Wednesday','10:00:00','11:30:00','Karim Mhedhbi','A5','F.11','lecture',2,1,12,3,NULL,3),(213,'BCOR 130','Wednesday','11:30:00','13:00:00','Karim Mhedhbi','A5','F.11','lecture',2,2,13,3,NULL,3),(214,'BCOR 140','Thursday','10:00:00','11:30:00','H. Medyouni','S2','F.11','tutorial',3,3,17,1,1,NULL),(215,'BCOR 150','Thursday','11:30:00','13:00:00','A. Dridi','A6','F.11','lecture',4,1,18,1,NULL,1),(216,'CS 120','Thursday','13:30:00','15:00:00','Khakouri+H.Alaya','Lab1+Lab2','F.11','lecture',9,1,19,4,NULL,4),(217,'CS 120','Thursday','15:00:00','16:30:00','Khakouri+H.Alaya','Lab1+Lab2','F.11','lecture',9,2,20,4,NULL,4),(218,'BCOR 111','Friday','10:00:00','11:30:00','F.B.Yahya','S9','F.11','tutorial',1,3,22,2,1,NULL),(219,'BCOR 150','Friday','11:30:00','13:00:00','A. Dridi','A6','F.11','lecture',4,2,23,1,NULL,1),(220,'BCOR 140','Friday','13:30:00','15:00:00','B. Guizani','A1','F.11','lecture',3,1,24,1,NULL,1),(221,'BCOR 140','Friday','15:00:00','16:30:00','B. Guizani','A1','F.11','lecture',3,2,25,1,NULL,1),(222,'BCOR 150','Monday','08:30:00','10:00:00','D. Myriam','S32','F.12','tutorial',4,3,1,1,1,NULL),(223,'CS 120','Monday','10:00:00','11:30:00','Benzarti+Sourour','Lab6+7','F.12','lecture',9,1,2,1,NULL,1),(224,'CS 120','Monday','11:30:00','13:00:00','Benzarti+Sourour','Lab6+7','F.12','lecture',9,2,3,1,NULL,1),(225,'BCOR 111','Monday','13:30:00','15:00:00','F.B.Yahya','S13','F.12','tutorial',1,3,4,2,1,NULL),(226,'BCOR 130','Monday','15:00:00','16:30:00','Yosr Guirat','S9','F.12','tutorial',2,3,5,3,1,NULL),(227,'BCOR 140','Tuesday','10:00:00','11:30:00','H. Medyouni','S32','F.12','tutorial',3,3,7,1,1,NULL),(228,'NBC 120','Tuesday','11:30:00','13:00:00','F. Lamloumi','S7','F.12','lecture',11,1,8,2,NULL,2),(229,'NBC 120','Tuesday','13:30:00','15:00:00','F. Lamloumi','S7','F.12','lecture',11,2,9,2,NULL,2),(230,'BCOR 130','Wednesday','10:00:00','11:30:00','Karim Mhedhbi','A5','F.12','lecture',2,1,12,3,NULL,3),(231,'BCOR 130','Wednesday','11:30:00','13:00:00','Karim Mhedhbi','A5','F.12','lecture',2,2,13,3,NULL,3),(232,'BCOR 150','Thursday','11:30:00','13:00:00','A. Dridi','A6','F.12','lecture',4,1,18,1,NULL,1),(233,'BCOR 111','Friday','08:30:00','10:00:00','I. Rassas','A8','F.12','lecture',1,1,21,3,NULL,3),(234,'BCOR 111','Friday','10:00:00','11:30:00','I. Rassas','A8','F.12','lecture',1,2,22,3,NULL,3),(235,'BCOR 150','Friday','11:30:00','13:00:00','A. Dridi','A6','F.12','lecture',4,2,23,1,NULL,1),(236,'BCOR 140','Friday','13:30:00','15:00:00','N. Khraief','A4','F.12','lecture',3,1,24,3,NULL,3),(237,'BCOR 140','Friday','15:00:00','16:30:00','N. Khraief','A4','F.12','lecture',3,2,25,3,NULL,3),(238,'BCOR 230','Monday','08:30:00','10:00:00','X','S7','SO.1','tutorial',7,3,1,1,1,NULL),(239,'BCOR 230','Monday','10:00:00','11:30:00','A. Gharbi','A2','SO.1','lecture',7,1,2,1,NULL,1),(240,'BCOR 230','Monday','11:30:00','13:00:00','A. Gharbi','A2','SO.1','lecture',7,2,3,1,NULL,1),(241,'888','Tuesday','10:00:00','11:30:00','A.Azouz','Lab6','SO.1','lecture',10,1,7,1,NULL,1),(242,'888','Tuesday','11:30:00','13:00:00','A.Azouz','Lab6','SO.1','lecture',10,2,8,1,NULL,1),(243,'NBC 210','Tuesday','13:30:00','15:00:00','L. Rezgui','S19','SO.1','lecture',13,1,9,3,NULL,3),(244,'NBC 210','Tuesday','15:00:00','16:30:00','L. Rezgui','S19','SO.1','lecture',13,2,10,3,NULL,3),(245,'777','Wednesday','10:00:00','11:30:00','R. Esghaier','A6','SO.1','lecture',8,1,12,1,NULL,1),(246,'777','Wednesday','11:30:00','13:00:00','R. Esghaier','A6','SO.1','lecture',8,2,13,1,NULL,1),(247,'BCOR 200','Thursday','10:00:00','11:30:00','S. Ben Abdallah','A8','SO.1','lecture',5,1,17,4,NULL,3),(248,'BCOR 200','Thursday','11:30:00','13:00:00','S. BenbAbdallah','A8','SO.1','lecture',5,2,18,4,1,NULL),(249,'BCOR 210','Thursday','13:30:00','15:00:00','H. Zouaoui','A7','SO.1','lecture',6,1,19,1,NULL,1),(250,'BCOR 210','Thursday','15:00:00','16:30:00','H. Zouaoui','A7','SO.1','lecture',6,2,20,1,NULL,1),(251,'777','Friday','13:30:00','15:00:00','Sadok Laajimi','A4','SO.1','tutorial',8,3,24,5,673,NULL),(252,'BCOR 230','Monday','10:00:00','11:30:00','A. Gharbi','A2','SO.2','lecture',7,1,2,1,NULL,1),(253,'BCOR 230','Monday','11:30:00','13:00:00','A. Gharbi','A2','SO.2','lecture',7,2,3,1,NULL,1),(254,'BCOR 260','Monday','13:30:00','15:00:00','R. Esghaier','A2','SO.2','lecture',8,1,4,1,NULL,1),(255,'BCOR 260','Monday','15:00:00','16:30:00','R. Esghaier','A2','SO.2','lecture',8,2,5,1,NULL,1),(256,'BCOR 200','Tuesday','10:00:00','11:30:00','S. Ben Abdallah','A8','SO.2','lecture',5,1,7,3,NULL,3),(257,'BCOR 200','Tuesday','11:30:00','13:00:00','S. Ben Abdallah','A8','SO.2','lecture',5,2,8,3,NULL,3),(258,'BCOR 210','Wednesday','10:00:00','11:30:00','M. Ben Nouri','A1','SO.2','lecture',6,1,12,2,NULL,2),(259,'BCOR 210','Wednesday','11:30:00','13:00:00','M. Ben Nouri','A1','SO.2','lecture',6,2,13,2,NULL,2),(260,'NBC 210','Thursday','10:00:00','11:30:00','L. Rezgui','S16','SO.2','lecture',13,1,17,3,NULL,3),(261,'NBC 210','Thursday','11:30:00','13:00:00','L. Rezgui','S16','SO.2','lecture',13,2,18,3,NULL,3),(262,'888','Thursday','13:30:00','15:00:00','Amel B.Yaghlene','Lab6','SO.2','lecture',10,1,19,2,NULL,2),(263,'888','Thursday','15:00:00','16:30:00','Amel B.Yaghlene','Lab6','SO.2','lecture',10,2,20,2,NULL,2),(264,'BCOR 230','Friday','10:00:00','11:30:00','X','S11','SO.2','tutorial',7,3,22,1,1,NULL),(265,'777','Friday','11:30:00','13:00:00','Sadok Laajimi','A4','SO.2','tutorial',8,3,23,5,673,NULL),(266,'777','Monday','08:30:00','10:00:00','K. Soussou','S39','SO.3','tutorial',8,3,1,1,1,NULL),(267,'BCOR 230','Monday','10:00:00','11:30:00','A. Gharbi','A2','SO.3','lecture',7,1,2,1,NULL,1),(268,'BCOR 230','Monday','11:30:00','13:00:00','A. Gharbi','A2','SO.3','lecture',7,2,3,1,NULL,1),(269,'NBC 210','Monday','13:30:00','15:00:00','F. Marzouki','S17','SO.3','lecture',13,1,4,2,NULL,2),(270,'NBC 210','Monday','15:00:00','16:30:00','F. Marzouki','S17','SO.3','lecture',13,2,5,2,NULL,2),(271,'888','Tuesday','13:30:00','15:00:00','M.Abdelmoulah','Lab5','SO.3','lecture',10,1,9,4,NULL,4),(272,'888','Tuesday','15:00:00','16:30:00','M.Abdelmoulah','Lab5','SO.3','lecture',10,2,10,4,NULL,4),(273,'777','Wednesday','10:00:00','11:30:00','R. Esghaier','A6','SO.3','lecture',8,1,12,1,NULL,1),(274,'777','Wednesday','11:30:00','13:00:00','R. Esghaier','A6','SO.3','lecture',8,2,13,1,NULL,1),(275,'BCOR 230','Thursday','08:30:00','10:00:00','X','S3','SO.3','tutorial',7,3,16,1,1,NULL),(276,'BCOR 200','Thursday','10:00:00','11:30:00','S. Ben Abdallah','A7','SO.3','lecture',5,1,17,3,NULL,3),(277,'BCOR 200','Thursday','11:30:00','13:00:00','S. Ben Abdallah','A7','SO.3','lecture',5,2,18,3,NULL,3),(278,'BCOR 210','Thursday','13:30:00','15:00:00','H. Zouaoui','A7','SO.3','lecture',6,1,19,1,NULL,1),(279,'BCOR 210','Thursday','15:00:00','16:30:00','H. Zouaoui','A7','SO.3','lecture',6,2,20,1,NULL,1),(280,'777','Monday','10:00:00','11:30:00','K. Soussou','A1','SO.4','tutorial',8,3,2,1,1,NULL),(281,'BCOR 230','Monday','11:30:00','13:00:00','X','S13','SO.4','tutorial',7,3,3,1,1,NULL),(282,'CS 220','Monday','13:30:00','15:00:00','M. Zayen','Lab3','SO.4','lecture',10,1,4,3,NULL,6),(283,'CS 220','Monday','15:00:00','16:30:00','M. Zayen','Lab3','SO.4','lecture',10,2,5,3,NULL,6),(284,'BCOR 210','Tuesday','13:30:00','15:00:00','M. Ben Nouri','A2','SO.4','lecture',6,1,9,2,NULL,2),(285,'BCOR 210','Tuesday','15:00:00','16:30:00','M. Ben Nouri','A2','SO.4','lecture',6,2,10,2,NULL,2),(286,'777','Wednesday','10:00:00','11:30:00','R. Esghaier','A6','SO.4','lecture',8,1,12,1,NULL,1),(287,'777','Wednesday','11:30:00','13:00:00','R. Esghaier','A6','SO.4','lecture',8,2,13,1,NULL,1),(288,'BCOR 230','Thursday','10:00:00','11:30:00','A. Gharbi','A2','SO.4','lecture',7,1,17,1,NULL,1),(289,'BCOR 230','Thursday','11:30:00','13:00:00','A. Gharbi','A2','SO.4','lecture',7,2,18,1,NULL,1),(290,'NBC 210','Thursday','13:30:00','15:00:00','B. Elkaou','S9','SO.4','lecture',13,1,19,1,NULL,1),(291,'NBC 210','Thursday','15:00:00','16:30:00','B. Elkaou','S9','SO.4','lecture',13,2,20,1,NULL,1),(292,'BCOR 200','Friday','10:00:00','11:30:00','G. Aydi','A2','SO.4','lecture',5,1,22,1,NULL,1),(293,'BCOR 200','Friday','11:30:00','13:00:00','G. Aydi','A2','SO.4','lecture',5,2,23,1,NULL,1),(294,'BCOR 230','Monday','10:00:00','11:30:00','X','S32','SO.5','tutorial',7,3,2,1,1,NULL),(295,'777','Monday','13:30:00','15:00:00','R. Esghaier','A2','SO.5','lecture',8,1,4,1,NULL,1),(296,'777','Monday','15:00:00','16:30:00','R. Esghaier','A2','SO.5','lecture',8,2,5,1,NULL,1),(297,'888','Tuesday','10:00:00','11:30:00','M.Abdelmoulah','Lab5','SO.5','lecture',10,1,7,4,NULL,4),(298,'888','Tuesday','11:30:00','13:00:00','M.Abdelmoulah','Lab5','SO.5','lecture',10,2,8,4,NULL,4),(299,'NBC 210','Tuesday','13:30:00','15:00:00','F. Marzouki','S17','SO.5','lecture',13,1,9,2,NULL,2),(300,'NBC 210','Tuesday','15:00:00','16:30:00','F. Marzouki','S17','SO.5','lecture',13,2,10,2,NULL,2),(301,'BCOR 210','Wednesday','10:00:00','11:30:00','M. Ben Nouri','A1','SO.5','lecture',6,1,12,2,NULL,2),(302,'BCOR 210','Wednesday','11:30:00','13:00:00','M. Ben Nouri','A1','SO.5','lecture',6,2,13,2,NULL,2),(303,'BCOR 230','Thursday','10:00:00','11:30:00','A. Gharbi','A2','SO.5','lecture',7,1,17,1,NULL,1),(304,'BCOR 230','Thursday','11:30:00','13:00:00','A. Gharbi','A2','SO.5','lecture',7,2,18,1,NULL,1),(305,'BCOR 200','Friday','10:00:00','11:30:00','I. Chakroun','A9','SO.5','lecture',5,1,22,2,NULL,2),(306,'BCOR 200','Friday','11:30:00','13:00:00','I. Chakroun','A9','SO.5','lecture',5,2,23,2,NULL,2),(307,'777','Friday','15:00:00','16:30:00','S. Bennouri','A1','SO.5','tutorial',8,3,25,4,617,NULL),(308,'BCOR 230','Monday','10:00:00','11:30:00','A. Gharbi','A2','SO.6','lecture',7,1,2,1,NULL,1),(309,'BCOR 230','Monday','11:30:00','13:00:00','A. Gharbi','A2','SO.6','lecture',7,2,3,1,NULL,1),(310,'NBC 210','Tuesday','10:00:00','11:30:00','L. Rezgui','S20','SO.6','lecture',13,1,7,3,NULL,3),(311,'NBC 210','Tuesday','11:30:00','13:00:00','L. Rezgui','S20','SO.6','lecture',13,2,8,3,NULL,3),(312,'888','Tuesday','13:30:00','15:00:00','Amel B.Yaghlene','Lab3','SO.6','lecture',10,1,9,2,NULL,2),(313,'888','Tuesday','15:00:00','16:30:00','Amel B.Yaghlene','Lab3','SO.6','lecture',10,2,10,2,NULL,2),(314,'777','Wednesday','10:00:00','11:30:00','R. Esghaier','A6','SO.6','lecture',8,1,12,1,NULL,1),(315,'777','Wednesday','11:30:00','13:00:00','R. Esghaier','A6','SO.6','lecture',8,2,13,1,NULL,1),(316,'BCOR 230','Thursday','10:00:00','11:30:00','X','S32','SO.6','tutorial',7,3,17,1,1,NULL),(317,'BCOR 210','Thursday','13:30:00','15:00:00','N. Belaid','A7','SO.6','lecture',6,1,19,3,NULL,3),(318,'BCOR 210','Thursday','15:00:00','16:30:00','N. Belaid','A7','SO.6','lecture',6,2,20,3,NULL,3),(319,'777','Friday','10:00:00','11:30:00','Sadok Laajimi','A4','SO.6','tutorial',8,3,22,5,673,NULL),(320,'BCOR 200','Friday','13:30:00','15:00:00','G. Aydi','A2','SO.6','lecture',5,1,24,1,NULL,1),(321,'BCOR 200','Friday','15:00:00','16:30:00','G. Aydi','A2','SO.6','lecture',5,2,25,1,NULL,1),(322,'888','Monday','10:00:00','11:30:00','M. Zayen','Lab3','SO.7','lecture',10,1,2,3,NULL,3),(323,'888','Monday','11:30:00','13:00:00','M. Zayen','Lab3','SO.7','lecture',10,2,3,3,NULL,3),(324,'777','Monday','13:30:00','15:00:00','R. Esghaier','A2','SO.7','lecture',8,1,4,1,NULL,1),(325,'777','Monday','15:00:00','16:30:00','R. Esghaier','A2','SO.7','lecture',8,2,5,1,NULL,1),(326,'BCOR 210','Tuesday','08:30:00','10:00:00','M. Ben Nouri','A2','SO.7','lecture',6,1,6,2,NULL,2),(327,'BCOR 210','Tuesday','10:00:00','11:30:00','M. Ben Nouri','A2','SO.7','lecture',6,2,7,2,NULL,2),(328,'NBC 210','Wednesday','10:00:00','11:30:00','B. Elkaou','S12','SO.7','lecture',13,1,12,1,NULL,1),(329,'NBC 210','Wednesday','11:30:00','13:00:00','B. Elkaou','S12','SO.7','lecture',13,2,13,1,NULL,1),(330,'BCOR 230','Thursday','10:00:00','11:30:00','A. Gharbi','A2','SO.7','lecture',7,1,17,1,NULL,1),(331,'BCOR 230','Thursday','11:30:00','13:00:00','A. Gharbi','A2','SO.7','lecture',7,2,18,1,NULL,1),(332,'BCOR 230','Friday','08:30:00','10:00:00','X','S32','SO.7','tutorial',7,3,21,1,1,NULL),(333,'BCOR 200','Friday','10:00:00','11:30:00','I. Chakroun','A9','SO.7','lecture',5,1,22,2,NULL,2),(334,'BCOR 200','Friday','11:30:00','13:00:00','I. Chakroun','A9','SO.7','lecture',5,2,23,2,NULL,2),(335,'777','Friday','13:30:00','15:00:00','S. Bannouri','S14','SO.7','tutorial',8,3,24,3,561,NULL),(350,'BCOR 230','Monday','10:00:00','11:30:00','A. Gharbi','A2','SO.8','lecture',7,1,2,1,NULL,1),(351,'BCOR 230','Monday','11:30:00','13:00:00','A. Gharbi','A2','SO.8','lecture',7,2,3,1,NULL,1),(352,'777','Monday','13:30:00','15:00:00','R. Esghaier','A2','SO.8','lecture',8,1,4,1,NULL,1),(353,'777','Monday','15:00:00','16:30:00','R. Esghaier','A2','SO.8','lecture',8,2,5,1,NULL,1),(354,'BCOR 210','Tuesday','08:30:00','10:00:00','M. Ben Nouri','A5','SO.8','lecture',6,1,6,2,NULL,2),(355,'BCOR 210','Tuesday','10:00:00','11:30:00','M. Ben Nouri','A5','SO.8','lecture',6,2,7,2,NULL,2),(356,'888','Tuesday','13:30:00','15:00:00','A.Azouz','Lab3','SO.8','lecture',10,1,9,1,NULL,1),(357,'888','Tuesday','15:00:00','16:30:00','A.Azouz','Lab3','SO.8','lecture',10,2,10,1,NULL,1),(358,'NBC 210','Thursday','10:00:00','11:30:00','B. Elkaou','S4','SO.8','lecture',13,1,17,1,NULL,1),(359,'NBC 210','Thursday','11:30:00','13:00:00','B. Elkaou','S4','SO.8','lecture',13,2,18,1,NULL,1),(360,'BCOR 230','Thursday','13:30:00','15:00:00','Unknown','S1','SO.8','tutorial',7,3,19,2,393,NULL),(361,'BCOR 200','Friday','10:00:00','11:30:00','G. Aydi','A2','SO.8','lecture',5,1,22,1,NULL,1),(362,'BCOR 200','Friday','11:30:00','13:00:00','G. Aydi','A3','SO.8','lecture',5,2,23,1,NULL,1),(363,'777','Friday','13:30:00','15:00:00','Sadok Laajimi','A4','SO.8','tutorial',8,3,24,5,673,NULL),(364,'777','Monday','10:00:00','11:30:00','Manara Toukabri','S39','SO.9','tutorial',8,3,2,2,113,NULL),(365,'BCOR 230','Monday','11:30:00','13:00:00','unknown','S13','SO.9','tutorial',7,3,3,2,393,NULL),(366,'777','Monday','13:30:00','15:00:00','R. Esghaier','A2','SO.9','lecture',8,1,4,1,NULL,1),(368,'888','Tuesday','10:00:00','11:30:00','Amel B.Yaghlene','Lab3','SO.9','lecture',10,2,7,2,NULL,2),(370,'BCOR 230','Thursday','10:00:00','11:30:00','A. Gharbi','A2','SO.9','lecture',7,1,17,1,NULL,1),(372,'BCOR 210','Thursday','13:30:00','15:00:00','N. Belaid','A1','SO.9','lecture',6,1,19,3,NULL,3),(374,'NBC 210','Friday','08:30:00','10:00:00','N. Manai','S17','SO.9','lecture',13,1,21,4,NULL,4),(376,'BCOR 200','Friday','13:30:00','15:00:00','G. Aydi','A2','SO.9','lecture',5,1,24,1,NULL,1),(380,'777','Monday','13:30:00','15:00:00','R. Esghaier','A2','SO.9','lecture',8,2,4,1,NULL,1),(382,'888','Tuesday','10:00:00','11:30:00','Amel B.Yaghlene','Lab3','SO.9','lecture',10,1,7,2,NULL,2),(384,'BCOR 230','Thursday','10:00:00','11:30:00','A. Gharbi','A2','SO.9','lecture',7,2,17,1,NULL,1),(386,'BCOR 210','Thursday','13:30:00','15:00:00','N. Belaid','A1','SO.9','lecture',6,2,19,3,NULL,3),(388,'NBC 210','Friday','08:30:00','10:00:00','N. Manai','S17','SO.9','lecture',13,2,21,4,NULL,4),(390,'BCOR 200','Friday','13:30:00','15:00:00','G. Aydi','A2','SO.9','lecture',5,2,24,1,NULL,1),(392,'NBC 210','Monday','10:00:00','11:30:00','F. Marzouki','S2','SO.10','lecture',13,1,2,2,NULL,2),(393,'NBC 210','Monday','11:30:00','13:00:00','F. Marzouki','S2','SO.10','lecture',13,2,3,2,NULL,2),(394,'888','Monday','13:30:00','15:00:00','A.Azouz','Lab6','SO.10','lecture',10,1,4,1,NULL,1),(395,'888','Monday','15:00:00','16:30:00','A.Azouz','Lab6','SO.10','lecture',10,2,5,1,NULL,1),(396,'BCOR 200','Tuesday','10:00:00','11:30:00','S. Ben Abdallah','A8','SO.10','lecture',5,1,7,3,NULL,3),(397,'BCOR 200','Tuesday','11:30:00','13:00:00','S. Ben Abdallah','A8','SO.10','lecture',5,2,8,3,NULL,3),(398,'BCOR 210','Tuesday','13:30:00','15:00:00','M. Ben Nouri','A2','SO.10','lecture',6,1,9,2,NULL,2),(399,'BCOR 210','Tuesday','15:00:00','16:30:00','M. Ben Nouri','A2','SO.10','lecture',6,2,10,2,NULL,2),(400,'777','Wednesday','10:00:00','11:30:00','R. Esghaier','A6','SO.10','lecture',8,1,12,1,NULL,1),(401,'777','Wednesday','11:30:00','13:00:00','R. Esghaier','A6','SO.10','lecture',8,2,13,1,NULL,1),(402,'BCOR 230','Thursday','10:00:00','11:30:00','A. Gharbi','A2','SO.10','lecture',7,1,17,1,NULL,1),(403,'BCOR 230','Thursday','11:30:00','13:00:00','A. Gharbi','A2','SO.10','lecture',7,2,18,1,NULL,1),(404,'777','Friday','10:00:00','11:30:00','Sadok Laajimi','A4','SO.10','tutorial',8,3,22,5,673,NULL),(405,'BCOR 230','Friday','11:30:00','13:00:00','unknown','S32','SO.10','tutorial',7,3,23,2,393,NULL),(406,'BCOR 230','Monday','10:00:00','11:30:00','unknown','S32','SO.11','tutorial',7,3,2,2,393,NULL),(407,'777','Monday','13:30:00','15:00:00','Manara Toukabri','S39','SO.11','tutorial',8,3,4,2,113,NULL),(408,'BCOR 200','Tuesday','10:00:00','11:30:00','S. Ben Abdallah','A8','SO.11','lecture',5,1,7,3,NULL,3),(410,'777','Wednesday','10:00:00','11:30:00','R. Esghaier','A6','SO.11','lecture',8,1,12,1,NULL,1),(412,'BCOR 230','Thursday','10:00:00','11:30:00','A. Gharbi','A2','SO.11','lecture',7,2,17,1,NULL,1),(414,'888','Thursday','13:30:00','15:00:00','M.Abdelmoulah','Lab6','SO.11','lecture',10,1,19,4,NULL,5),(416,'BCOR 210','Friday','08:30:00','10:00:00','N. Belaid','A1','SO.11','lecture',6,2,21,3,NULL,3),(422,'BCOR 200','Tuesday','10:00:00','11:30:00','S. Ben Abdallah','A8','SO.11','lecture',5,2,7,3,NULL,3),(424,'777','Wednesday','10:00:00','11:30:00','R. Esghaier','A6','SO.11','lecture',8,2,12,1,NULL,1),(426,'BCOR 230','Thursday','10:00:00','11:30:00','A. Gharbi','A2','SO.11','lecture',7,1,17,1,NULL,1),(428,'888','Thursday','13:30:00','15:00:00','M.Abdelmoulah','Lab6','SO.11','lecture',10,2,19,4,NULL,5),(430,'BCOR 210','Friday','08:30:00','10:00:00','N. Belaid','A1','SO.11','lecture',6,1,21,3,NULL,3),(462,'777','Monday','13:30:00','15:00:00','R. Esghaier','A2','SO.12','lecture',8,1,4,1,NULL,1),(463,'777','Monday','15:00:00','16:30:00','R. Esghaier','A2','SO.12','lecture',8,2,5,1,NULL,1),(464,'BCOR 200','Tuesday','10:00:00','11:30:00','S. Ben Abdallah','A8','SO.12','lecture',5,1,7,3,NULL,3),(465,'BCOR 200','Tuesday','11:30:00','13:00:00','S. Ben Abdallah','A8','SO.12','lecture',5,2,8,3,NULL,3),(466,'888','Tuesday','13:30:00','15:00:00','M. Zayen','Lab6','SO.12','lecture',10,1,9,3,NULL,6),(467,'888','Tuesday','15:00:00','16:30:00','M. Zayen','Lab6','SO.12','lecture',10,2,10,3,NULL,6),(468,'BCOR 230','Thursday','10:00:00','11:30:00','A. Gharbi','A2','SO.12','lecture',7,1,17,1,NULL,1),(469,'BCOR 230','Thursday','11:30:00','13:00:00','A. Gharbi','A2','SO.12','lecture',7,2,18,1,NULL,1),(470,'BCOR 230','Thursday','15:00:00','16:30:00','unknown','S32','SO.12','tutorial',7,3,20,2,393,NULL),(471,'BCOR 210','Friday','08:30:00','10:00:00','N. Belaid','A1','SO.12','lecture',6,1,21,3,NULL,3),(472,'BCOR 210','Friday','10:00:00','11:30:00','N. Belaid','A1','SO.12','lecture',6,2,22,3,NULL,3),(473,'777','Friday','11:30:00','13:00:00','Sadok Laajimi','A4','SO.12','tutorial',8,3,23,5,673,NULL),(479,'BA 350','Thursday','10:00:00','11:30:00','A. Dridi','A5','Ju. BA/IT','lecture',16,1,17,1,NULL,1),(480,'BA 350','Thursday','11:30:00','13:00:00','A. Dridi','A5','Ju. BA/IT','lecture',16,2,18,1,NULL,1),(481,'BA 350','Friday','10:00:00','11:30:00','L. Issaoui','32','Ju. BA/IT','tutorial',16,3,22,7,7,NULL),(485,'BA 350','Tuesday','10:00:00','11:30:00','F. Talmoudi','A7','Ju. BA/IBE','lecture',16,1,7,3,NULL,3),(486,'BA 350','Tuesday','11:30:00','13:00:00','F. Talmoudi','A7','Ju. BA/IBE','lecture',16,2,8,2,NULL,2),(487,'BA 350','Friday','11:30:00','13:00:00','L. Issaoui','S15','Ju. BA/IBE','tutorial',16,3,23,7,7,NULL),(488,'BA 350','Thursday','10:00:00','11:30:00','A. Dridi','A5','Ju. BA/MRK','lecture',16,1,17,1,NULL,1),(489,'BA 350','Thursday','11:30:00','13:00:00','A. Dridi','A5','Ju. BA/MRK','lecture',16,2,18,1,NULL,1),(490,'BA 350','Tuesday','10:00:00','11:30:00','L. Issaoui','32','Ju. BA/MRK','tutorial',16,3,7,7,7,NULL),(491,'BA 350','Tuesday','10:00:00','11:30:00','F. Talmoudi','A7','Ju. IT/BA','lecture',16,1,7,3,NULL,3),(492,'BA 350','Tuesday','11:30:00','13:00:00','F. Talmoudi','A7','Ju. IT/BA','lecture',16,2,8,2,NULL,2),(493,'BA 350','Tuesday','08:30:00','10:00:00','L. Issaoui','32','Ju. IT/BA','tutorial',16,3,6,7,7,NULL),(494,'BA 350','Thursday','10:00:00','11:30:00','A. Dridi','A5','Ju. BA/FIN','lecture',16,1,17,1,NULL,1),(495,'BA 350','Thursday','11:30:00','13:00:00','A. Dridi','A5','Ju. BA/FIN','lecture',16,2,18,1,NULL,1),(496,'BA 350','Friday','08:30:00','10:00:00','L. Issaoui','15','Ju. BA/FIN','tutorial',16,3,21,7,7,NULL),(497,'BA 350','Tuesday','10:00:00','11:30:00','R. Aloui','Lab 10','Ju. FIN/BA','lecture',16,1,7,3,NULL,2),(498,'BA 350','Tuesday','11:30:00','13:00:00','R. Aloui','Lab 10','Ju. FIN/BA','lecture',16,2,8,3,NULL,2),(499,'BA 350','Thursday','11:30:00','13:00:00','X','Y','Ju. FIN/BA','tutorial',16,3,18,3,2,NULL);
/*!40000 ALTER TABLE `schedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schedule_parameters`
--

DROP TABLE IF EXISTS `schedule_parameters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schedule_parameters` (
  `id` int NOT NULL AUTO_INCREMENT,
  `weight_mode_a` decimal(5,2) NOT NULL,
  `weight_mode_b` int NOT NULL,
  `maximum_solutions` int DEFAULT NULL,
  `time_limit` int DEFAULT NULL,
  `penalty_gap` int DEFAULT NULL,
  `schedule_validation` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schedule_parameters`
--

LOCK TABLES `schedule_parameters` WRITE;
/*!40000 ALTER TABLE `schedule_parameters` DISABLE KEYS */;
INSERT INTO `schedule_parameters` VALUES (1,10.00,1,10,20,100,0);
/*!40000 ALTER TABLE `schedule_parameters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `student_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(40) NOT NULL,
  `last_name` varchar(40) NOT NULL,
  `national_id` int NOT NULL,
  `enrollment_status` enum('enrolled','graduated','dismissed','transferred') DEFAULT 'enrolled',
  `email_address` varchar(80) NOT NULL,
  `password` varchar(255) NOT NULL,
  `year_of_study` int DEFAULT NULL,
  `level` varchar(20) DEFAULT 'Freshman',
  `major` enum('ACCT','BA','FIN','IT','MRK') DEFAULT NULL,
  `second_major` enum('ACCT','BA','FIN','IT','MRK') DEFAULT NULL,
  `minor` enum('ACCT','BA','FIN','IT','MRK','IBE') DEFAULT NULL,
  `second_minor` enum('ACCT','BA','FIN','IT','MRK','IBE') DEFAULT NULL,
  `group` varchar(50) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `profile_picture` longblob,
  `non_french` tinyint(1) DEFAULT '0',
  `eligible_for_major` tinyint NOT NULL DEFAULT '0',
  `is_new_student` tinyint(1) DEFAULT '1',
  `secondary_email_address` varchar(80) DEFAULT NULL,
  `email_confirmed` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`student_id`),
  UNIQUE KEY `national_id` (`national_id`),
  UNIQUE KEY `email_address` (`email_address`),
  CONSTRAINT `chk_major_minor_different` CHECK (((`major` is null) or (`minor` is null) or (`major` <> `minor`))),
  CONSTRAINT `chk_major_second_major` CHECK (((`major` is null) or (`second_major` is null) or (`major` <> `second_major`))),
  CONSTRAINT `chk_major_second_minor` CHECK (((`major` is null) or (`second_minor` is null) or (`major` <> `second_minor`))),
  CONSTRAINT `chk_minor_second_minor` CHECK (((`minor` is null) or (`second_minor` is null) or (`minor` <> `second_minor`)))
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES (1,'szdefrghj','azerth',12345678,'enrolled','ali@gmail.com','scrypt:32768:8:1$zwiTT1nDgMMuDVpH$146888d0eda021263e35d052cbec4a40f7738b0cb8f90ad790847b30a6e4277157527f7dbb04b17bdeca3d7ddfad2b8803a73872962316147ba884cdae2a7a7e',1,'Freshman',NULL,NULL,'BA',NULL,NULL,NULL,NULL,0,0,0,NULL,0),(2,'zefrgthyj','szdfghj',34567890,'enrolled','youssef@gmail.com','scrypt:32768:8:1$fG3RBaLZsECaVlPz$073c309c95f7215bd13e81d70b3c3c79f290344f6dd7a20291bd270b766eb4501f4692b7410a04f03c3dc6b6d655a1a93af7d5da0922345d94fb5ea8bf3ff9d7',1,'Freshman',NULL,'BA',NULL,NULL,NULL,NULL,NULL,0,0,0,NULL,0),(3,'TBSer','TBSer',23456789,'enrolled','test.test@tbs.u-tunis.tn','scrypt:32768:8:1$gwOqyIIvmAz4pyUk$81e90554eb2c0bab049ab8856a0e958693def15edf441eb5a7f07d0841df610003a54b9d41d73dbc3ce7c7b5870ccbe94a929205bd288f94502e8afed07f52bd',4,'Junior','FIN',NULL,'BA',NULL,'--','555-123-4567',NULL,1,1,0,'',1),(4,'Noah','Brown',456789012,'enrolled','noah.brown@univ.edu','hashed_password4',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33456789012',NULL,0,1,0,NULL,0),(5,'Ava','Jones',567890123,'enrolled','ava.jones@univ.edu','hashed_password5',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33567890123',NULL,0,1,0,NULL,0),(6,'William','Garcia',678901234,'enrolled','william.garcia@univ.edu','hashed_password6',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33678901234',NULL,1,1,0,NULL,0),(7,'Sophia','Miller',789012345,'enrolled','sophia.miller@univ.edu','hashed_password7',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33789012345',NULL,0,0,0,NULL,0),(8,'Benjamin','Davis',890123456,'enrolled','benjamin.davis@univ.edu','hashed_password8',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33890123456',NULL,0,1,0,NULL,0),(9,'Isabella','Rodriguez',901234567,'enrolled','isabella.rodriguez@univ.edu','hashed_password9',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33901234567',NULL,1,1,0,NULL,0),(10,'Lucas','Martinez',123456780,'enrolled','lucas.martinez@univ.edu','hashed_password10',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33123456780',NULL,0,1,0,NULL,0),(11,'Mia','Hernandez',234567891,'enrolled','mia.hernandez@univ.edu','hashed_password11',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33234567891',NULL,0,0,0,NULL,0),(12,'Henry','Lopez',345678902,'enrolled','henry.lopez@univ.edu','hashed_password12',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33345678902',NULL,1,1,0,NULL,0),(13,'Charlotte','Gonzalez',456789013,'enrolled','charlotte.gonzalez@univ.edu','hashed_password13',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33456789013',NULL,0,1,0,NULL,0),(14,'Alexander','Wilson',567890124,'enrolled','alexander.wilson@univ.edu','hashed_password14',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33567890124',NULL,0,1,0,NULL,0),(15,'Amelia','Anderson',678901235,'enrolled','amelia.anderson@univ.edu','hashed_password15',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33678901235',NULL,1,0,0,NULL,0),(16,'James','Thomas',789012346,'enrolled','james.thomas@univ.edu','hashed_password16',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33789012346',NULL,0,1,0,NULL,0),(17,'Harper','Taylor',890123457,'enrolled','harper.taylor@univ.edu','hashed_password17',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33890123457',NULL,0,1,0,NULL,0),(18,'Michael','Moore',901234568,'enrolled','michael.moore@univ.edu','hashed_password18',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33901234568',NULL,1,1,0,NULL,0),(19,'Evelyn','Jackson',123456781,'enrolled','evelyn.jackson@univ.edu','hashed_password19',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33123456781',NULL,0,1,0,NULL,0),(20,'Daniel','Martin',234567892,'enrolled','daniel.martin@univ.edu','hashed_password20',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33234567892',NULL,0,0,0,NULL,0),(21,'Abigail','Lee',345678903,'enrolled','abigail.lee@univ.edu','hashed_password21',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33345678903',NULL,1,1,0,NULL,0),(22,'Logan','Perez',456789014,'enrolled','logan.perez@univ.edu','hashed_password22',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33456789014',NULL,0,1,0,NULL,0),(23,'Emily','Thompson',567890125,'enrolled','emily.thompson@univ.edu','hashed_password23',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33567890125',NULL,0,1,0,NULL,0),(24,'Jacob','White',678901236,'enrolled','jacob.white@univ.edu','hashed_password24',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33678901236',NULL,1,1,0,NULL,0),(25,'Elizabeth','Harris',789012347,'enrolled','elizabeth.harris@univ.edu','hashed_password25',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33789012347',NULL,0,0,0,NULL,0),(26,'Elijah','Sanchez',890123458,'enrolled','elijah.sanchez@univ.edu','hashed_password26',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33890123458',NULL,0,1,0,NULL,0),(27,'Sofia','Clark',901234569,'enrolled','sofia.clark@univ.edu','hashed_password27',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33901234569',NULL,1,1,0,NULL,0),(28,'Matthew','Ramirez',123456782,'enrolled','matthew.ramirez@univ.edu','hashed_password28',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33123456782',NULL,0,1,0,NULL,0),(29,'Avery','Lewis',234567893,'enrolled','avery.lewis@univ.edu','hashed_password29',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33234567893',NULL,0,1,0,NULL,0),(30,'Ella','Robinson',345678904,'enrolled','ella.robinson@univ.edu','hashed_password30',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33345678904',NULL,1,0,0,NULL,0),(31,'David','Walker',456789015,'enrolled','david.walker@univ.edu','hashed_password31',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33456789015',NULL,0,1,0,NULL,0),(32,'Scarlett','Young',567890126,'enrolled','scarlett.young@univ.edu','hashed_password32',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33567890126',NULL,0,1,0,NULL,0),(33,'Joseph','Allen',678901237,'enrolled','joseph.allen@univ.edu','hashed_password33',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33678901237',NULL,1,1,0,NULL,0),(34,'Victoria','King',789012348,'enrolled','victoria.king@univ.edu','hashed_password34',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33789012348',NULL,0,1,0,NULL,0),(35,'Jackson','Wright',890123459,'enrolled','jackson.wright@univ.edu','hashed_password35',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33890123459',NULL,0,0,0,NULL,0),(36,'Grace','Scott',901234570,'enrolled','grace.scott@univ.edu','hashed_password36',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33901234570',NULL,1,1,0,NULL,0),(37,'Samuel','Torres',123456783,'enrolled','samuel.torres@univ.edu','hashed_password37',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33123456783',NULL,0,1,0,NULL,0),(38,'Chloe','Nguyen',234567894,'enrolled','chloe.nguyen@univ.edu','hashed_password38',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33234567894',NULL,0,1,0,NULL,0),(39,'Sebastian','Hill',345678905,'enrolled','sebastian.hill@univ.edu','hashed_password39',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33345678905',NULL,1,1,0,NULL,0),(40,'Madison','Flores',456789016,'enrolled','madison.flores@univ.edu','hashed_password40',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33456789016',NULL,0,0,0,NULL,0),(41,'Aiden','Green',567890127,'enrolled','aiden.green@univ.edu','hashed_password41',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33567890127',NULL,0,1,0,NULL,0),(42,'Lily','Adams',678901238,'enrolled','lily.adams@univ.edu','hashed_password42',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33678901238',NULL,1,1,0,NULL,0),(43,'Owen','Nelson',789012349,'enrolled','owen.nelson@univ.edu','hashed_password43',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33789012349',NULL,0,1,0,NULL,0),(44,'Zoey','Baker',890123460,'enrolled','zoey.baker@univ.edu','hashed_password44',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33890123460',NULL,0,1,0,NULL,0),(45,'John','Hall',901234571,'enrolled','john.hall@univ.edu','hashed_password45',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33901234571',NULL,1,0,0,NULL,0),(46,'Penelope','Rivera',123456784,'enrolled','penelope.rivera@univ.edu','hashed_password46',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33123456784',NULL,0,1,0,NULL,0),(47,'Luke','Campbell',234567895,'enrolled','luke.campbell@univ.edu','hashed_password47',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33234567895',NULL,0,1,0,NULL,0),(48,'Layla','Mitchell',345678906,'enrolled','layla.mitchell@univ.edu','hashed_password48',1,'Freshman',NULL,NULL,NULL,NULL,'A','+33345678906',NULL,1,1,0,NULL,0),(49,'Dylan','Carter',456789017,'enrolled','dylan.carter@univ.edu','hashed_password49',1,'Freshman',NULL,NULL,NULL,NULL,'C','+33456789017',NULL,0,1,0,NULL,0),(50,'Nora','Roberts',567890128,'enrolled','nora.roberts@univ.edu','hashed_password50',1,'Freshman',NULL,NULL,NULL,NULL,'B','+33567890128',NULL,0,0,0,NULL,0),(57,'Ryan','Barnes',345678915,'enrolled','ryan.barnes@univ.edu','$2a$10$N9qo8uLOickgx2ZMRZoMy.MQDq3WJkOFsJQ9Vn7FNEq.4gVO6X7K',23,'Freshman',NULL,NULL,NULL,NULL,'F','+33345678915',NULL,1,1,0,NULL,0),(70,'Tbser','Tbser',88888888,'enrolled','spooqibear@gmail.com','scrypt:32768:8:1$djOm0nnlrtEcMrye$6c1e8ebe74bfaeeb5f73b62d6e1047d88f318a3276e6d423719f7b8828708d283a96600fb7ba1349434ee92c63bf3d7a787e59a571504658d9e7c8ed6182e58d',1,'Freshman',NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,1,NULL,0),(71,'Grad1','Student',10000001,'graduated','grad1@example.com','hashed_pw',1,'Freshman','ACCT',NULL,NULL,NULL,'G1','00000001',NULL,0,1,0,'grad1b@example.com',1),(72,'Grad2','Student',10000002,'graduated','grad2@example.com','hashed_pw',1,'Freshman','BA',NULL,NULL,NULL,'G2','00000002',NULL,0,1,0,'grad2b@example.com',1),(73,'Grad3','Student',10000003,'graduated','grad3@example.com','hashed_pw',1,'Freshman','FIN',NULL,NULL,NULL,'G3','00000003',NULL,0,1,0,'grad3b@example.com',1),(74,'Grad4','Student',10000004,'graduated','grad4@example.com','hashed_pw',1,'Freshman','IT',NULL,NULL,NULL,'G4','00000004',NULL,0,1,0,'grad4b@example.com',1),(75,'Grad5','Student',10000005,'graduated','grad5@example.com','hashed_pw',1,'Freshman','MRK',NULL,NULL,NULL,'G5','00000005',NULL,0,1,0,'grad5b@example.com',1),(76,'Grad6','Student',10000006,'graduated','grad6@example.com','hashed_pw',1,'Freshman','ACCT',NULL,NULL,NULL,'G6','00000006',NULL,0,1,0,'grad6b@example.com',1),(77,'Grad7','Student',10000007,'graduated','grad7@example.com','hashed_pw',1,'Freshman','BA',NULL,NULL,NULL,'G7','00000007',NULL,0,1,0,'grad7b@example.com',1),(78,'Grad8','Student',10000008,'graduated','grad8@example.com','hashed_pw',1,'Freshman','IT',NULL,NULL,NULL,'G8','00000008',NULL,0,1,0,'grad8b@example.com',1),(79,'Grad9','Student',10000009,'graduated','grad9@example.com','hashed_pw',1,'Freshman','ACCT',NULL,NULL,NULL,'G1','00000009',NULL,0,1,0,'grad9b@example.com',1),(80,'Grad10','Student',10000010,'graduated','grad10@example.com','hashed_pw',1,'Freshman','FIN',NULL,NULL,NULL,'G2','00000010',NULL,0,1,0,'grad10b@example.com',1),(81,'Grad11','Student',10000011,'graduated','grad11@example.com','hashed_pw',1,'Freshman','MRK',NULL,NULL,NULL,'G3','00000011',NULL,0,1,0,'grad11b@example.com',1),(82,'Grad12','Student',10000012,'graduated','grad12@example.com','hashed_pw',1,'Freshman','IT',NULL,NULL,NULL,'G4','00000012',NULL,0,1,0,'grad12b@example.com',1),(83,'Grad13','Student',10000013,'graduated','grad13@example.com','hashed_pw',1,'Freshman','BA',NULL,NULL,NULL,'G1','00000013',NULL,0,1,0,'grad13b@example.com',1),(84,'Grad14','Student',10000014,'graduated','grad14@example.com','hashed_pw',1,'Freshman','ACCT',NULL,NULL,NULL,'G2','00000014',NULL,0,1,0,'grad14b@example.com',1),(85,'Grad15','Student',10000015,'graduated','grad15@example.com','hashed_pw',1,'Freshman','FIN',NULL,NULL,NULL,'G3','00000015',NULL,0,1,0,'grad15b@example.com',1);
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_parameters_overrides`
--

DROP TABLE IF EXISTS `student_parameters_overrides`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_parameters_overrides` (
  `student_id` int NOT NULL,
  `max_courses_per_semester` int DEFAULT NULL,
  `min_credit_percentage_major` decimal(6,3) DEFAULT NULL,
  `min_gpa_acct` decimal(5,4) DEFAULT NULL,
  `min_gpa_ba` decimal(5,4) DEFAULT NULL,
  `min_gpa_fin` decimal(5,4) DEFAULT NULL,
  `min_gpa_it` decimal(5,4) DEFAULT NULL,
  `min_gpa_mrk` decimal(5,4) DEFAULT NULL,
  `max_forgiveness_uses` int DEFAULT NULL,
  `max_probation_board` int DEFAULT NULL,
  `max_probation_total` int DEFAULT NULL,
  PRIMARY KEY (`student_id`),
  CONSTRAINT `student_parameters_overrides_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_parameters_overrides`
--

LOCK TABLES `student_parameters_overrides` WRITE;
/*!40000 ALTER TABLE `student_parameters_overrides` DISABLE KEYS */;
INSERT INTO `student_parameters_overrides` VALUES (1,NULL,NULL,3.0000,NULL,NULL,NULL,NULL,NULL,NULL,NULL),(31,NULL,NULL,NULL,NULL,NULL,NULL,NULL,5,NULL,NULL);
/*!40000 ALTER TABLE `student_parameters_overrides` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_schedules`
--

DROP TABLE IF EXISTS `student_schedules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_schedules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `enrolled_courses_key` varchar(500) NOT NULL,
  `schedule_data` mediumtext NOT NULL,
  `semester` int DEFAULT NULL,
  `year` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `previous_solutions` text,
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`,`enrolled_courses_key`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_schedules`
--

LOCK TABLES `student_schedules` WRITE;
/*!40000 ALTER TABLE `student_schedules` DISABLE KEYS */;
INSERT INTO `student_schedules` VALUES (1,3,'','[{\"classroom\": \"A2\", \"course_code\": \"BCOR 230\", \"course_index\": 7, \"day\": \"Monday\", \"end_time\": \"11:30\", \"group\": \"SO.6\", \"option_id\": 308, \"professor\": \"A. Gharbi\", \"professor_index\": 1, \"session_number\": 1, \"session_type\": \"lecture\", \"start_time\": \"10:00\", \"time_slot\": 2}, {\"classroom\": \"A2\", \"course_code\": \"BCOR 230\", \"course_index\": 7, \"day\": \"Monday\", \"end_time\": \"13:00\", \"group\": \"SO.6\", \"option_id\": 309, \"professor\": \"A. Gharbi\", \"professor_index\": 1, \"session_number\": 2, \"session_type\": \"lecture\", \"start_time\": \"11:30\", \"time_slot\": 3}, {\"classroom\": \"S20\", \"course_code\": \"NBC 210\", \"course_index\": 13, \"day\": \"Tuesday\", \"end_time\": \"11:30\", \"group\": \"SO.6\", \"option_id\": 310, \"professor\": \"L. Rezgui\", \"professor_index\": 3, \"session_number\": 1, \"session_type\": \"lecture\", \"start_time\": \"10:00\", \"time_slot\": 7}, {\"classroom\": \"S20\", \"course_code\": \"NBC 210\", \"course_index\": 13, \"day\": \"Tuesday\", \"end_time\": \"13:00\", \"group\": \"SO.6\", \"option_id\": 311, \"professor\": \"L. Rezgui\", \"professor_index\": 3, \"session_number\": 2, \"session_type\": \"lecture\", \"start_time\": \"11:30\", \"time_slot\": 8}, {\"classroom\": \"Lab3\", \"course_code\": \"CS 220\", \"course_index\": 10, \"day\": \"Tuesday\", \"end_time\": \"15:00\", \"group\": \"SO.6\", \"option_id\": 312, \"professor\": \"Amel B.Yaghlene\", \"professor_index\": 2, \"session_number\": 1, \"session_type\": \"lecture\", \"start_time\": \"13:30\", \"time_slot\": 9}, {\"classroom\": \"Lab3\", \"course_code\": \"CS 220\", \"course_index\": 10, \"day\": \"Tuesday\", \"end_time\": \"16:30\", \"group\": \"SO.6\", \"option_id\": 313, \"professor\": \"Amel B.Yaghlene\", \"professor_index\": 2, \"session_number\": 2, \"session_type\": \"lecture\", \"start_time\": \"15:00\", \"time_slot\": 10}, {\"classroom\": \"A6\", \"course_code\": \"BCOR 260\", \"course_index\": 8, \"day\": \"Wednesday\", \"end_time\": \"11:30\", \"group\": \"SO.6\", \"option_id\": 314, \"professor\": \"R. Esghaier\", \"professor_index\": 1, \"session_number\": 1, \"session_type\": \"lecture\", \"start_time\": \"10:00\", \"time_slot\": 12}, {\"classroom\": \"A6\", \"course_code\": \"BCOR 260\", \"course_index\": 8, \"day\": \"Wednesday\", \"end_time\": \"13:00\", \"group\": \"SO.6\", \"option_id\": 315, \"professor\": \"R. Esghaier\", \"professor_index\": 1, \"session_number\": 2, \"session_type\": \"lecture\", \"start_time\": \"11:30\", \"time_slot\": 13}, {\"classroom\": \"S32\", \"course_code\": \"BCOR 230\", \"course_index\": 7, \"day\": \"Thursday\", \"end_time\": \"11:30\", \"group\": \"SO.6\", \"option_id\": 316, \"professor\": \"X\", \"professor_index\": 1, \"session_number\": 3, \"session_type\": \"tutorial\", \"start_time\": \"10:00\", \"time_slot\": 17}, {\"classroom\": \"A7\", \"course_code\": \"BCOR 210\", \"course_index\": 6, \"day\": \"Thursday\", \"end_time\": \"15:00\", \"group\": \"SO.6\", \"option_id\": 317, \"professor\": \"N. Belaid\", \"professor_index\": 3, \"session_number\": 1, \"session_type\": \"lecture\", \"start_time\": \"13:30\", \"time_slot\": 19}, {\"classroom\": \"A7\", \"course_code\": \"BCOR 210\", \"course_index\": 6, \"day\": \"Thursday\", \"end_time\": \"16:30\", \"group\": \"SO.6\", \"option_id\": 318, \"professor\": \"N. Belaid\", \"professor_index\": 3, \"session_number\": 2, \"session_type\": \"lecture\", \"start_time\": \"15:00\", \"time_slot\": 20}, {\"classroom\": \"A4\", \"course_code\": \"BCOR 260\", \"course_index\": 8, \"day\": \"Friday\", \"end_time\": \"11:30\", \"group\": \"SO.6\", \"option_id\": 319, \"professor\": \"Sadok Laajimi\", \"professor_index\": 5, \"session_number\": 3, \"session_type\": \"tutorial\", \"start_time\": \"10:00\", \"time_slot\": 22}, {\"classroom\": \"A2\", \"course_code\": \"BCOR 200\", \"course_index\": 5, \"day\": \"Friday\", \"end_time\": \"15:00\", \"group\": \"SO.6\", \"option_id\": 320, \"professor\": \"G. Aydi\", \"professor_index\": 1, \"session_number\": 1, \"session_type\": \"lecture\", \"start_time\": \"13:30\", \"time_slot\": 24}, {\"classroom\": \"A2\", \"course_code\": \"BCOR 200\", \"course_index\": 5, \"day\": \"Friday\", \"end_time\": \"16:30\", \"group\": \"SO.6\", \"option_id\": 321, \"professor\": \"G. Aydi\", \"professor_index\": 1, \"session_number\": 2, \"session_type\": \"lecture\", \"start_time\": \"15:00\", \"time_slot\": 25}]',2,2184,'2025-06-25 06:46:27',NULL),(2,3,'','[{\"classroom\": \"A5\", \"course_code\": \"BA 350\", \"course_index\": 16, \"day\": \"Thursday\", \"end_time\": \"11:30\", \"group\": \"Ju. BA/IT\", \"option_id\": 479, \"professor\": \"A. Dridi\", \"professor_index\": 1, \"session_number\": 1, \"session_type\": \"lecture\", \"start_time\": \"10:00\", \"time_slot\": 17}, {\"classroom\": \"A5\", \"course_code\": \"BA 350\", \"course_index\": 16, \"day\": \"Thursday\", \"end_time\": \"13:00\", \"group\": \"Ju. BA/IT\", \"option_id\": 480, \"professor\": \"A. Dridi\", \"professor_index\": 1, \"session_number\": 2, \"session_type\": \"lecture\", \"start_time\": \"11:30\", \"time_slot\": 18}, {\"classroom\": \"32\", \"course_code\": \"BA 350\", \"course_index\": 16, \"day\": \"Friday\", \"end_time\": \"11:30\", \"group\": \"Ju. BA/IT\", \"option_id\": 481, \"professor\": \"L. Issaoui\", \"professor_index\": 7, \"session_number\": 3, \"session_type\": \"tutorial\", \"start_time\": \"10:00\", \"time_slot\": 22}]',1,2186,'2025-06-25 14:04:30',NULL),(3,3,'','[{\"classroom\": \"A2\", \"course_code\": \"BCOR 260\", \"course_index\": 8, \"day\": \"Monday\", \"end_time\": \"15:00\", \"group\": \"SO.2\", \"option_id\": 254, \"professor\": \"R. Esghaier\", \"professor_index\": 1, \"session_number\": 1, \"session_type\": \"lecture\", \"start_time\": \"13:30\", \"time_slot\": 4}, {\"classroom\": \"A2\", \"course_code\": \"BCOR 260\", \"course_index\": 8, \"day\": \"Monday\", \"end_time\": \"16:30\", \"group\": \"SO.2\", \"option_id\": 255, \"professor\": \"R. Esghaier\", \"professor_index\": 1, \"session_number\": 2, \"session_type\": \"lecture\", \"start_time\": \"15:00\", \"time_slot\": 5}, {\"classroom\": \"S32\", \"course_code\": \"BCOR 140\", \"course_index\": 3, \"day\": \"Tuesday\", \"end_time\": \"11:30\", \"group\": \"F.12\", \"option_id\": 227, \"professor\": \"H. Medyouni\", \"professor_index\": 1, \"session_number\": 3, \"session_type\": \"tutorial\", \"start_time\": \"10:00\", \"time_slot\": 7}, {\"classroom\": \"S12\", \"course_code\": \"NBC 210\", \"course_index\": 13, \"day\": \"Wednesday\", \"end_time\": \"11:30\", \"group\": \"SO.7\", \"option_id\": 328, \"professor\": \"B. Elkaou\", \"professor_index\": 1, \"session_number\": 1, \"session_type\": \"lecture\", \"start_time\": \"10:00\", \"time_slot\": 12}, {\"classroom\": \"S12\", \"course_code\": \"NBC 210\", \"course_index\": 13, \"day\": \"Wednesday\", \"end_time\": \"13:00\", \"group\": \"SO.7\", \"option_id\": 329, \"professor\": \"B. Elkaou\", \"professor_index\": 1, \"session_number\": 2, \"session_type\": \"lecture\", \"start_time\": \"11:30\", \"time_slot\": 13}, {\"classroom\": \"A2\", \"course_code\": \"BCOR 230\", \"course_index\": 7, \"day\": \"Thursday\", \"end_time\": \"11:30\", \"group\": \"SO.4\", \"option_id\": 288, \"professor\": \"A. Gharbi\", \"professor_index\": 1, \"session_number\": 1, \"session_type\": \"lecture\", \"start_time\": \"10:00\", \"time_slot\": 17}, {\"classroom\": \"A2\", \"course_code\": \"BCOR 230\", \"course_index\": 7, \"day\": \"Thursday\", \"end_time\": \"13:00\", \"group\": \"SO.4\", \"option_id\": 289, \"professor\": \"A. Gharbi\", \"professor_index\": 1, \"session_number\": 2, \"session_type\": \"lecture\", \"start_time\": \"11:30\", \"time_slot\": 18}, {\"classroom\": \"A7\", \"course_code\": \"BCOR 210\", \"course_index\": 6, \"day\": \"Thursday\", \"end_time\": \"15:00\", \"group\": \"SO.1\", \"option_id\": 249, \"professor\": \"H. Zouaoui\", \"professor_index\": 1, \"session_number\": 1, \"session_type\": \"lecture\", \"start_time\": \"13:30\", \"time_slot\": 19}, {\"classroom\": \"A7\", \"course_code\": \"BCOR 210\", \"course_index\": 6, \"day\": \"Thursday\", \"end_time\": \"16:30\", \"group\": \"SO.1\", \"option_id\": 250, \"professor\": \"H. Zouaoui\", \"professor_index\": 1, \"session_number\": 2, \"session_type\": \"lecture\", \"start_time\": \"15:00\", \"time_slot\": 20}, {\"classroom\": \"S32\", \"course_code\": \"BCOR 230\", \"course_index\": 7, \"day\": \"Friday\", \"end_time\": \"10:00\", \"group\": \"SO.7\", \"option_id\": 332, \"professor\": \"X\", \"professor_index\": 1, \"session_number\": 3, \"session_type\": \"tutorial\", \"start_time\": \"08:30\", \"time_slot\": 21}, {\"classroom\": \"A2\", \"course_code\": \"BCOR 200\", \"course_index\": 5, \"day\": \"Friday\", \"end_time\": \"11:30\", \"group\": \"SO.4\", \"option_id\": 292, \"professor\": \"G. Aydi\", \"professor_index\": 1, \"session_number\": 1, \"session_type\": \"lecture\", \"start_time\": \"10:00\", \"time_slot\": 22}, {\"classroom\": \"A2\", \"course_code\": \"BCOR 200\", \"course_index\": 5, \"day\": \"Friday\", \"end_time\": \"13:00\", \"group\": \"SO.4\", \"option_id\": 293, \"professor\": \"G. Aydi\", \"professor_index\": 1, \"session_number\": 2, \"session_type\": \"lecture\", \"start_time\": \"11:30\", \"time_slot\": 23}, {\"classroom\": \"A1\", \"course_code\": \"BCOR 140\", \"course_index\": 3, \"day\": \"Friday\", \"end_time\": \"15:00\", \"group\": \"F.4\", \"option_id\": 67, \"professor\": \"B. Guizani\", \"professor_index\": 1, \"session_number\": 1, \"session_type\": \"lecture\", \"start_time\": \"13:30\", \"time_slot\": 24}, {\"classroom\": \"A1\", \"course_code\": \"BCOR 140\", \"course_index\": 3, \"day\": \"Friday\", \"end_time\": \"16:30\", \"group\": \"F.4\", \"option_id\": 68, \"professor\": \"B. Guizani\", \"professor_index\": 1, \"session_number\": 2, \"session_type\": \"lecture\", \"start_time\": \"15:00\", \"time_slot\": 25}]',2,2191,'2025-07-03 10:26:48',NULL);
/*!40000 ALTER TABLE `student_schedules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_semester_summary`
--

DROP TABLE IF EXISTS `student_semester_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_semester_summary` (
  `record_id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `year` int NOT NULL,
  `semester` tinyint NOT NULL,
  `registered_credits` decimal(5,2) DEFAULT '0.00',
  `earned_credits` decimal(5,2) DEFAULT '0.00',
  `semester_gpa` decimal(4,2) DEFAULT '0.00',
  `cumulative_registered_credits` decimal(6,2) DEFAULT '0.00',
  `cumulative_earned_credits` decimal(6,2) DEFAULT '0.00',
  `cumulative_gpa` decimal(4,2) DEFAULT '0.00',
  `probation_counter` int DEFAULT '0',
  `forgiveness_counter` int DEFAULT '0',
  `acct_gpa` decimal(6,4) DEFAULT NULL,
  `ba_gpa` decimal(6,4) DEFAULT NULL,
  `fin_gpa` decimal(6,4) DEFAULT NULL,
  `it_gpa` decimal(6,4) DEFAULT NULL,
  `mrk_gpa` decimal(6,4) DEFAULT NULL,
  PRIMARY KEY (`record_id`),
  UNIQUE KEY `student_semester_unique` (`student_id`,`year`,`semester`),
  CONSTRAINT `fk_student` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `student_semester_summary_chk_1` CHECK ((`semester` in (1,2,3)))
) ENGINE=InnoDB AUTO_INCREMENT=359 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_semester_summary`
--

LOCK TABLES `student_semester_summary` WRITE;
/*!40000 ALTER TABLE `student_semester_summary` DISABLE KEYS */;
INSERT INTO `student_semester_summary` VALUES (1,1,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(2,2,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(4,4,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(5,5,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(6,6,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(7,7,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(8,8,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(9,9,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(10,10,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(11,11,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(12,12,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(13,13,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(14,14,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(15,15,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(16,16,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(17,17,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(18,18,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(19,19,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(20,20,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(21,21,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(22,22,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(23,23,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(24,24,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(25,25,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(26,26,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(27,27,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(28,28,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(29,29,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(30,30,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(31,31,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(32,32,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(33,33,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(34,34,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(35,35,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(36,36,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(37,37,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(38,38,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(39,39,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(40,40,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(41,41,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(42,42,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(43,43,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(44,44,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(45,45,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(46,46,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(47,47,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(48,48,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(49,49,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(50,50,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(51,57,20,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(52,70,1,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(64,3,1,1,13.00,13.00,1.31,13.00,13.00,1.31,0,0,NULL,NULL,NULL,NULL,NULL),(72,1,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(73,2,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(74,3,1,2,17.00,14.00,1.56,30.00,27.00,1.45,0,0,NULL,NULL,NULL,NULL,NULL),(75,4,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(76,5,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(77,6,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(78,7,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(79,8,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(80,9,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(81,10,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(82,11,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(83,12,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(84,13,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(85,14,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(86,15,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(87,16,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(88,17,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(89,18,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(90,19,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(91,20,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(92,21,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(93,22,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(94,23,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(95,24,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(96,25,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(97,26,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(98,27,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(99,28,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(100,29,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(101,30,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(102,31,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(103,32,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(104,33,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(105,34,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(106,35,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(107,36,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(108,37,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(109,38,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(110,39,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(111,40,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(112,41,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(113,42,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(114,43,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(115,44,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(116,45,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(117,46,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(118,47,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(119,48,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(120,49,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(121,50,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(122,57,20,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(123,70,1,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(143,3,2,1,17.00,17.00,2.30,47.00,44.00,1.76,0,0,NULL,NULL,NULL,NULL,NULL),(144,57,21,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(152,3,2,2,20.00,20.00,3.00,67.00,64.00,2.13,1,0,2.8500,2.0000,2.2500,2.4000,2.1250),(153,57,21,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(270,3,3,1,18.00,18.00,3.00,85.00,82.00,2.31,0,0,NULL,NULL,NULL,NULL,NULL),(271,57,22,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(279,3,3,2,16.00,16.00,3.00,101.00,98.00,2.42,0,0,2.8500,2.0000,2.2500,2.4000,2.1250),(280,57,22,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(313,3,4,1,15.00,15.00,3.00,116.00,113.00,2.50,0,0,NULL,NULL,NULL,NULL,NULL),(314,57,23,1,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL),(321,3,4,2,0.00,0.00,0.00,116.00,113.00,2.50,0,0,2.8500,2.0000,2.2500,2.4000,2.1250),(322,57,23,2,0.00,0.00,0.00,0.00,0.00,NULL,0,0,NULL,NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `student_semester_summary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_parameters`
--

DROP TABLE IF EXISTS `system_parameters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_parameters` (
  `id` int NOT NULL,
  `max_courses_per_semester` int NOT NULL,
  `min_credit_percentage_major` decimal(6,3) NOT NULL,
  `min_gpa_acct` decimal(5,4) NOT NULL,
  `min_gpa_ba` decimal(5,4) NOT NULL,
  `min_gpa_fin` decimal(5,4) NOT NULL,
  `min_gpa_it` decimal(5,4) NOT NULL,
  `min_gpa_mrk` decimal(5,4) NOT NULL,
  `max_forgiveness_uses` int NOT NULL,
  `max_probation_board` int NOT NULL,
  `max_probation_total` int NOT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `min_cumulative_gpa` decimal(5,4) DEFAULT NULL,
  `minimum_grad_credit` int DEFAULT NULL,
  `minimum_grad_cgpa` decimal(5,4) DEFAULT NULL,
  `maximum_forgive_grade` decimal(2,1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `system_parameters_chk_1` CHECK ((`id` = 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_parameters`
--

LOCK TABLES `system_parameters` WRITE;
/*!40000 ALTER TABLE `system_parameters` DISABLE KEYS */;
INSERT INTO `system_parameters` VALUES (1,7,85.000,2.0000,2.0000,2.0000,2.0000,2.0000,4,3,4,'2025-06-21 23:58:41',2.0000,130,2.0000,1.7);
/*!40000 ALTER TABLE `system_parameters` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tbs_students`
--

DROP TABLE IF EXISTS `tbs_students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tbs_students` (
  `student_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(40) NOT NULL,
  `last_name` varchar(40) NOT NULL,
  `national_id` int NOT NULL,
  `email_address` varchar(80) NOT NULL,
  `password` varchar(255) NOT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `marital_status` enum('Single','Married','Divorced','Widowed') DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `contact_email` varchar(80) DEFAULT NULL,
  `tbs_email` varchar(80) DEFAULT NULL,
  `zip_code` varchar(10) DEFAULT NULL,
  `enrollment_id` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`student_id`),
  UNIQUE KEY `national_id` (`national_id`),
  UNIQUE KEY `email_address` (`email_address`),
  UNIQUE KEY `phone_number` (`phone_number`),
  UNIQUE KEY `contact_email` (`contact_email`),
  UNIQUE KEY `tbs_email` (`tbs_email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tbs_students`
--

LOCK TABLES `tbs_students` WRITE;
/*!40000 ALTER TABLE `tbs_students` DISABLE KEYS */;
INSERT INTO `tbs_students` VALUES (1,'Ali','Ben Salah',12345678,'ali@tbs.u-tunis.tn','hashed_pass_1','22115566','2000-05-12','Single','123 Rue Habib Bourguiba, Tunis','ali.contact@gmail.com','ali@tbs.tn','1001',NULL),(2,'Sara','Trabelsi',23456789,'majd.hamdi@tbs.u-tunis.tn','hashed_pass_2','99887766','1999-09-23','Married','45 Avenue de France, Sfax','sara.contact@gmail.com','sara@tbs.tn','3021','B32-97'),(3,'Youssef','Hammami',34567890,'youssef@gmail.com','hashed_pass_3','55667788','2001-01-15','Single','78 Rue de Marseille, Sousse','youssef.contact@gmail.com','youssef@tbs.tn','4000',NULL),(4,'Test','User',88888888,'spooqibear@gmail.com','hashed_password_here','12345678','2000-01-01','Single','123 Main Street','spooqibear@gmail.com','spooqibear@tbs.u-tunis.tn','1000',NULL);
/*!40000 ALTER TABLE `tbs_students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `time_slot_preferences`
--

DROP TABLE IF EXISTS `time_slot_preferences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `time_slot_preferences` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `time_slot_number` int DEFAULT NULL,
  `is_preferred` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_time_slot` (`student_id`,`time_slot_number`),
  KEY `student_id` (`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `time_slot_preferences`
--

LOCK TABLES `time_slot_preferences` WRITE;
/*!40000 ALTER TABLE `time_slot_preferences` DISABLE KEYS */;
INSERT INTO `time_slot_preferences` VALUES (91,3,1,0,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(92,3,2,0,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(93,3,3,0,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(94,3,4,0,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(95,3,5,0,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(96,3,6,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(97,3,7,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(98,3,8,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(99,3,9,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(100,3,10,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(101,3,11,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(102,3,12,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(103,3,13,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(104,3,14,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(105,3,15,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(106,3,16,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(107,3,17,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(108,3,18,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(109,3,19,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(110,3,20,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(111,3,21,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(112,3,22,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(113,3,23,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(114,3,24,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(115,3,25,1,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(116,3,26,0,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(117,3,27,0,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(118,3,28,0,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(119,3,29,0,'2025-07-03 10:26:00','2025-07-03 10:26:00'),(120,3,30,0,'2025-07-03 10:26:00','2025-07-03 10:26:00');
/*!40000 ALTER TABLE `time_slot_preferences` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'pfe'
--

--
-- Dumping routines for database 'pfe'
--
/*!50003 DROP PROCEDURE IF EXISTS `update_semester_summary` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `update_semester_summary`(
    IN p_student_id INT,
    IN p_year INT,
    IN p_semester INT
)
proc: BEGIN
    DECLARE v_registered DECIMAL(5,2);
    DECLARE v_earned DECIMAL(5,2);
    DECLARE v_gpa DECIMAL(4,2);
    DECLARE v_cumulative_registered DECIMAL(6,2);
    DECLARE v_cumulative_earned DECIMAL(6,2);
    DECLARE v_cumulative_gpa DECIMAL(4,2);
    DECLARE v_has_rows INT DEFAULT 0;

    SELECT COUNT(*) INTO v_has_rows
    FROM add_course ac
    JOIN courses c ON ac.course_code = c.course_code
    WHERE ac.student_id = p_student_id
      AND ac.year = p_year
      AND ac.semester = p_semester
      AND ac.grade_point IS NOT NULL;

    IF v_has_rows = 0 THEN
        LEAVE proc;
    END IF;

    SELECT 
        IFNULL(SUM(c.coefficient), 0), 
        IFNULL(SUM(IF(ac.status = 'passed', c.coefficient, 0)), 0),
        IFNULL(SUM(c.coefficient * ac.grade_point) / NULLIF(SUM(c.coefficient), 0), 0)
    INTO v_registered, v_earned, v_gpa
    FROM add_course ac
    JOIN courses c ON ac.course_code = c.course_code
    WHERE ac.student_id = p_student_id
      AND ac.year = p_year
      AND ac.semester = p_semester
      AND ac.grade_point IS NOT NULL;

    SELECT 
        IFNULL(SUM(c.coefficient), 0),
        IFNULL(SUM(IF(ac.status = 'passed', c.coefficient, 0)), 0),
        IFNULL(SUM(c.coefficient * ac.grade_point) / NULLIF(SUM(c.coefficient), 0), 0)
    INTO v_cumulative_registered, v_cumulative_earned, v_cumulative_gpa
    FROM add_course ac
    JOIN courses c ON ac.course_code = c.course_code
    WHERE ac.student_id = p_student_id
      AND (ac.year < p_year OR (ac.year = p_year AND ac.semester <= p_semester))
      AND ac.grade_point IS NOT NULL;

    INSERT INTO student_semester_summary (
        student_id, year, semester, 
        registered_credits, earned_credits, semester_gpa,
        cumulative_registered_credits, cumulative_earned_credits, cumulative_gpa
    )
    VALUES (
        p_student_id, p_year, p_semester,
        v_registered, v_earned, v_gpa,
        v_cumulative_registered, v_cumulative_earned, v_cumulative_gpa
    )
    ON DUPLICATE KEY UPDATE
        registered_credits = v_registered,
        earned_credits = v_earned,
        semester_gpa = v_gpa,
        cumulative_registered_credits = v_cumulative_registered,
        cumulative_earned_credits = v_cumulative_earned,
        cumulative_gpa = v_cumulative_gpa;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-13 22:11:08
