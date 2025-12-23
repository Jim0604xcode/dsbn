1. Admin portal Phase 4 NEW API Gateway config
/admin/user_life_overview_chart_table post

2. Admin portal Phase 5 NEW API Gateway config
/admin/user_storage_usage_table post

# shared life experience (life moment and trajectory)
/posts/get/shared_with_me/life_experiences get

# get shared life trajectory by id
/get/shared_with_me/life_trajectories/{life_trajectory_post_id} get

# Remove not used API Gateway config
GET	/auth/get/prasejwtdata
GET	/auth/get/authgear_jwt 
POST	/auth/get/userByAuthGearID
POST	/auth/get/userByPhone
POST	/payment/apple/notifications
POST	/payment/google/notifications
POST	/payment/create_payment_for_apple/{id}
POST	/payment/create_payment_for_apple_subscription
POST	/payment/create_payment_for_google/{id}
POST	/payment/create_payment_for_google_subscription
POST	/payment/create_pre_transaction
GET	/payment/query_subscription_still_valid
POST	/crypto/encrypt-plan-text
POST	/crypto/decrypt-plan-text
POST    /auth/get/usersByAuthGearIDs
GET /get_single_favorite_headshot/{id}
GET /verified_inheritor_ulink_token/{token}
GET /get/organs_donor/{id}
GET /get/user_inheritor_by_jwt/{id}
GET /posts/get/permissions_group/{group_id}
DELETE  /posts/remove/permissions_group/{group_id}/members/{member_id}
POST    /oss/video/upload
POST    /oss/images/upload
POST    /oss/images/download
POST    /posts/file/upload

#Upgrade
ALTER TABLE `message_to_you` ADD COLUMN `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE `message_to_you` ADD COLUMN `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE `secret_base` ADD COLUMN `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP; 
ALTER TABLE `secret_base` ADD COLUMN `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP; 

#Downgrade
ALTER TABLE `message_to_you` DROP COLUMN `updated_at`;
ALTER TABLE `message_to_you` DROP COLUMN `created_at`;
ALTER TABLE `secret_base` DROP COLUMN `updated_at`;
ALTER TABLE `secret_base` DROP COLUMN `created_at`;

