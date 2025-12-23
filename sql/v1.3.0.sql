#Upgrade

ALTER TABLE posts_permissions_group_members modify phone_number_prefix varchar(20) NOT NULL;
ALTER TABLE posts_permissions_group_members modify phone_number varchar(20) NOT NULL;

CREATE TABLE `family_office` (
  `id` int NOT NULL AUTO_INCREMENT,
  `did_family_office` tinyint(1) DEFAULT '0',
  `did_family_office_date` datetime NULL,
  `family_office_name` TEXT NULL,
  `registeration_address` TEXT NULL,
  `contact_person` TEXT NULL,
  `mobile` TEXT NULL,
  `comment` TEXT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `family_office_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

CREATE TABLE `trust` (
  `id` int NOT NULL AUTO_INCREMENT,
  `did_trust` tinyint(1) DEFAULT '0',
  `did_trust_date` datetime NULL,
  `trust_name` TEXT NULL,
  `contact_person` TEXT NULL,
  `mobile` TEXT NULL,
  `settlor` TEXT NULL,
  `beneficiary` TEXT NULL,
  `comment` TEXT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `trust_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

#Downgrade

ALTER TABLE posts_permissions_group_members modify phone_number_prefix int NOT NULL;
ALTER TABLE posts_permissions_group_members modify phone_number int NOT NULL;

drop table if exists `family_office`;
drop table if exists `trust`;