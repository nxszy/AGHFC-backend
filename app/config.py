from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class FirebaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="firebase_")
    project_id: str
    public_keys_url: str

class Config(BaseModel):
    firebase_config: FirebaseConfig = FirebaseConfig()

settings = Config()