-- ALTER TABLE `posts_permissions_group_members` ADD `phone_master_id` int NULL;
-- ALTER TABLE `posts_permissions_group_members` ADD CONSTRAINT `posts_permissions_group_members_ibfk_3` FOREIGN KEY (`phone_master_id`) REFERENCES `phone_master` (`id`);

-- INSERT INTO phone_master (phone_number, user_id)
-- SELECT
--     CONCAT('+', phone_number_prefix, phone_number) AS phone_number,
--     user_id
-- FROM posts_permissions_group_members;

-- UPDATE posts_permissions_group_members pgm
-- SET phone_master_id = (
--     SELECT pm.id
--     FROM phone_master pm
--     WHERE pm.phone_number = CONCAT('+', pgm.phone_number_prefix, pgm.phone_number)
--     LIMIT 1
-- )
-- WHERE EXISTS (
--     SELECT 1
--     FROM phone_master pm2
--     WHERE pm2.phone_number = CONCAT('+', pgm.phone_number_prefix, pgm.phone_number)
-- );


-- ALTER TABLE `posts_permissions_group_members` DROP COLUMN `phone_number`;
-- ALTER TABLE `posts_permissions_group_members` DROP COLUMN `phone_number_prefix`;
