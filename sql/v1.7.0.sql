#Production production config
1. AI DASHSCOPE key prepare
2. AI AliGreen key prepare
3. NEW API Gateway config
4. KMS DashScope API key Secret prepare

#Upgrade

ALTER TABLE staff ADD COLUMN authgear_id char(36) DEFAULT '' ;
UPDATE staff SET authgear_id = 'f8d0040c-8841-4af5-b39c-14f6bcc9f321';  -- 这里需要你根据业务填充值，例如生成UUID或从其他表迁移
ALTER TABLE staff MODIFY authgear_id char(36) NOT NULL;
ALTER TABLE staff ADD UNIQUE KEY `authgear_id` (`authgear_id`);

ALTER TABLE staff DROP COLUMN username;
ALTER TABLE staff DROP COLUMN password;

ALTER TABLE staff MODIFY id char(36) NOT NULL;


ALTER TABLE pass_away_info_meta DROP FOREIGN KEY pass_away_info_meta_ibfk_1;
ALTER TABLE pass_away_info_meta MODIFY admin_user_id CHAR(36) DEFAULT NULL;
ALTER TABLE staff MODIFY id CHAR(36) NOT NULL;
ALTER TABLE pass_away_info_meta ADD CONSTRAINT pass_away_info_meta_ibfk_1 FOREIGN KEY (admin_user_id) REFERENCES staff(id);

INSERT INTO staff (id,role,authgear_id) values ('d6d69138-52b7-4e3f-889e-8655563454ec','admin','f8d0040c-8841-4af5-b39c-14f6bcc9f321');


UPDATE staff SET id = 'your-migration-logic-here' where authgear_id = '';  -- 这里需要你根据业务填充值，例如生成UUID或从其他表迁移
UPDATE pass_away_info_meta SET admin_user_id = 'your-migration-logic-here';  -- 这里需要你根据业务填充值，例如生成UUID或从其他表迁移


ALTER TABLE posts_master ADD COLUMN ai_feedback_content TEXT NULL;
ALTER TABLE posts_master ADD COLUMN ai_feedback_status ENUM('NA', 'ALLOWED', 'COMPLETED', 'ERROR_SAFEGUARD', 'ERROR_MASKING', 'ERROR_AI_FEEDBACK', 'ERROR_OTHER') DEFAULT 'NA';
ALTER TABLE posts_master ADD COLUMN ai_feedback_count INT NOT NULL DEFAULT 0;
-- add a new column ai_feedback_hotline boolean value, with default value false
ALTER TABLE posts_master ADD COLUMN ai_feedback_hotline BOOLEAN NULL DEFAULT FALSE;
ALTER TABLE posts_master ADD COLUMN ai_feedback_lang ENUM('en', 'sc', 'tc', 'other') NULL;


#Downgrade

ALTER TABLE staff ADD COLUMN username varchar(50) NOT NULL DEFAULT '';
ALTER TABLE staff ADD COLUMN password varchar(500) NOT NULL DEFAULT '';

ALTER TABLE staff DROP INDEX authgear_id;  -- 移除唯一键
ALTER TABLE staff DROP COLUMN authgear_id;

ALTER TABLE staff MODIFY id int NOT NULL AUTO_INCREMENT;

ALTER TABLE pass_away_info_meta MODIFY admin_user_id int DEFAULT NULL;

ALTER TABLE posts_master DROP COLUMN ai_feedback_content;
ALTER TABLE posts_master DROP COLUMN ai_feedback_status;
ALTER TABLE posts_master DROP COLUMN ai_feedback_count;

ALTER TABLE posts_master DROP COLUMN ai_feedback_hotline;
ALTER TABLE posts_master DROP COLUMN ai_feedback_lang;













