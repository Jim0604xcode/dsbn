# Getting Started

<!-- test build commit msg -->

### Prerequisites

- Python 3.8+
- Virtual environment tool (e.g., `venv`)

### Turobot shot

- **Check connection with database**
  ```sh
  python tests/test_db_connection.py
  ```

### Installation

1. **Clone the repository:**

   ```sh
   git clone <repository-url>
   cd deepsoul-backend
   ```

2. **Activate the virtual environment:**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install the dependencies:**
   ```sh
   pip3 install -r requirements/dev.txt
   ```

### API doc

- Access the API documentation: Open your browser and avigate to http://127.0.0.1:8000/docs

### commit code process

1. clone project
2. create branch from main
3. update your code in branch
4. push your branch into github
5. create merger request in your github

### Running the Application with Different Environment Files

You can run the application with different environment files for different environments (e.g., UAT, local development) by setting the `ENV` environment variable.

#### Prerequisites

1. Ensure you have `python-dotenv` installed:
   ```sh
   pip install python-dotenv
   ```

### Environment Configuration

The application can be run with different environment files for various environments. Below is a table that outlines the environment files used for each environment:

| Environment | Description                    | Environment File    |
| ----------- | ------------------------------ | ------------------- |
| local       | Local testing                  | `.env`              |
| localDocker | Local development using Docker | `.env.local.docker` |
| staging     | Staging environment            | `.env.prod`         |
| prod        | Production environment         | `.env.staging`      |

### Example with Running the Application with local

- **Running the Application with local**

  ```sh
  export ENV=local
  uvicorn src.main:app
  ```

- **Running the Application with Docker**

### Docker build

2. docker build -t DOCKER_NAME .
3. docker run --rm -it -p 8000:8000 DOCKER_NAME bash
   a. check repo file: ls - a
   b. remove iamge by: docker rmi DOCKER_NAME
4. ENV=local.Docker uvicorn src.main:app --host=0.0.0.0
   OR
   ENV=local.Docker docker-compose up --build

   ```sh
   export ENV=localDocker
   docker run --env ENV=localDocker --env-file .env.local.docker -p 8000:8000 your-image-name
   ```

### Docker ECS Deployment

## Deployment

### Setup up API Gateway to allow new api

1. copy openapi json via `http://127.0.0.1:8000/openapi.json`
2. login alicloud
3. api gateway -> API 管理 -> API 列表 -> Import Swagger -> paste openapi json -> release
4. API 列表 -> select updated api -> 更多操作 -> 授權
5. WIP

### Deploy to ECS

## UAT

1. When you code merge to `uat` branch, which will trigger depolt to alicloud ACR.
2. login into ecs: `ssh -i YOUR_PATH/ECS-UAT-SSH.pem root@47.84.32.137`
3. In you local termainl: `scp env/.env.staging root@47.84.32.137:/path/to/remote/env`
   3.1 In you local termainl: `scp /Users/xxxx/Downloads/ervice-account.json.json root@47.84.32.137:/path/to/remote/google`
4. pull image from acr: `docker pull crpi-53omb0ulwhsu310m-vpc.ap-southeast-1.personal.cr.aliyuncs.com/uat_deepsoul/uat:1739201301`
5. After login ecs: `cd /path/to/remote/env`
   ```sh
   /path/to/remote/
   └── env/
      └── .env.staging
   ```
6. Run new application:
   - If port 8000 is already in use, stop the existing container:
     ```sh
     docker ps  # List all running containers
     docker stop <container_id>  # Replace <container_id> with the ID of the container using port 8000
     ```
     -Run new applciation:
     `docker run --env-file .env.staging -d -p 8000:8000 47642e0babf5`
     - Run with google file:
       `docker run --env-file .env.staging -v /path/to/remote/google:/app/path/to/remote/google -d -p 8000:8000 f25d0522161c`

## Production

1. When you code merge to `prod` branch, which will trigger depolt to alicloud ACR.
2. login into ecs via workbench
3. use workbench upload .env.prod file into target path
4. sudo docker login --username=itsupport@deepsoulai.com crpi-8dq4fm7ms8sqtmq2-vpc.cn-hongkong.personal.cr.aliyuncs.com
5. sudo docker pull crpi-8dq4fm7ms8sqtmq2-vpc.cn-hongkong.personal.cr.aliyuncs.com/deepsoul-app/deepsoul-backend:1753423072
6. docker run --env-file .env.prod -d -p 8000:8000 --memory=7g --memory-reservation=6.5g

### Mauel deploy to ACR

      - name: Build the Docker image
        run: docker build --platform linux/amd64 -t ${{ secrets.ACR_REPOSITORY_URL }}:${{ env.TIMESTAMP }} .

      - name: Push the Docker image to ACR
        run: docker push ${{ secrets.ACR_REPOSITORY_URL }}:${{ env.TIMESTAMP }}
