DROP DATABASE IF EXISTS HRMS;
CREATE DATABASE IF NOT EXISTS HRMS DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE HRMS;

-- ---------------------------------------------------------------- --
--                     Employee TABLE                        --
-- ---------------------------------------------------------------- --
DROP TABLE IF EXISTS employee;
CREATE TABLE IF NOT EXISTS employee (
  Staff_ID INT PRIMARY KEY,
  Staff_FName VARCHAR(50) NOT NULL,
  Staff_LName VARCHAR(50) NOT NULL,
  Dept VARCHAR(50),
  Position VARCHAR(50) NOT NULL,
  Country varchar(50) NOT NULL,
  Email VARCHAR(50) NOT NULL,
  Reporting_Manager INT,
  Role INT NOT NULL,
  Password_Hash VARCHAR(256) NOT NULL,
  FOREIGN KEY (`Reporting_Manager`) REFERENCES `employee`(`Staff_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
  
DROP TABLE IF EXISTS `schedule`;
CREATE TABLE IF NOT EXISTS `schedule` (
  `Schedule_ID` INT PRIMARY KEY,
  `Staff_ID` INT NOT NULL,
  `Date` DATE NOT NULL,
  `Time_Slot` TINYINT NOT NULL,
  FOREIGN KEY (`Staff_ID`) REFERENCES `employee`(`Staff_ID`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `request`;
CREATE TABLE IF NOT EXISTS `request` (
  `Request_ID` INT PRIMARY KEY AUTO_INCREMENT,
  `Staff_ID` INT NOT NULL,
  `Reason` VARCHAR(200) NOT NULL,
  `Status` TINYINT NOT NULL,
  -- `File_Type` MEDIUMBLOB, SQL cant handle file data types so omitting for now
  `StartDate` DATE NOT NULL,
  `EndDate` DATE NOT NULL,
  `Time_Slot` TINYINT NOT NULL,
  `Request_Type` TINYINT NOT NULL,
  FOREIGN KEY (`Staff_ID`) REFERENCES `employee`(`Staff_ID`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `team`;
CREATE TABLE IF NOT EXISTS `team` (
  `Staff_ID` INT NOT NULL,
  `Team_ID` INT NOT NULL,
  FOREIGN KEY (`Staff_ID`) REFERENCES `employee`(`Staff_ID`),
  PRIMARY KEY (`Staff_ID`, `Team_ID`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;



-- ---------------------------------------------------------------- --
--                    FAKE DATA                       --
-- ---------------------------------------------------------------- --

INSERT INTO employee (Staff_ID, Staff_FName, Staff_LName, Dept, Position, Country, Email, Reporting_Manager, Role, Password_Hash) VALUES
(130002, 'Jack', 'Sim', 'CEO', 'MD', 'Singapore', 'jack.sim@allinone.com.sg', 130002, 1, "459ff9761f33bf7ef77104e7aa47edb8eb88a65afc300609165848f8ca2e3c17"), -- Hashed password using 123
(140001, 'Derek', 'Tan', 'Sales', 'Director', 'Singapore', 'Derek.Tan@allinone.com.sg', 130002, 1, "15bd67868b50b2f9c10f2553794def2bb2f24348b2070a827c0a71cd3420d246"), -- Hashed password using 123
(140894, 'Rahim', 'Khalid', 'Sales', 'Sales Manager', 'Singapore', 'Rahim.Khalid@allinone.com.sg', 140001, 3, 'bebd257f5cfc64347ed352c3730e55481dbc50b75c8eb249bbc2808b691fd837'), -- Hashed password using 123
(140002, 'Susan', 'Goh', 'Sales', 'Account Manager', 'Singapore', 'Susan.Goh@allinone.com.sg', 140894, 2, '24a02a8c983680f4fd57fec048fed7d13470796c68d584195419aec46be8cb0c'),  -- Hashed password using 123
(160008, 'Sally', 'Loh', 'HR', 'Director', 'Singapore', 'Sally.Loh@allinone.com.sg', 130002, 1, '173a0d2b90dca473b3309cb01b4ebcce427913929e6ee6cea48a34b1a640d772');  -- Hashed password using 123

-- Insert data into Schedule table
INSERT INTO schedule (Schedule_ID, Staff_ID, Date, Time_Slot) VALUES
(1, 130002, '2024-11-11', 1),
(2, 140001, '2024-11-12', 2),
(3, 140894, '2024-11-13', 3),
(4, 140002, '2024-11-14', 2),
(5, 160008, '2024-11-15', 1);
-- 1 = AM, 2 = PM, 3 = AMPM

-- Insert data into Request table
INSERT INTO request (Request_ID, Staff_ID, Reason, Status, StartDate, EndDate, Time_Slot, Request_Type) VALUES
(1, 140001, 'Medical leave', 0, '2024-11-08', '2024-11-08',1, 1),
(2, 140894, 'Training session', 0, '2024-11-04', '2024-11-08', 2, 2),
(3, 140002, 'Personal time off', 0, '2024-11-06', '2024-11-07', 3, 1);
-- For Status: 0 = Pending, 1 = Approved (should be reflected in schedule DB), -1 = Rejected
-- For Time_Slot: 1 = AM, 2 = PM, 3 = AMPM
-- For Request_Type: 1 = Adhoc, 2 = Recurring

-- Insert data into Team table
INSERT INTO team (Staff_ID, Team_ID) VALUES
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