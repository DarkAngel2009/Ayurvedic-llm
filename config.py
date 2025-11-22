import os

class Config:
    MODEL_NAME = os.getenv("MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    CHROMA_DB_PATH = os.getenv("DB_PATH", "./data/embeddings/chroma_db")
    PROCESSED_DATA_PATH = os.getenv("PROCESSED_DATA_PATH", "./data/processed/")
    BOOKS_PATH = os.getenv("BOOKS_PATH", "./data/books/")
    MAX_RECOMMENDATIONS = int(os.getenv("MAX_RECOMMENDATIONS", "5"))
    REQUIRE_SAFETY_CHECK = os.getenv("REQUIRE_SAFETY_CHECK", "True") == "True"
    API_PORT = int(os.getenv("API_PORT", "5000"))
    DEBUG = os.getenv("DEBUG", "True") == "True"
