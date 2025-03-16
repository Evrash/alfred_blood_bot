from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / 'db.sqlite3'

class BloodGroups(BaseModel):
    o_plus: str = '🅾️➕'
    o_minus: str = '🅾️➖'
    a_plus: str = '🅰️➕'
    a_minus: str = '🅰️️➖'
    b_plus: str = '🅱️➕'
    b_minus: str = '🅱️➖'
    ab_plus: str = '🆎➕'
    ab_minus: str = '🆎➖'

class DbSettings(BaseModel):
    url: str = f"sqlite+aiosqlite:///{DB_PATH}"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file= (BASE_DIR / '.env.template', BASE_DIR / '.env'),
        case_sensitive=False,
        env_nested_delimiter='__',
        env_prefix='BOT_CONFIG__'
    )
    base_dir:Path = BASE_DIR
    token: str = ''
    group: BloodGroups = BloodGroups()

settings = Settings()
