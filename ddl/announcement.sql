CREATE TABLE "evacuation_announcement" (
  "id" varchar(64) NOT NULL,
  "user_id" int NOT NULL,
  "a_type" varchar(45) NOT NULL,
  "a_service" varchar(45) NOT NULL,
  "info" text,
  "scheduled" timestamp NULL DEFAULT NULL,
  "created" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "city_from_id" int NOT NULL,
  "city_to_id" int DEFAULT NULL,
  PRIMARY KEY ("id")
)