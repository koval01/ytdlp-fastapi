import requests

from pydantic import field_validator
from pydantic_settings import BaseSettings


def fetch_cookies_data(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.text


class Settings(BaseSettings):
    ALLOWED_HOSTS: str = 'localhost,127.0.0.1,*.trycloudflare.com'
    CRYPT_KEY: str = 'fl5JcIwHh0SM87Vl18B_Sn65lVOwhYIQ3fnfGYqpVlE='
    CRYPT_TTL: int = 1200
    SECRET_KEY: str = 'devsecretkey'
    DISABLE_DOCS: int = 0
    DISABLE_DEMO: int = 0
    DISABLE_HOST_VALIDATION: int = 0
    COOKIES_URL: str = 'https://gist.githubusercontent.com/username/hex/raw/hex/file.txt'
    COOKIES: str = ''
    REST_MODE: int = 0

    class Config:
        env_file = "./.env.local"

    @field_validator('COOKIES')
    def load_cookies(cls, _, values):
        url = values.data["COOKIES_URL"]
        if url:
            return fetch_cookies_data(url)
        raise ValueError("COOKIES_URL must be provided")


settings = Settings()
