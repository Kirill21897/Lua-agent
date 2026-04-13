from dataclasses import dataclass

@dataclass
class Config:
    MODEL_NAME: str = "qwen2.5-coder:7b"
    OLLAMA_URL: str = "http://localhost:11434/api/generate"
    MAX_ITERATIONS: int = 3
    CONTEXT_WINDOW: int = 4096
    EXECUTION_TIMEOUT: int = 5  # секунд
    WORKSPACE_DIR: str = "workspace"