DROP DATABASE IF EXISTS HRMS;
CREATE DATABASE IF NOT EXISTS HRMS DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE HRMS;

-- ---------------------------------------------------------------- --
--                     Employee TABLE                        --
-- ---------------------------------------------------------------- --
DROP TABLE IF EXISTS Employee;
CREATE TABLE IF NOT EXISTS Employee (
  `Staff_ID` INT PRIMARY KEY,
  `Staff_FName` VARCHAR(50) NOT NULL,
  `Staff_LName` VARCHAR(50) NOT NULL,
  `Dept` VARCHAR(50),
  `Position` VARCHAR(50) NOT NULL,
  `Country` VARCHAR(50) NOT NULL,
  `Email` VARCHAR(50) NOT NULL,
  `Reporting_Manager` INT,
  `Role` INT NOT NULL,
  `Hashed_Password` VARCHAR(50) NOT NULL,
  FOREIGN KEY (`Reporting_Manager`) REFERENCES `Employee`(`Staff_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
  
DROP TABLE IF EXISTS `Schedule`;
CREATE TABLE IF NOT EXISTS `Schedule` (
  `Schedule_ID` INT PRIMARY KEY,
  `Staff_ID` INT NOT NULL,
  `Date` DATE NOT NULL,
  `Time_Slot` TINYINT NOT NULL,
  FOREIGN KEY (`Staff_ID`) REFERENCES `Employee`(`Staff_ID`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `Request`;
CREATE TABLE IF NOT EXISTS `Request` (
  `Request_ID` INT PRIMARY KEY,
  `Staff_ID` INT NOT NULL,
  `Schedule_ID` INT NOT NULL,
  `Reason` VARCHAR(200) NOT NULL,
  `Status` TINYINT NOT NULL,
  -- `File_Type` MEDIUMBLOB,
  `Date` DATE NOT NULL,
  `Time_Slot` TINYINT NOT NULL,
  `Request_Type` TINYINT NOT NULL,
  FOREIGN KEY (`Staff_ID`) REFERENCES `Employee`(`Staff_ID`),
  FOREIGN KEY (`Schedule_ID`) REFERENCES `Schedule`(`Schedule_ID`),
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `Team`;
CREATE TABLE IF NOT EXISTS `Team` (
  `Staff_ID` INT NOT NULL,
  `Team_ID` INT NOT NULL,
  FOREIGN KEY (`Staff_ID`) REFERENCES `Employee`(`Staff_ID`),
  PRIMARY KEY (`Staff_ID`, `Team_ID`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
