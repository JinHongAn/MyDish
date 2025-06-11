-- 초기 설정
SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- 데이터베이스 생성 및 사용
CREATE SCHEMA IF NOT EXISTS `mydish_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `mydish_db`;

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS `user` (
  `user_id` VARCHAR(225) NOT NULL,
  `username` VARCHAR(225) NOT NULL,
  `password` VARCHAR(225) NOT NULL,
  `allergy` VARCHAR(225) NOT NULL COMMENT '알러지 정보',
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- CSV 기반 Recipe 테이블
CREATE TABLE IF NOT EXISTS `Recipe` (
  `recipe_id` INT NOT NULL,
  `CKG_NM` VARCHAR(255) NOT NULL,
  `CKG_MTH_ACTO_NM` VARCHAR(255),
  `CKG_MTRL_ACTO_NM` TEXT,
  `CKG_KND_ACTO_NM` VARCHAR(255),
  `CKG_TIME_NM` VARCHAR(100),
  `RCP_PARTS_DTLS` TEXT,
  `INFO_NA` FLOAT,
  `INFO_PRO` FLOAT,
  `INFO_FAT` FLOAT,
  `INFO_CAR` FLOAT,
  `INFO_ENG` FLOAT,
  `RCP_NA_TIP` TEXT,
  `MANUAL01` TEXT,
  `MANUAL02` TEXT,
  `MANUAL03` TEXT,
  `MANUAL04` TEXT,
  `MANUAL05` TEXT,
  `MANUAL06` TEXT,
  PRIMARY KEY (`recipe_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 검색 기록 테이블
CREATE TABLE IF NOT EXISTS `Search_history` (
  `search_id` INT NOT NULL,
  `search_user_id` VARCHAR(225),
  `search_query` TEXT,
  PRIMARY KEY (`search_id`),
  INDEX `user_id_idx` (`search_user_id` ASC),
  CONSTRAINT `fk_search_user_id`
    FOREIGN KEY (`search_user_id`)
    REFERENCES `user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 즐겨찾기 테이블
CREATE TABLE IF NOT EXISTS `Favorite` (
  `favorite_id` INT NOT NULL,
  `favorite_user_id` VARCHAR(225) NOT NULL,
  `favorite_recipe_id` INT NOT NULL,
  PRIMARY KEY (`favorite_id`),
  INDEX `user_id_idx` (`favorite_user_id` ASC),
  INDEX `recipe_id_idx` (`favorite_recipe_id` ASC),
  CONSTRAINT `fk_favorite_user_id`
    FOREIGN KEY (`favorite_user_id`)
    REFERENCES `user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_favorite_recipe_id`
    FOREIGN KEY (`favorite_recipe_id`)
    REFERENCES `Recipe` (`recipe_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 추천 기록 및 피드백 테이블
CREATE TABLE IF NOT EXISTS `Recommendation` (
  `recommendation_id` INT NOT NULL,
  `history_id` INT NOT NULL,
  `rcm_user_id` VARCHAR(225) NOT NULL,
  `rcm_recipe_id` INT NOT NULL,
  `user_feedback` VARCHAR(225) NOT NULL,
  PRIMARY KEY (`recommendation_id`),
  INDEX `user_id_idx` (`rcm_user_id` ASC),
  INDEX `recipe_id_idx` (`rcm_recipe_id` ASC),
  CONSTRAINT `fk_rcm_user_id`
    FOREIGN KEY (`rcm_user_id`)
    REFERENCES `user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_rcm_recipe_id`
    FOREIGN KEY (`rcm_recipe_id`)
    REFERENCES `Recipe` (`recipe_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 설정 복구
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
