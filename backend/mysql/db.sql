DROP DATABASE IF EXISTS HRMS;
CREATE DATABASE IF NOT EXISTS HRMS DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE HRMS;

-- ---------------------------------------------------------------- --
--                     Employee TABLE                        --
-- ---------------------------------------------------------------- --
DROP TABLE IF EXISTS Employee;
CREATE TABLE IF NOT EXISTS Employee (
  Staff_ID INT PRIMARY KEY,
  Staff_FName VARCHAR(50) NOT NULL,
  Staff_LName VARCHAR(50) NOT NULL,
  Dept VARCHAR(50),
  Team INT,
  Position VARCHAR(50) NOT NULL,
  Country varchar(50) NOT NULL,
  Email VARCHAR(50) NOT NULL,
  Reporting_Manager INT,
  Role INT NOT NULL,
  FOREIGN KEY (`Reporting_Manager`) REFERENCES `Employee`(`Staff_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
  
DROP TABLE IF EXISTS Schedule;
CREATE TABLE IF NOT EXISTS Schedule (
  Schedule_ID INT PRIMARY KEY,
  Staff_ID INT NOT NULL,
  StartTime DateTime,
  EndTime DateTime,
  Reason VARCHAR(200),
  Status TINYINT NOT NULL,
  FOREIGN KEY (`Staff_ID`) REFERENCES `Employee`(`Staff_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS Team;
CREATE TABLE IF NOT EXISTS Team (
    Team_ID INT PRIMARY KEY,
    Staff_ID INT NOT NULL,
    FOREIGN KEY (`Staff_ID`) REFERENCES `Employee`(`Staff_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;