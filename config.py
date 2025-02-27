from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent

class Settings(BaseSettings):
    base_dir:Path = BASE_DIR

settings = Settings()
