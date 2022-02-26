CREATE TABLE `alesha`.`evacuation_announcement` (
  `id` VARCHAR(64) NOT NULL,
  `user_id` INT NOT NULL,
  `a_type` VARCHAR(45) NOT NULL,
  `a_service` VARCHAR(45) NOT NULL,
  `city_a` VARCHAR(64) NOT NULL,
  `city_b` VARCHAR(64) NULL,
  `info` VARCHAR(500) NULL,
  `scheduled` TIMESTAMP NULL,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT,
  PRIMARY KEY (`id`));
