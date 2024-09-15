
CREATE DATABASE IF NOT EXISTS `Employee` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `Employee`;

-- ---------------------------------------------------------------- --
--                     Employee TABLE                        --
-- ---------------------------------------------------------------- --
DROP TABLE IF EXISTS `Employee`;
CREATE TABLE IF NOT EXISTS `Employee` (
  `Staff_ID` INT PRIMARY KEY,
  `Staff_FName` VARCHAR(50) NOT NULL,
  `Staff_LName` VARCHAR(50) NOT NULL,
  `Dept` VARCHAR(50),
  `Position` VARCHAR(50) NOT NULL,
  `Country` varchar(50) NOT NULL,
  `Email` VARCHAR(50) NOT NULL,
  `Reporting_Manager` INT,
  `Role` INT NOT NULL,
  FOREIGN KEY (`Reporting_Manager`) REFERENCES `Employee`(`Staff_ID`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
