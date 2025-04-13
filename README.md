# 📱 Phone Agent

Phone Agent is a system for crawling phone-related data, generating vector embeddings, and enabling question-answering via an API.

---

## 🚀 Getting Started

Follow the steps below to set up and run the project locally using Docker.

### 1. Clone the Repository

```
git clone https://github.com/suongnq/phone_agent.git
cd phone_agent 
```

### 2. Configure Environment Variables
Create the .env file from the sample provided:
```
cp .env_sample .env
```
You need to add your API keys and other configuration values in the .env file.

### 3.  Build & Run with Docker
Build and start the project with Docker by running the following command:
```
docker-compose up --build
```

### 4. Access the API
Once the service is running, open your browser and navigate to:
```
http://0.0.0.0:8000/docs#
 ```
This will open the Swagger UI for you to interact with and test the API.

## 🧪 API Endpoints
### 1. POST```/api/crawl-data```
Run above API to crawl phone-related data in the following sequences:
- ```type = "phone_series_url"```
- ```type = "item_url"```
- ```type = "item_detail"```

### 2. GET ```/api/generate-embedding```
 Generate vector embeddings from the crawled data to build a semantic vector database.

### 3. POST ```/api/ask-phone-agent```
Ask questions about phone specifications, and the model will return answers.

```question = "your question"```

## 🔁 Workflow Diagram
The diagram below illustrates the entire flow of the Phone Agent system:

<img src="https://raw.githubusercontent.com/suongnq/phone_agent/main/app/workflows/phone_agent_flow.png" width="800"/>

