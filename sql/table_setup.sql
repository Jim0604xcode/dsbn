-- Set the database character set to utf8mb4
ALTER DATABASE `deepsoul_uat` CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = users   */
/******************************************/
-- TNC and Privacy table

CREATE TABLE `staff` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role` enum('admin','staff') NOT NULL,
  `username` varchar(50) NOT NULL, 
  `password` varchar(500) NOT NULL, 
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) 
)
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;


CREATE TABLE `users` (
  `id` char(36) NOT NULL,
  `authgear_id` char(36) NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `authgear_id` (`authgear_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = user_settings   */
/******************************************/
CREATE TABLE `user_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` char(36) NOT NULL,
  `notification_enabled` tinyint(1) DEFAULT '0',
  `language` enum('en','zh_hans','zh_hk') NOT NULL,
  `maximum_number_inheritor` int NOT NULL DEFAULT 5,  
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_settings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = products   */
/******************************************/
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` varchar(100) NOT NULL,
  `product_name` varchar(100) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `currency` varchar(3) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_id` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;


/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = default_life_moments_post_types   */
/******************************************/
CREATE TABLE `default_life_moments_post_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type_code` varchar(255) NOT NULL,
  `zh_hk_type_name` varchar(255) NOT NULL,
  `zh_hans_type_name` varchar(255) NOT NULL,
  `en_type_name` varchar(255) NOT NULL,
  `zh_hk_type_description` varchar(255) NOT NULL,
  `zh_hans_type_description` varchar(255) NOT NULL,
  `en_type_description` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `type_code` (`type_code`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4
;


/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = default_life_trajectory_post_types   */
/******************************************/
CREATE TABLE `default_life_trajectory_post_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type_code` varchar(255) NOT NULL,
  `zh_hk_type_name` varchar(255) NOT NULL,
  `zh_hans_type_name` varchar(255) NOT NULL,
  `zh_hk_type_description` varchar(255) NOT NULL,
  `zh_hans_type_description` varchar(255) NOT NULL,
  `en_type_name` varchar(255) NOT NULL,
  `en_type_description` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `type_code` (`type_code`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4
;



/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = default_message_to_you_post_types   */
/******************************************/
CREATE TABLE `default_message_to_you_post_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type_code` varchar(255) NOT NULL,
  `zh_hk_type_name` varchar(255) NOT NULL,
  `zh_hans_type_name` varchar(255) NOT NULL,
  `zh_hk_type_description` varchar(255) NOT NULL,
  `zh_hans_type_description` varchar(255) NOT NULL,
  `en_type_name` varchar(255) NOT NULL,
  `en_type_description` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `type_code` (`type_code`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4
;



/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = secret_base   */
/******************************************/
CREATE TABLE `secret_base` (
  `id` int NOT NULL AUTO_INCREMENT,
  `asset_type` enum('BANK_ACCOUNT','PROPERTY','SAFETY_DEPOSIT_BOX','CONFIDENTIAL_EVENT') NOT NULL,
  `user_id` char(36) NOT NULL,
  `product_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `secret_base_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `secret_base_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = posts_master   */
/******************************************/
CREATE TABLE `posts_master` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `content` mediumtext NOT NULL,
  `start_date` timestamp NULL DEFAULT NULL,
  `end_date` timestamp NULL DEFAULT NULL,
  `motion_rate` decimal(10,0) DEFAULT NULL,
  `images_name` json DEFAULT NULL,
  `videos_name` json DEFAULT NULL,
  `voices_name` json DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = replies_master   */
/******************************************/
CREATE TABLE replies_master (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `post_master_id` INT NOT NULL, -- The original post this reply belongs to
  `user_id` char(36) NOT NULL, -- The user who made the reply
  `parent_reply_master_id` INT, -- NULL for direct replies to the original post, otherwise points to the reply it's responding to
  `content` TEXT NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_deleted` BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (post_master_id) REFERENCES posts_master(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (parent_reply_master_id) REFERENCES replies_master(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = custom_life_moments_post_types   */
/******************************************/
CREATE TABLE `custom_life_moments_post_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` char(36) NOT NULL,
  `type_name` varchar(255) NOT NULL,
  `type_description` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `custom_life_moments_post_types_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = custom_life_trajectory_post_types   */
/******************************************/
CREATE TABLE `custom_life_trajectory_post_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` char(36) NOT NULL,
  `type_name` varchar(255) NOT NULL,
  `type_description` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `custom_life_trajectory_post_types_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = post_permissions_groups   */
/******************************************/
CREATE TABLE `post_permissions_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_name` varchar(255) NOT NULL,
  `create_by` char(36) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `create_by` (`create_by`),
  CONSTRAINT `post_permissions_groups_ibfk_1` FOREIGN KEY (`create_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = post_user_permissions   */
/******************************************/
CREATE TABLE `post_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `shared_post_id` int NOT NULL,
  `shared_by` char(36) NOT NULL,
  `post_source` enum('LIFE_MOMENT','MESSAGE_TO_YOU','LIFE_TRAJECTORY') NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `shared_by` (`shared_by`),
  CONSTRAINT `post_user_permissions_ibfk_1` FOREIGN KEY (`shared_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = posts_permissions_group_members   */
/******************************************/
CREATE TABLE `posts_permissions_group_members` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `user_id` char(36) DEFAULT NULL,
  `phone_number_prefix` int NOT NULL,
  `phone_number` int NOT NULL,
  `first_name` varchar(255) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `group_id` (`group_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `posts_permissions_group_members_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `post_permissions_groups` (`id`),
  CONSTRAINT `posts_permissions_group_members_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = post_shared_recipients   */
/******************************************/
CREATE TABLE `post_shared_recipients` (
  `id` int NOT NULL AUTO_INCREMENT,
  `permission_id` int NOT NULL,
  `shared_to` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `permission_id` (`permission_id`),
  KEY `shared_to` (`shared_to`),
  CONSTRAINT `post_shared_recipients_ibfk_1` FOREIGN KEY (`permission_id`) REFERENCES `post_user_permissions` (`id`),
  CONSTRAINT `post_shared_recipients_ibfk_2` FOREIGN KEY (`shared_to`) REFERENCES `posts_permissions_group_members` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = bank_account   */
/******************************************/
CREATE TABLE `bank_account` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bank_account_name` text NOT NULL,
  `bank_account_number` text NOT NULL,
  `currency` varchar(3) NOT NULL,
  `meta_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `meta_id` (`meta_id`),
  CONSTRAINT `bank_account_ibfk_1` FOREIGN KEY (`meta_id`) REFERENCES `secret_base` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = property   */
/******************************************/
CREATE TABLE `property` (
  `id` int NOT NULL AUTO_INCREMENT,
  `property_name` text NOT NULL,
  `property_address` text NOT NULL,
  `remarks` text,
  `meta_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `meta_id` (`meta_id`),
  CONSTRAINT `property_ibfk_1` FOREIGN KEY (`meta_id`) REFERENCES `secret_base` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = safety_deposit_box   */
/******************************************/
CREATE TABLE `safety_deposit_box` (
  `id` int NOT NULL AUTO_INCREMENT,
  `safety_deposit_box_name` text NOT NULL,
  `safety_deposit_box_open_method` text NOT NULL,
  `safety_deposit_box_address` text NOT NULL,
  `remarks` text,
  `meta_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `meta_id` (`meta_id`),
  CONSTRAINT `safety_deposit_box_ibfk_1` FOREIGN KEY (`meta_id`) REFERENCES `secret_base` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = confidential_event   */
/******************************************/
CREATE TABLE `confidential_event` (
  `id` int NOT NULL AUTO_INCREMENT,
  `event_name` text NOT NULL,
  `event_details` text NOT NULL,
  `meta_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `meta_id` (`meta_id`),
  CONSTRAINT `confidential_event_ibfk_1` FOREIGN KEY (`meta_id`) REFERENCES `secret_base` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = goods_donor   */
/******************************************/
CREATE TABLE `goods_donor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `image_url_1` text,
  `image_url_2` text,
  `image_url_3` text,
  `goods_info` text NOT NULL,
  `donor_organization` text NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `goods_donor_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = user_beneficiaries   */
/******************************************/
CREATE TABLE `user_beneficiaries` (
  `id` int NOT NULL AUTO_INCREMENT,
  `beneficiary_type` enum('PHONE','INSURANCE') NOT NULL,
  `platform_or_company` text NOT NULL,
  `first_name` text NOT NULL,
  `last_name` text NOT NULL,
  `relation` text NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_beneficiaries_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = user_beneficiaries_meta   */
/******************************************/
CREATE TABLE `user_beneficiaries_meta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `contact_country_code` varchar(100) NOT NULL,
  `contact_number` varchar(100) NOT NULL,
  `meta_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `meta_id` (`meta_id`),
  CONSTRAINT `user_beneficiaries_meta_ibfk_1` FOREIGN KEY (`meta_id`) REFERENCES `user_beneficiaries` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = user_inheritor   */
/******************************************/
CREATE TABLE `user_inheritor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inviate_status` enum('WIP','ACCEPT','REJECT','EXPIRE') NOT NULL,
  `invitation_expire_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `phone_number` varchar(100) NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  `inheritor_user_id` char(36) DEFAULT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `jwt` text,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `inheritor_user_id` (`inheritor_user_id`),
  CONSTRAINT `user_inheritor_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `user_inheritor_ibfk_2` FOREIGN KEY (`inheritor_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;


/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = user_inheritor_meta   */
/******************************************/
CREATE TABLE `user_inheritor_meta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `LB` tinyint(1) DEFAULT '0' COMMENT 'Love Bequeathed',
  `OP` tinyint(1) DEFAULT '0' COMMENT 'Obituaries',
  `LET` tinyint(1) DEFAULT '0' COMMENT 'Life Events Timeline',
  `SB` tinyint(1) DEFAULT '0' COMMENT 'Secret Base',
  `HM` tinyint(1) DEFAULT '0' COMMENT 'Health Management',
  `MTS` tinyint(1) DEFAULT '0' COMMENT 'Message To Someone',
  `LS` tinyint(1) DEFAULT '0' COMMENT 'Legal Summiries',
  `FC` tinyint(1) DEFAULT '0' COMMENT 'Financial Chapter',
  `PE` tinyint(1) DEFAULT '0' COMMENT 'Personal Effects',
  `meta_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `meta_id` (`meta_id`),
  CONSTRAINT `user_inheritor_meta_ibfk_1` FOREIGN KEY (`meta_id`) REFERENCES `user_inheritor` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = life_moments   */
/******************************************/
CREATE TABLE `life_moments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `post_master_id` int NOT NULL,
  `user_id` char(36) NOT NULL,
  `weather` varchar(255) DEFAULT NULL,
  `participants` varchar(255) DEFAULT NULL,
  `post_type_code` varchar(255) DEFAULT NULL,
  `custom_post_type_id` int DEFAULT NULL,
  `restaurant_name` varchar(255) DEFAULT NULL,
  `food_name` varchar(255) DEFAULT NULL,
  `academic_work_interest` varchar(255) DEFAULT NULL,
  `school_score` varchar(20) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `post_master_id` (`post_master_id`),
  KEY `user_id` (`user_id`),
  KEY `post_type_code` (`post_type_code`),
  KEY `custom_post_type_id` (`custom_post_type_id`),
  CONSTRAINT `life_moments_ibfk_1` FOREIGN KEY (`post_master_id`) REFERENCES `posts_master` (`id`),
  CONSTRAINT `life_moments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `life_moments_ibfk_3` FOREIGN KEY (`post_type_code`) REFERENCES `default_life_moments_post_types` (`type_code`),
  CONSTRAINT `life_moments_ibfk_4` FOREIGN KEY (`custom_post_type_id`) REFERENCES `custom_life_moments_post_types` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = life_trajectories   */
/******************************************/
CREATE TABLE `life_trajectories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` char(36) NOT NULL,
  `post_master_id` int NOT NULL,
  `post_type_code` varchar(255) DEFAULT NULL,
  `custom_post_type_id` int DEFAULT NULL,
  `age` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `post_master_id` (`post_master_id`),
  KEY `user_id` (`user_id`),
  KEY `post_type_code` (`post_type_code`),
  KEY `custom_post_type_id` (`custom_post_type_id`),
  CONSTRAINT `life_trajectories_ibfk_1` FOREIGN KEY (`post_master_id`) REFERENCES `posts_master` (`id`),
  CONSTRAINT `life_trajectories_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `life_trajectories_ibfk_3` FOREIGN KEY (`post_type_code`) REFERENCES `default_life_trajectory_post_types` (`type_code`),
  CONSTRAINT `life_trajectories_ibfk_4` FOREIGN KEY (`custom_post_type_id`) REFERENCES `custom_life_trajectory_post_types` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = love_left_in_the_world   */
/******************************************/
CREATE TABLE `love_left_in_the_world` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` text NOT NULL,
  `content` text NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `love_left_in_the_world_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = message_to_you   */
/******************************************/
CREATE TABLE `message_to_you` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` char(36) NOT NULL,
  `post_master_id` int NOT NULL,
  `post_type_code` varchar(255) NOT NULL,
  `when_can_read_the_post` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `post_type_code` (`post_type_code`),
  KEY `post_master_id` (`post_master_id`),
  CONSTRAINT `message_to_you_ibfk_1` FOREIGN KEY (`post_master_id`) REFERENCES `posts_master` (`id`),
  CONSTRAINT `message_to_you_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `message_to_you_ibfk_3` FOREIGN KEY (`post_type_code`) REFERENCES `default_message_to_you_post_types` (`type_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = organs_donor   */
/******************************************/
CREATE TABLE `organs_donor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `did_arrange_organ_donor` enum('YES','NO','NOT_YET') DEFAULT 'NOT_YET',
  `contact_organization` text NOT NULL,
  `comment` text NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `organs_donor_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;



/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = transaction   */
/******************************************/
CREATE TABLE `transaction` (
  `id` int NOT NULL AUTO_INCREMENT,
  `payment_service_provider` enum('APPLE','GOOGLE') NOT NULL,
  `payment_status` enum('PENDING','COMPLETED','FAILED') NOT NULL,
  `payment_type` enum('CONSUMPTION','SUBSCRIPTION') NOT NULL,
  `transaction_id` varchar(100) DEFAULT NULL,
  `purchase_date` datetime DEFAULT NULL,
  `purchase_token` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  `product_id` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `transaction_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `transaction_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;











/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = pass_away_info   */
/******************************************/
CREATE TABLE `pass_away_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `death_time` datetime NOT NULL,
  `death_certificate` text,
  `id_card_copy` text,
  `relationship_proof` text,
  `inheritor_id_proof` text,
  `submitted_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `meta_id` int NOT NULL,
  `transaction_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `meta_id` (`meta_id`),
  KEY `transaction_id` (`transaction_id`),
  CONSTRAINT `pass_away_info_ibfk_1` FOREIGN KEY (`meta_id`) REFERENCES `user_inheritor` (`id`),
  CONSTRAINT `pass_away_info_ibfk_2` FOREIGN KEY (`transaction_id`) REFERENCES `transaction` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;

/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = pass_away_info_meta   */
/******************************************/

CREATE TABLE `pass_away_info_meta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `approval_status` enum('VERIFY','APPROVAL','REJECT') NOT NULL,
  `approval_comments` varchar(500) DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  `admin_user_id` int DEFAULT NULL,
  `meta_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_user_id` (`admin_user_id`),
  KEY `meta_id` (`meta_id`),
  CONSTRAINT `pass_away_info_meta_ibfk_1` FOREIGN KEY (`admin_user_id`) REFERENCES `staff` (`id`),
  CONSTRAINT `pass_away_info_meta_ibfk_2` FOREIGN KEY (`meta_id`) REFERENCES `pass_away_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;



/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = subscription_meta   */
/******************************************/
CREATE TABLE `subscription_meta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `subscription_expire_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `meta_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `meta_id` (`meta_id`),
  CONSTRAINT `subscription_meta_ibfk_1` FOREIGN KEY (`meta_id`) REFERENCES `transaction` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;



/******************************************/
/*   DatabaseName = deepsoul_uat   */
/*   TableName = user_testament   */
/******************************************/
CREATE TABLE `user_testament` (
  `id` int NOT NULL AUTO_INCREMENT,
  `did_testament` tinyint(1) DEFAULT '0',
  `did_testament_date` datetime DEFAULT NULL,
  `testament_store_in` text,
  `comment` text,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_testament_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y'
;


CREATE TABLE push_notification (
  `id` int NOT NULL AUTO_INCREMENT,
  `token` varchar(100) DEFAULT NULL,
  `device_uuid` varchar(100) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `push_notification_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y';





CREATE TABLE palliative_care(
  `id` int NOT NULL AUTO_INCREMENT,
  `did_arrange` enum('AGREE','NOT_AGREE','NOT_YET') DEFAULT 'NOT_YET',
  `contact_organization` varchar(255) NOT NULL,
  `notes` varchar(1000) DEFAULT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `palliative_care_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y';



CREATE TABLE medical_preference(
  `id` int NOT NULL AUTO_INCREMENT,
  `did_arrange` enum('DID','NOT_DID','NOT_YET') DEFAULT 'NOT_YET',
  `notes` varchar(1000) DEFAULT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `medical_preference_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y';



CREATE TABLE enduring_power_of_attorney(
  `id` int NOT NULL AUTO_INCREMENT,
  `did_arrange` enum('DID','NOT_DID','NOT_YET') DEFAULT 'NOT_YET',
  `notes` varchar(1000) DEFAULT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `enduring_power_of_attorney_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y';




CREATE TABLE ceremony_preference(
  `id` int NOT NULL AUTO_INCREMENT,
  `did_arrange` enum('BUDDHISM','TAOISM','CHRISTIANITY','NOT_YET','CUSTOM') DEFAULT 'NOT_YET',
  `notes` varchar(1000) DEFAULT NULL,
  `custom` varchar(100) DEFAULT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `ceremony_preference_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y';




CREATE TABLE coffin(
  `id` int NOT NULL AUTO_INCREMENT,
  `did_arrange` enum('CHINESE','WEST','EF','NOT_YET','CUSTOM') DEFAULT 'NOT_YET',
  `notes` varchar(1000) DEFAULT NULL,
  `custom` varchar(100) DEFAULT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `coffin_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y';



CREATE TABLE funeral(
  `id` int NOT NULL AUTO_INCREMENT,
  `did_arrange` enum('CREMATION','BURIAL','NOT_YET','CUSTOM') DEFAULT 'NOT_YET',
  `notes` varchar(1000) DEFAULT NULL,
  `custom` varchar(100) DEFAULT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `funeral_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y';


CREATE TABLE ashes(
  `id` int NOT NULL AUTO_INCREMENT,
  `did_arrange` enum('CB','SAITGOR','SAOTS','CR','NOT_YET','CUSTOM') DEFAULT 'NOT_YET',
  `notes` varchar(1000) DEFAULT NULL,
  `custom` varchar(100) DEFAULT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `ashes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y';



-- 十句形容自己的話
CREATE TABLE describe_yourself_ten_sentences(
  `id` int NOT NULL AUTO_INCREMENT,
  `content` varchar(1000) NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `describe_yourself_ten_sentences_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y';



-- 我的生命價值
CREATE TABLE value_of_life(
  `id` int NOT NULL AUTO_INCREMENT,
  `content` varchar(1000) NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `value_of_life_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y';



-- 人生感悟
CREATE TABLE life_insights(
  `id` int NOT NULL AUTO_INCREMENT,
  `content` varchar(1000) NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `life_insights_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y';


-- 我的墓誌銘
CREATE TABLE epitaph(
  `id` int NOT NULL AUTO_INCREMENT,
  `content` varchar(1000) NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `epitaph_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y';



-- 我最愛的大頭照
CREATE TABLE favorite_headshot(
  `id` int NOT NULL AUTO_INCREMENT,
  `picture` varchar(200) DEFAULT NULL,
  `ago` int NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` char(36) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `favorite_headshot_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ENCRYPTION='Y';


INSERT INTO `default_life_moments_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `en_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_description`, `created_at`) VALUES ('1','SMALL_HAPPINESS','小確幸','小确幸','Small Happiness','「今天飲咗杯超香咖啡，正！」只要你用心發現，雖然好微小嘅事，都能讓人幸福感滿滿。','「今天喝了杯超香咖啡，真棒！」只要你用心发现，虽然是很微小的事，都能让人幸福感满满。','“I had a super fragrant coffee today, great!” As long as you discover with your heart, even small things can make you feel full of happiness.','2025-04-25 17:00:01');
INSERT INTO `default_life_moments_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `en_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_description`, `created_at`) VALUES ('2','GRATITUDE','好感恩','好感恩','Gratitude','記下值得感恩的人事，你會發覺你的生命滿是喜樂！','记下值得感恩的人事，你会发觉你的生命满是喜乐！','Write down the people and things you are grateful for, and you will find that your life is full of joy!','2025-04-25 17:00:01');
INSERT INTO `default_life_moments_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `en_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_description`, `created_at`) VALUES ('3','SAVING_HAPPINESS','儲蓄快樂','储蓄快乐','Saving Happiness','把快樂的事像儲蓄一樣存起來，心靈自然富足又健康！','把快乐的事像储蓄一样存起来，心灵自然富足又健康！','Save happy things like savings, and your mind will naturally be rich and healthy!','2025-04-25 17:00:01');
INSERT INTO `default_life_moments_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `en_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_description`, `created_at`) VALUES ('4','PROUD_MOMENTS','驕傲事：學業/工作/興趣','骄傲事：学业/工作/兴趣','Proud Moments: Studies/Work/Interests','用自己的標準記下驕傲事，時刻給自己鼓勵和加油！','用自己的标准记下骄傲事，时刻给自己鼓励和加油！','Record proud moments by your own standards, and always encourage and cheer yourself up!','2025-04-25 17:00:01');
INSERT INTO `default_life_moments_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `en_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_description`, `created_at`) VALUES ('5','HEALING_SADNESS','憂傷療癒間','忧伤疗愈间','Healing Sadness','唔開心？嚟呢度同AI傾，心情自然靚返晒！','不开心？来这里和AI聊聊，心情自然好起来！','Feeling down? Come here and talk to AI, and your mood will naturally improve!','2025-04-25 17:00:01');
INSERT INTO `default_life_moments_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `en_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_description`, `created_at`) VALUES ('6','REGRETS','遺憾事','遗憾事','Regrets','記低錯過事，心釋懷，人健康。','记下错过的事，心释怀，人健康。','Record missed things, let go, and stay healthy.','2025-04-25 17:00:01');
INSERT INTO `default_life_moments_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `en_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_description`, `created_at`) VALUES ('7','I_WANT_TO_RANT','我要鬧人','我要骂人','I Want to Rant','「嬲到爆」？唔使忍，呢度盡情發洩！','「气到爆」？不用忍，这里尽情发泄！','“Furious”? No need to hold back, vent here to your heart’s content!','2025-04-25 17:00:01');
INSERT INTO `default_life_moments_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `en_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_description`, `created_at`) VALUES ('8','RANDOM_NOTES','隨心留','随心留','Random Notes','每日事多難分類，見乜記乜就好！','每日事多难分类，看到什么记什么就好！','Too many things to categorize every day, just record whatever you see!','2025-04-25 17:00:01');
INSERT INTO `default_life_moments_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `en_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_description`, `created_at`) VALUES ('9','SPECIAL_JOURNAL','特別日誌','特别日志','Special Journal','係咪有啲日子對你有特別意義呢？記低特別日子！','是否有些日子对你有特别意义呢？记下特别意义！','Are there any days that are particularly meaningful to you? Record those special date!','2025-04-25 17:00:01');
INSERT INTO `default_life_moments_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `en_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_description`, `created_at`) VALUES ('10','CHERISHED_ANNIVERSARIES','珍重紀念日','珍重纪念日','Cherished Anniversaries','有啲日子真係年年都要慶祝同紀念㗎！','有些日子真是年年都要庆祝和纪念的！','Some days really need to be celebrated and commemorated every year!','2025-04-25 17:00:01');
INSERT INTO `default_life_moments_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `en_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_description`, `created_at`) VALUES ('11','TRAVEL_SNAPSHOTS','旅遊剪影','旅游剪影','Travel Snapshots','記下旅遊經歷，看足跡遍佈何方。','记下旅游经历，看足迹遍布何方。','Record travel experiences and see where your footprints have been.','2025-04-25 17:00:01');
INSERT INTO `default_life_moments_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `en_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_description`, `created_at`) VALUES ('12','GOURMET_LIFE','美食人生','美食人生','Gourmet Life','係咪次次食飯都要打卡先呢？咁呢度就啱晒你啦！','是不是每次吃饭都要打卡呢？那这里就很适合你啦！','Do you always need to check in before eating? Then this is perfect for you!','2025-04-25 17:00:01');
INSERT INTO `default_life_moments_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `en_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_description`, `created_at`) VALUES ('13','PETS_AND_ME','竉物與我','宠物与我','Pets and Me','記錄與竉物相處的點滴，分享你和牠的溫馨時刻。','记录与宠物相处的点滴，分享你和它的温馨时刻。','Record moments with your pets and share your warm memories together.','2025-05-23 14:45:56');

INSERT INTO `default_life_trajectory_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('1','INFANCY','初生','初生','0-3歲','0-3岁','Infancy','0-3 years old','2025-04-25 16:59:31');
INSERT INTO `default_life_trajectory_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('2','PRIMARY_SCHOOL','小學','小学','小學1-6','小学1-6','Primary School','Primary School 1-6','2025-04-25 16:59:31');
INSERT INTO `default_life_trajectory_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('3','SECONDARY_SCHOOL','中學','中学','中學1-7','中学1-7','Secondary School','Secondary School 1-7','2025-04-25 16:59:31');
INSERT INTO `default_life_trajectory_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('4','UNIVERSITY','大學','大学','大學1-4','1-4','University','University 1-4','2025-04-25 16:59:31');
INSERT INTO `default_life_trajectory_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('5','WORK','工作','工作','','','Work','Work','2025-04-25 16:59:31');
INSERT INTO `default_life_trajectory_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('6','MARRIAGE','婚姻','婚姻','','','Marriage','Marriage','2025-04-25 16:59:31');
INSERT INTO `default_life_trajectory_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('7','CHILDREN','子女','子女','','','Children','Children','2025-04-25 16:59:31');
INSERT INTO `default_life_trajectory_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('8','RETIREMENT','退休','退休','','','Retirement','Retirement','2025-04-25 16:59:31');

INSERT INTO `default_message_to_you_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('1','THANKS_TO_YOU','好在有你','好在有你','感謝你一直以來的支持和陪伴。','感谢你一直以来的支持和陪伴。','Thanks to You','Thank you for your continuous support and companionship.','2025-04-25 16:59:47');
INSERT INTO `default_message_to_you_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('2','SORRY','對不起','对不起','對不起，請原諒我過去的錯誤。','对不起，请原谅我过去的错误。','Sorry','I am sorry, please forgive my past mistakes.','2025-04-25 16:59:47');
INSERT INTO `default_message_to_you_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('3','HAVE_SOMETHING_TO_TELL_YOU','有話跟你說','有话跟你说','我有一些話想跟你說。','我有一些话想跟你说。','Have Something to Tell You','I have something to tell you.','2025-04-25 16:59:47');
INSERT INTO `default_message_to_you_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('4','GRATEFUL_FOR_YOU','感恩有你','感恩有你','感恩有你在我生命中。','感恩有你在我生命中。','Grateful for You','Grateful to have you in my life.','2025-04-25 16:59:47');

