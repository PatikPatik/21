import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyUrl

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    BOT_TOKEN: str
    BASE_URL: str
    WEBHOOK_SECRET: str = Field(default="change-me")
    ENV: str = Field(default="prod")
    SENTRY_DSN: str | None = None
    DATABASE_URL: str | None = None
    ADMIN_IDS: List[int] = Field(default_factory=list)

    @classmethod
    def from_env(cls) -> "Settings":
        # Parse comma-separated ADMIN_IDS if present
        admin_ids_raw = os.getenv("ADMIN_IDS", "")
        admin_ids = []
        for x in admin_ids_raw.split(","):
            x = x.strip()
            if not x:
                continue
            try:
                admin_ids.append(int(x))
            except ValueError:
                pass
        st = cls()  # will read from env/.env
        st.ADMIN_IDS = admin_ids
        return st
