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
    url: str = f'sqlite+aiosqlite:///{DB_PATH}'
    echo: bool = False
    naming_convention: dict[str, str]= {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }

class ProxySettings(BaseModel):
    use_proxy: bool = False
    proto: str = ''
    host: str = ''
    port: str = ''
    login: str = ''
    password: str = ''

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file= (BASE_DIR / '.env.template', BASE_DIR / '.env'),
        case_sensitive=False,
        env_nested_delimiter='__',
        env_prefix='BOT_CONFIG__'
    )
    base_dir:Path = BASE_DIR
    token: str = ''
    default_img_template: str = 'simple_standard'
    group: BloodGroups = BloodGroups()
    db: DbSettings = DbSettings()
    proxy: ProxySettings = ProxySettings()
    super_admins: list = []

settings = Settings()
