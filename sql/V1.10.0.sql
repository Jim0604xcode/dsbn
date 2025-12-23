#Production production config
1. Admin portal Phase 1 NEW API Gateway config
/admin/life_moment_table post
/admin/life_traj_table post
/admin/message_to_you_table post

2. WAF add below:
HTTP 80:
HTTPS 443: 
TLS协议版本1.3 
/home/letsencrypt/live/adminportal.deepsoulai.com/fullchain.pem 
/home/letsencrypt/live/adminportal.deepsoulai.com/privkey.pem

3. Admin portal Phase 2 NEW API Gateway config
/admin/user_life_moment_table post
/admin/user_life_traj_table post
/admin/user_message_to_you_table post
/admin/post_and_ai_total_summary_table get

4. Admin portal Phase 3 NEW API Gateway config
/admin/user_pre_death_plan_table post

6. API gateway:
auth/validation post change request body form => JSON

7. Serveless config
 - create a new serveless function
 - Setup Env value
 - Setup Timer Trigger
 - Create a new user for Serverless mysql connection
 - KMS key for Serverless mysql connection