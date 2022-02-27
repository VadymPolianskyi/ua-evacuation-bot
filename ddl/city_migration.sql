ALTER TABLE `alesha`.`evacuation_announcement`
ADD COLUMN `city_from_id` INT NOT NULL AFTER `created`,
ADD COLUMN `city_to_id` INT NULL AFTER `city_from_id`,
CHANGE COLUMN `city_a` `city_a` VARCHAR(64) NULL ;
