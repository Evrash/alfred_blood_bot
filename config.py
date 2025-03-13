from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file= (BASE_DIR / '.env.template', BASE_DIR / '.env'),
        case_sensitive=False,
        env_nested_delimiter='__',
        env_prefix='BOT_CONFIG__'
    )
    base_dir:Path = BASE_DIR
    token: str = ''

settings = Settings()
