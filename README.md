# HackNU 2024 - EPAM Track

## Prerequisites
docker\
docker-compose

## Getting Started

### Clone the Repository
To get started, first clone the repository to your local machine:

```bash
git clone https://github.com/elamirKad/hacknu2024.git
cd hacknu2024
```

### Set Up the .env in root folder
```
DEBUG=1
SECRET_KEY=secret
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=some-pass
DB_HOST=db
DB_PORT=5432
OPENAI_API_KEY=openai-key
PINECONE_API_KEY=pinecone-key
HF_API_KEY=huggingface-key
```

### Build and Run the Project
To build and run the project, run the following command:

```bash
docker-compose up --build
```
