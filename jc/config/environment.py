"""Configuration management"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings from environment"""

    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "sqlite:///./jc_production.db"
    DATABASE_BACKUP_PATH: str = "./backups/"
    DATABASE_CHECKPOINT_INTERVAL: int = 3600

    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Session Management
    SESSION_TIMEOUT: int = 3600
    SESSION_MAX_AGE: int = 86400
    SESSION_STORE: str = "sqlite"

    # Voice Configuration
    STT_PROVIDER: str = "openai"
    TTS_PROVIDER: str = "openai"
    VAD_ENABLED: bool = True
    BARGE_IN_ENABLED: bool = True
    VOICE_SAMPLE_RATE: int = 16000

    # Agent Configuration
    DEFAULT_MODEL: str = "gpt-4"
    AGENT_TEMPERATURE: float = 0.7
    AGENT_MAX_TOKENS: int = 2000
    AGENT_MEMORY_SIZE: int = 20
    CONTEXT_WINDOW_SIZE: int = 8000

    # Autonomy & Safety
    AUTONOMY_LEVEL: str = "bounded"
    REQUIRE_APPROVAL_FOR_MUTATIONS: bool = True
    MAX_AUTONOMOUS_ACTIONS: int = 100
    EMERGENCY_STOP_ENABLED: bool = True

    # Security
    ZERO_TRUST_ENABLED: bool = True
    SECRETS_BACKEND: str = "env"
    AUDIT_LOG_ENABLED: bool = True
    AUDIT_LOG_PATH: str = "./logs/audit/"

    # Real-time Runtime
    WORKER_COUNT: int = 4
    EVENT_STREAM_BACKEND: str = "memory"
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30

    # Disaster Recovery
    DISASTER_RECOVERY_MODE: str = "normal"
    BACKUP_ENABLED: bool = True
    BACKUP_INTERVAL: int = 3600
    BACKUP_RETENTION_DAYS: int = 30

    # Monitoring
    METRICS_ENABLED: bool = True
    TRACE_ENABLED: bool = False
    ANOMALY_DETECTION_ENABLED: bool = True
    HEALTH_CHECK_INTERVAL: int = 60

    # Feature Flags
    FEATURE_STREAMING: bool = True
    FEATURE_VOICE: bool = True
    FEATURE_TOOL_CALLING: bool = True
    FEATURE_AUTONOMOUS_EXECUTION: bool = True
    FEATURE_KNOWLEDGE_GRAPH: bool = True

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 1000
    RATE_LIMIT_WINDOW: int = 3600

    # Integration
    WEBHOOK_SIGNATURE_SECRET: str = "your_webhook_secret"
    EXTERNAL_INTEGRATION_TIMEOUT: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
