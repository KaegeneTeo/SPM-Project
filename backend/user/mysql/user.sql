
CREATE DATABASE IF NOT EXISTS `user` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `user`;

-- ---------------------------------------------------------------- --
--                     USER TABLE                        --
-- ---------------------------------------------------------------- --
DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `user_id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(64) UNIQUE NOT NULL,
  `email` VARCHAR(120) UNIQUE NOT NULL,
  `password_hash` VARCHAR(128),
  `telegram_id` VARCHAR(64) UNIQUE,
  `telegram_tag` varchar(64) NOT NULL,
  `image` VARCHAR(256)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `user` (`user_id`, `username`, `email`, `password_hash`, `telegram_tag`, `image`, `telegram_id`) VALUES
(1, 'bokyan', 'bok@bok.com', 'pbkdf2:sha256:600000$Ant22xex5VCnUclw$b65776c52241f4a3394e58a264f8d01e8cbf960c9a72399c3d4c36047327432d', '@bokyannn', NULL, NULL),
(2, 'kae', 'kae@kae.com', 'pbkdf2:sha256:600000$Ant22xex5VCnUclw$b65776c52241f4a3394e58a264f8d01e8cbf960c9a72399c3d4c36047327432d', '@hotatementai', NULL, NULL)
