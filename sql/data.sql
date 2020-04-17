CREATE DATABASE IF NOT EXISTS rasp_db;
CREATE  TABLE IF NOT EXISTS `sensors_data` (
  `id` INT  AUTO_INCREMENT ,
  `temperature` FLOAT(4,2) ,
  `pressure` FLOAT(6,2) ,
  `humidity` FLOAT(5,3) ,
  `airquality` INTEGER,
  `record_datetime` TIMESTAMP ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;