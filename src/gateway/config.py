"""Application settings for the Q&A routing gateway."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CMU Student Support Q&A Gateway"
    # auto | ollama | stub
    llm_mode: str = "auto"
    ollama_host: str = "http://127.0.0.1:11434"
    ollama_model: str = "tinyllama"
    request_timeout_seconds: float = 60.0
    disclaimer: str = (
        "For specific course policies, defer to your syllabus. "
        "For official immigration status, consult OIE."
    )


settings = Settings()
