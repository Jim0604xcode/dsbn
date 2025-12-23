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

#Downgrade

drop table if exists `replies_master`;
