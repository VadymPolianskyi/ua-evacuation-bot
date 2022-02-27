CREATE TABLE "evacuation_announcement" (
  "id" varchar(64) NOT NULL,
  "user_id" int NOT NULL,
  "a_type" varchar(45) NOT NULL,
  "a_service" varchar(45) NOT NULL,
  "city_a" varchar(64) NOT NULL,
  "city_b" varchar(64) DEFAULT NULL,
  "info" text,
  "scheduled" timestamp NULL DEFAULT NULL,
  "created" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id")
)