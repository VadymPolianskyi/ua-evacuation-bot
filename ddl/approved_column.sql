ALTER TABLE `alesha`.`evacuation_announcement`
ADD COLUMN `approved` TINYINT(1) NOT NULL DEFAULT 0 AFTER `city_to_id`;
