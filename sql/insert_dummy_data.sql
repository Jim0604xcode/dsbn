INSERT INTO products (product_id,product_name,price,currency) values ('uat_consumer001','30日內繼承帳戶方案',1200,'HKD');
INSERT INTO products (product_id,product_name,price,currency) values ('uat_consumer002','7個工作日繼承帳戶方案',2800,'HKD');
INSERT INTO products (product_id,product_name,price,currency) values ('uat_consumer003','加快繼承帳戶方案',5000,'HKD');
INSERT INTO products (product_id,product_name,price,currency) values ('uat_subscription001','30日內繼承帳戶方案',1200,'HKD');
INSERT INTO products (product_id,product_name,price,currency) values ('uat_subscription002','30日內繼承帳戶方案',1200,'HKD');

INSERT INTO products (product_id,product_name,price,currency) values ('dev_consumer001','30日內繼承帳戶方案',1200,'HKD');
INSERT INTO products (product_id,product_name,price,currency) values ('dev_consumer002','7個工作日繼承帳戶方案',2800,'HKD');
INSERT INTO products (product_id,product_name,price,currency) values ('dev_consumer003','加快繼承帳戶方案',5000,'HKD');
INSERT INTO products (product_id,product_name,price,currency) values ('dev_subscription001','30日內繼承帳戶方案',1200,'HKD');
INSERT INTO products (product_id,product_name,price,currency) values ('dev_subscription002','30日內繼承帳戶方案',1200,'HKD');

INSERT INTO products (product_id,product_name,price,currency) values ('no_need_to_pay_consumer','Testing consumer',0,'HKD');
INSERT INTO products (product_id,product_name,price,currency) values ('no_need_to_pay_subscription','Testing subscription',0,'HKD');



-- mobile 59991234
INSERT INTO users (id,authgear_id) values ('9fcbe4e4-a9b2-409f-8766-46e2094246ff','9fcbe4e4-a9b2-409f-8766-46e2094246ff'); 
-- mobile 51823007
INSERT INTO users (id,authgear_id) values ('517ef59b-5d88-4b38-b700-4b72e5dde04f','780c6181-05bb-4326-9c82-9ad060100c4d'); 
-- mobile 65781752
INSERT INTO users (id,authgear_id) values ('19895842-6638-4bf2-b318-b9435e1220f8','19895842-6638-4bf2-b318-b9435e1220f8'); 


INSERT INTO user_inheritor (inviate_status,invitation_expire_date,phone_number,user_id,inheritor_user_id) values ('ACCEPT',NOW() + INTERVAL 7 DAY,'+85251823007','9fcbe4e4-a9b2-409f-8766-46e2094246ff','517ef59b-5d88-4b38-b700-4b72e5dde04f')
INSERT INTO user_inheritor (inviate_status,invitation_expire_date,phone_number,user_id,inheritor_user_id) values ('ACCEPT',NOW() + INTERVAL 7 DAY,'+85251823007','19895842-6638-4bf2-b318-b9435e1220f8','517ef59b-5d88-4b38-b700-4b72e5dde04f')
INSERT INTO user_inheritor_meta (LB,OP,LET,SB,HM,MTS,LS,FC,PE,meta_id) values (1,1,1,1,1,1,1,1,1,2);
INSERT INTO user_inheritor_meta (LB,OP,LET,SB,HM,MTS,LS,FC,PE,meta_id) values (1,1,1,1,1,1,1,1,1,3);


INSERT INTO transaction (payment_service_provider,payment_status,payment_type,user_id,product_id) values ('APPLE','PENDING','CONSUMPTION','517ef59b-5d88-4b38-b700-4b72e5dde04f','dev_consumer001');
INSERT INTO transaction (payment_service_provider,payment_status,payment_type,user_id,product_id) values ('APPLE','PENDING','CONSUMPTION','517ef59b-5d88-4b38-b700-4b72e5dde04f','dev_consumer003');

INSERT INTO pass_away_info (death_time,death_certificate,id_card_copy,relationship_proof,inheritor_id_proof,submitted_at,meta_id,transaction_id) values (NOW() - INTERVAL 7 DAY,'1c0b6935-598f-426b-a785-4279f50b37c5/personal_life_overview_chart/images/1747028101picture.jpg','1c0b6935-598f-426b-a785-4279f50b37c5/personal_life_overview_chart/images/1747028101picture.jpg','1c0b6935-598f-426b-a785-4279f50b37c5/personal_life_overview_chart/images/1747028101picture.jpg','1c0b6935-598f-426b-a785-4279f50b37c5/personal_life_overview_chart/images/1747028101picture.jpg',NOW(),2,104);
INSERT INTO pass_away_info (death_time,death_certificate,id_card_copy,relationship_proof,inheritor_id_proof,submitted_at,meta_id,transaction_id) values (NOW() - INTERVAL 7 DAY,'1c0b6935-598f-426b-a785-4279f50b37c5/personal_life_overview_chart/images/1747028101picture.jpg','1c0b6935-598f-426b-a785-4279f50b37c5/personal_life_overview_chart/images/1747028101picture.jpg','1c0b6935-598f-426b-a785-4279f50b37c5/personal_life_overview_chart/images/1747028101picture.jpg','1c0b6935-598f-426b-a785-4279f50b37c5/personal_life_overview_chart/images/1747028101picture.jpg',NOW(),3,105);

INSERT INTO pass_away_info_meta (approval_status,meta_id) values ('APPROVAL',68);

INSERT INTO acknowledge_reading(app_name,terms_and_conditions_path,privacy_path,tnc_version,privacy_version) values ('deepsoul','admin/acknowledge_reading/images/1750750544Screenshot 2025-06-16 at 2.24.31 PM.png','admin/acknowledge_reading/images/1750750544privacy_path.png',1750750545,1750750545);
insert into user_settings (user_id,notification_enabled,language) values ('62077306-faf4-432f-bc90-9d8cb65352cf',1,'en');



insert into user_settings (user_id,notification_enabled,language) values ('c7d07dcd-eff6-47e8-8cdf-319a36269542',0,'en');
insert into user_settings (user_id,notification_enabled,language) values ('e6041ea9-b5fa-4218-9308-0908892e57a2',0,'en');








-- UAT
| id                                   | authgear_id                          | created_at          | username / mobile
| 0c498016-0af9-42f3-b5af-f361825c263b | 423edd74-4f77-4896-a790-aaf13f52116e | 2025-05-20 02:21:00 | testing
| 10266f03-b409-42c6-9970-eb30914c1260 | f65a5e38-fb4d-42e4-826c-fb5ed6dd1e12 | 2025-06-02 18:31:18 | 陳小明4 51346123
| 56ee4bd2-c794-44d8-9b9f-52e05586288c | 1c0b6935-598f-426b-a785-4279f50b37c5 | 2025-05-22 08:54:19 | 
| 65d11e6b-9f1c-40e4-ab12-fe87c1a6dd37 | 9e1b90cb-4092-4c54-bd50-d3249a12e321 | 2025-04-28 05:18:03 |
| 7fe7ca04-abf8-4659-9fda-fa7c32c792b4 | be650aef-dcb0-436b-b982-64653d1a7ccb | 2025-06-20 01:35:58 |
| 9f2e8022-6dd6-4842-8003-0c5b20be72de | 46d080ff-8efe-4b70-b497-63de7173baf6 | 2025-06-16 08:29:04 | Jim Chan 51823007
| a542847b-fb0c-480c-b523-6962234e023d | 9fcbe4e4-a9b2-409f-8766-46e2094246ff | 2025-06-17 09:03:20 | WUWU Diem 59991234
| adc46c55-334b-4db8-bc5e-10fb904c6406 | 3ab1efdb-0c2a-4a8e-bc24-342f2677d0d6 | 2025-06-20 01:35:58 |
| b09c9e70-a887-4e18-9bef-d063920a5220 | 780c6181-05bb-4326-9c82-9ad060100c4d | 2025-05-29 16:24:38 |
| cba7c96c-832c-4708-916a-2ad7e519b97f | a9c2b7ca-46ca-4f2c-9de5-eb09ae721757 | 2025-05-27 01:36:16 |
| cc736ad7-b53b-4621-aaa2-45107dbe9ad5 | 7a2e7a95-0ec1-40ce-bd0c-6d20afddf94a | 2025-06-09 15:18:37 |
| e83d2b5e-9f5b-45a9-8b80-f2d2d37acd80 | 19895842-6638-4bf2-b318-b9435e1220f8 | 2025-06-06 09:00:22 | Diem 65781752
| ed91ce56-01f5-4925-8de5-24f57151d4d1 | 375b9605-a5f2-4ce9-97ff-725e0ecf55d1 | 2025-06-09 15:18:37 |
| 9750a119-5415-4e2c-8fab-d61638e33cd2 | 0b575562-7920-4d65-9a3a-6b73f5596f3d | 2025-07-01 07:44:08 | Don 94660121 delete at agthgear 
| 41ac4572-ad73-44da-9224-c62be4074507 | 963e3a81-1cf6-4491-a307-041e744f71ea | 2025-07-10 09:00:45 | Don 94660121  







INSERT INTO `default_message_to_you_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('1','THANKS_TO_YOU','好在有你','好在有你','感謝你一直以來的支持和陪伴。','感谢你一直以来的支持和陪伴。','Thanks to You','Thank you for your continuous support and companionship.','2025-04-25 16:59:47');
INSERT INTO `default_message_to_you_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('2','SORRY','對不起','对不起','對不起，請原諒我過去的錯誤。','对不起，请原谅我过去的错误。','Sorry','I am sorry, please forgive my past mistakes.','2025-04-25 16:59:47');
INSERT INTO `default_message_to_you_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('3','HAVE_SOMETHING_TO_TELL_YOU','有話跟你說','有话跟你说','我有一些話想跟你說。','我有一些话想跟你说。','Have Something to Tell You','I have something to tell you.','2025-04-25 16:59:47');
INSERT INTO `default_message_to_you_post_types` (`id`, `type_code`, `zh_hk_type_name`, `zh_hans_type_name`, `zh_hk_type_description`, `zh_hans_type_description`, `en_type_name`, `en_type_description`, `created_at`) VALUES ('4','GRATEFUL_FOR_YOU','感恩有你','感恩有你','感恩有你在我生命中。','感恩有你在我生命中。','Grateful for You','Grateful to have you in my life.','2025-04-25 16:59:47');



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

