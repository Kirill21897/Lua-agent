from dataclasses import dataclass

@dataclass
class Config:
    MODEL_NAME: str = "qwen-reasoning:latest"
    OLLAMA_URL: str = "http://localhost:11434/api/chat"
    MAX_ITERATIONS: int = 5
    CONTEXT_WINDOW: int = 4096
    NUM_PREDICT: int = 256
    NUM_BATCH: int = 1
    PARALLEL: int = 1
    EXECUTION_TIMEOUT: int = 5  # секунд
    WORKSPACE_DIR: str = "workspace"