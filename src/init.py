class Config:
    PERSIST_DIR = "db"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 500
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    NUM_CHUNKS = 3
    BEDROCK_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"
    AWS_REGION = "us-east-1"
    TEMPERATURE = 0.7
    MAX_HISTORY = 5
    MAX_FILE_SIZE_MB = 10  # Limit for uploaded files