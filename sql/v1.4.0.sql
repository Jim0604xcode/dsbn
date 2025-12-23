#Upgrade

ALTER TABLE user_inheritor ADD in_app_noti_send tinyint(1) DEFAULT '0';
ALTER TABLE user_inheritor ADD sender_name varchar(255) NOT NULL;


#Downgrade

ALTER TABLE user_inheritor DROP COLUMN in_app_noti_send;
ALTER TABLE user_inheritor DROP COLUMN sender_name;
