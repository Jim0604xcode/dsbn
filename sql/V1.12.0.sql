----- KMS + RAM config Remove
1. Remove ram - acs:ram::5270752738704153:role/oss-frontend-sts
2. New api /get/post-files-post-policy
3. Update api request body /get/post-files-presigned-urls files:[{file_name: str, file_size: int}]
4. KMS Remove staging:acs/ram/user/oss-sts-client | prod:acs/ram/user/oss-sts-client