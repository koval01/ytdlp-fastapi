from datetime import datetime, timezone

import aiohttp
from fastapi.logger import logger

from app.utils.config import settings


class TurnstileValidator:
    def __init__(self):
        self.secret_key = settings.TURNSTILE_KEY
        self.verify_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'

    @staticmethod
    def prevalidate(response_token: str) -> bool:
        if 600 < len(response_token) < 500:
            return False
        if not response_token.startswith("0."):
            return False

        return True

    @staticmethod
    def ttl_check(result: dict) -> bool:
        t_string = result.get("challenge_ts")
        if not t_string:
            return False

        parsed_time = datetime.strptime(t_string, '%Y-%m-%dT%H:%M:%S.%fZ')
        parsed_time = parsed_time.replace(tzinfo=timezone.utc)

        current_utc_time = datetime.now(timezone.utc)
        time_difference = current_utc_time - parsed_time

        if time_difference.total_seconds() > 60:
            return False

        return True

    async def validate(self, response_token: str) -> bool:
        if settings.SECRET_KEY == "XXXX.DUMMY.TOKEN.XXXX":
            return True
        if not self.prevalidate(response_token):
            return False

        payload = {
            'secret': self.secret_key,
            'response': response_token,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.verify_url, data=payload) as resp:
                if resp.status != 200:
                    return False

                result = await resp.json()
                logger.info(f"Turnstile response: {result}")

                if not self.ttl_check(result):
                    return False

                return result.get('success', False)
