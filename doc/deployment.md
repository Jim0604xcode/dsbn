# Deployment Guide

### 1. production prepare (should be ready in uat)

1. Database migration scripts (if schema changes):
2. Place in `deployment/version` directory.
3. every step need to markup in version.txt

### 2. Manuel enable maintance mode

1. Go to OSS
2. Go appconfig-deepsoul/object
3. Edit appConfig json is_under_maintenance -> true
4. Upload the updated appConfig.json
5. Permission select: 文件 ACL -> 公共讀

### 3. Production Deployment

1. Merge code into the `prod` branch to trigger deployment to Aliyun ACR automatically.
2. Login to ECS via workbench.
3. Upload the .env file to the target path using workbench.
4. Login to ACR:
   ```sh
   sudo docker login --username=itsupport@deepsoulai.com crpi-8dq4fm7ms8sqtmq2-vpc.cn-hongkong.personal.cr.aliyuncs.com
   ```
5. Pull the Docker image:
   ```sh
   sudo docker pull crpi-8dq4fm7ms8sqtmq2-vpc.cn-hongkong.personal.cr.aliyuncs.com/deepsoul-app/deepsoul-backend:1753423072  # Update image tag as needed
   ```
6. Stop pre old container
   ```sh
   docker stop {CONTAINER_ID}
   ```
7. Start the application:
   ```sh
   docker run --env-file .env.prod -d -p 8000:8000 --memory=7g --memory-reservation=6.5g --restart unless-stopped {IMAGE_ID} # Update image ID as needed
   ```

### 4. RDS deployment

1. Login database
2. Create sql

### 7.5. If new API -> Manuel Gateway Configuration (Aliyun)

1. Login alicloud https://signin.alibabacloud.com/ 
2. Search for "api gateway" in the search bar
3. In the left hand menu, "Manage APIs" > "APIs"
4. Chagne the location to "Singapore"
5. Go to API Gateway -> API Management -> API List -> Add your new api into api list.
6. 將API上線
7. 更多操作 -> 授權

### 8. Rollback Steps

If you need to rollback to a previous version:

1. Identify the previous stable Docker image tag or container ID.
2. Stop the current running container:
   ```sh
   docker ps
   docker stop <current_container_id>
   ```
3. Start the previous version:
   ```sh
    docker run --env-file .env.prod -d -p 8000:8000 --memory=7g --memory-reservation=6.5g --restart unless-stopped {PRE_IMAGE_ID}
   ```
4. Verify the application is running as expected.

5. If sql updated. do downgrade action.

6. If API gateway deployed. Remove your deployed api.
