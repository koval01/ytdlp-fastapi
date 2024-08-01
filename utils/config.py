"""
Configuration settings for the application.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ALLOWED_HOSTS: str = 'localhost:8000'
    CRYPT_KEY: str = 'fl5JcIwHh0SM87Vl18B_Sn65lVOwhYIQ3fnfGYqpVlE='
    SECRET_KEY: str = 'devsecretkey'
    DISABLE_DOCS: int = 0

    class Config:
        env_file = "./.env.local"


settings = Settings()
