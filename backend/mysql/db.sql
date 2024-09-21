DROP DATABASE IF EXISTS HRMS;
CREATE DATABASE IF NOT EXISTS HRMS DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE HRMS;

-- ---------------------------------------------------------------- --
--                     Employee TABLE                        --
-- ---------------------------------------------------------------- --
DROP TABLE IF EXISTS `Employee`;
CREATE TABLE IF NOT EXISTS `Employee` (
  `Staff_ID` INT PRIMARY KEY,
  `Staff_FName` VARCHAR(50) NOT NULL,
  `Staff_LName` VARCHAR(50) NOT NULL,
  `Dept` VARCHAR(50) NOT NULL,
  `Position` VARCHAR(50) NOT NULL,
  `Country` VARCHAR(50) NOT NULL,
  `Email` VARCHAR(50) NOT NULL,
  `Reporting_Manager` INT NOT NULL,
  `Role` INT NOT NULL,
  `Hashed_Password` VARCHAR(100) NOT NULL,
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
  `Request_ID` INT PRIMARY KEY AUTO_INCREMENT,
  `Staff_ID` INT NOT NULL,
  `Schedule_ID` INT NOT NULL,
  `Reason` VARCHAR(200) NOT NULL,
  `Status` TINYINT NOT NULL,
  -- `File_Type` MEDIUMBLOB, SQL cant handle file data types so omitting for now
  `Date` DATE NOT NULL,
  `Time_Slot` TINYINT NOT NULL,
  `Request_Type` TINYINT NOT NULL,
  FOREIGN KEY (`Staff_ID`) REFERENCES `Employee`(`Staff_ID`),
  FOREIGN KEY (`Schedule_ID`) REFERENCES `Schedule`(`Schedule_ID`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `Team`;
CREATE TABLE IF NOT EXISTS `Team` (
  `Staff_ID` INT NOT NULL,
  `Team_ID` INT NOT NULL,
  FOREIGN KEY (`Staff_ID`) REFERENCES `Employee`(`Staff_ID`),
  PRIMARY KEY (`Staff_ID`, `Team_ID`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;



-- ---------------------------------------------------------------- --
--                    FAKE DATA                       --
-- ---------------------------------------------------------------- --

INSERT INTO Employee (Staff_ID, Staff_FName, Staff_LName, Dept, Position, Country, Email, Reporting_Manager, Role, Hashed_Password) VALUES
(130002, 'Jack', 'Sim', 'CEO', 'MD', 'Singapore', 'jack.sim@allinone.com.sg', 130002, 1, '5e884898da28047151d0e56f8dc6292773603d0d'), -- Hashed password using SHA-256 for "password"
(140001, 'Derek', 'Tan', 'Sales', 'Director', 'Singapore', 'Derek.Tan@allinone.com.sg', 130002, 1, '6f8db599de986fab7a21625b7916589c82d6b01d'), -- Hashed password using SHA-1 for "admin"
(140894, 'Rahim', 'Khalid', 'Sales', 'Sales Manager', 'Singapore', 'Rahim.Khalid@allinone.com.sg', 140001, 3, '7c222fb2927d828af22f592134e8932480637c0d'), -- Hashed password using MD5 for "123456"
(140002, 'Susan', 'Goh', 'Sales', 'Account Manager', 'Singapore', 'Susan.Goh@allinone.com.sg', 140894, 2, '3c59dc048e8850243be8079a5c74d079988e6f19'),  -- Hashed password using MD5 for "qwerty"
(160008, 'Sally', 'Loh', 'HR', 'Director', 'Singapore', 'Sally.Loh@allinone.com.sg', 130002, 1, '36bbe50ed96841d10443bcb670d6554f0a34b761be67ec9c4a8ad2c0c44ca42c');  -- Hashed password using sha-256 for "abcde"

-- Insert data into Schedule table
INSERT INTO Schedule (Schedule_ID, Staff_ID, Date, Time_Slot) VALUES
(1, 130002, '2024-11-11', 1),
(2, 140001, '2024-11-12', 2),
(3, 140894, '2024-11-13', 3),
(4, 140002, '2024-11-14', 2),
(5, 160008, '2024-11-15', 1);
-- 1 = AM, 2 = PM, 3 = AMPM

-- Insert data into Request table
INSERT INTO Request (Request_ID, Staff_ID, Schedule_ID, Reason, Status, Date, Time_Slot, Request_Type) VALUES
(1, 140001, 2, 'Medical leave', 0, '2024-11-08', 1, 1),
(2, 140894, 3, 'Training session', 0, '2024-11-07', 2, 2),
(3, 140002, 4, 'Personal time off', 0, '2024-11-06', 3, 1);
-- For Status: 0 = Pending, 1 = Approved (should be reflected in schedule DB), -1 = Rejected
-- For Time_Slot: 1 = AM, 2 = PM, 3 = AMPM
-- For Request_Type: 1 = Adhoc, 2 = Recurring

-- Insert data into Team table
INSERT INTO Team (Staff_ID, Team_ID) VALUES
(130002, 1),
(140001, 2),
(140001, 1),
(140894, 3),
(140894, 2),
(140002, 3),
(160008, 1),
(160008, 15),
(160008, 16),
(160008, 17);
/*
There are 24 teams in total
1 - CEO Team
2 - Sales Director Team
3 - Sales Team 1
4 - Sales Team 2
5 - Sales Team 3
6 - Sales Team 4
7 - Sales Team 5
8 - Consultancy Division Director Team
9 - System Solutioning Division Director Team (Developers)
10 - System Solutioning Division Director Team (Support Team)
11 - Engineering Operation Division Director Team (Senior Engineers)
12 - Engineering Operation Division Director Team (Junior Engineers)
13 - Engineering Operation Division Director Team (Call Centre)
14 - Engineering Operation Division Director Team (Operations Planning Team)
15 - HR and Admin Director Team (HR Team)
16 - HR and Admin Director Team (L&D Team)
17 - HR and Admin Director Team (Admin Team)
18 - Finance Director Team 
19 - Finance Team 1
20 - Finance Team 2
21 - Finance Team 3
22 - Finance Team 4
23 - Finance Team 5
24 - IT Director Team
*/