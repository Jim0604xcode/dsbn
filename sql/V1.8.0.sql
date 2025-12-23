-- below is edit phone number migration script
#Upgrade
CREATE TABLE `phone_master` (
  `id` int NOT NULL AUTO_INCREMENT,
  `phone_number` varchar(100) NOT NULL,
  `user_id` char(36) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `phone_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
)ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4
;

ALTER TABLE `user_inheritor` ADD COLUMN `inheritor_phone_master_id` int NULL;
ALTER TABLE `user_inheritor` ADD CONSTRAINT `user_inheritor_ibfk_3` FOREIGN KEY (`inheritor_phone_master_id`) REFERENCES `phone_master` (`id`);

SELECT phone_number,inheritor_user_id FROM user_inheritor;
INSERT INTO phone_master (phone_number,user_id) values ('',''); -- according to user_inheritor rows

UPDATE user_inheritor 
SET inheritor_phone_master_id = (SELECT id FROM phone_master WHERE phone_master.phone_number = user_inheritor.phone_number AND phone_master.user_id = user_inheritor.inheritor_user_id LIMIT 1)
WHERE phone_number IN (SELECT phone_number FROM phone_master);


ALTER TABLE `user_inheritor` Modify COLUMN `inheritor_phone_master_id` int NOT NULL;
ALTER TABLE `user_inheritor` DROP COLUMN `phone_number`;


#Downgrade
-- 1. Put the phone_number back into user_inheritor
ALTER TABLE `user_inheritor` 
ADD COLUMN `phone_number` VARCHAR(100) NULL;

-- 2. Populate phone_number from phone_master (using the FK)
UPDATE `user_inheritor` ui
INNER JOIN `phone_master` pm ON ui.inheritor_phone_master_id = pm.id
SET ui.phone_number = pm.phone_number;

-- 3. Make phone_number NOT NULL (only if all rows now have a value)
--    (Optional: add a WHERE clause if some may be NULL)
ALTER TABLE `user_inheritor` 
MODIFY COLUMN `phone_number` VARCHAR(100) NOT NULL;

-- 4. Drop the FK and column inheritor_phone_master_id
ALTER TABLE `user_inheritor` 
DROP FOREIGN KEY `user_inheritor_ibfk_3`;

ALTER TABLE `user_inheritor` 
DROP COLUMN `inheritor_phone_master_id`;

-- 5. Drop the phone_master table
drop table if exists `phone_master`;







#Upgrade
ALTER TABLE staff ADD COLUMN `phone_number` varchar(100) NULL DEFAULT '';
UPDATE staff SET phone_number = '+85251823007' WHERE authgear_id = 'f8d0040c-8841-4af5-b39c-14f6bcc9f321'; -- -- according to staff rows

INSERT INTO staff (id,role,authgear_id,phone_number) values ('3fa3a9c0-1bfc-4adf-8183-aaf7c8b669c7','admin','3fa3a9c0-1bfc-4adf-8183-aaf7c8b669c7','+85265781752');
INSERT INTO staff (id,role,authgear_id,phone_number) values ('9ed2be7e-bd76-4797-b411-7ae4c0cc7fcb','admin','9ed2be7e-bd76-4797-b411-7ae4c0cc7fcb','+85293753876');

#Downgrade
ALTER TABLE staff DROP COLUMN `phone_number`;





























-- below is edit sendPushByLastEnablePushTime script
#Upgrade
ALTER TABLE `push_notification` ADD COLUMN `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP;
#Downgrade
ALTER TABLE `push_notification` DROP COLUMN `updated_at`;




#Production production config
1. NEW API Gateway config
/admin/send_push_notification_specific_device post
/auth/updateMobile put