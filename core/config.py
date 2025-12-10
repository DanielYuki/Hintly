"""
Configuration management for Hintly.

Loads environment variables and manages paths.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration loaded from environment."""

    # API Keys
    anthropic_api_key: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""

    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    credentials_path: Optional[Path] = None
    token_path: Path = field(default_factory=lambda: Path.home() / ".hintly" / "token.json")

    # Output directories
    reports_dir: Path = field(default_factory=lambda: Path("outputs/reports"))
    solutions_dir: Path = field(default_factory=lambda: Path("outputs/solutions"))
    exports_dir: Path = field(default_factory=lambda: Path("outputs/exports"))

    # Google OAuth2 scopes
    scopes: list[str] = field(
        default_factory=lambda: [
            "https://www.googleapis.com/auth/classroom.courses.readonly",
            "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
            "https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
            "https://www.googleapis.com/auth/classroom.announcements.readonly",
        ]
    )

    def __post_init__(self):
        """Resolve relative paths to absolute paths."""
        if not self.reports_dir.is_absolute():
            self.reports_dir = self.base_dir / self.reports_dir
        if not self.solutions_dir.is_absolute():
            self.solutions_dir = self.base_dir / self.solutions_dir
        if not self.exports_dir.is_absolute():
            self.exports_dir = self.base_dir / self.exports_dir

        # Ensure directories exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.solutions_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.token_path.parent.mkdir(parents=True, exist_ok=True)

    def validate(self) -> list[str]:
        """
        Validate configuration.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self.anthropic_api_key:
            errors.append("ANTHROPIC_API_KEY is not set")

        if not self.google_client_id:
            errors.append("GOOGLE_CLIENT_ID is not set")

        if not self.google_client_secret:
            errors.append("GOOGLE_CLIENT_SECRET is not set")

        return errors

    @property
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return len(self.validate()) == 0


def get_config(env_path: Optional[Path] = None) -> Config:
    """
    Load configuration from environment.

    Args:
        env_path: Optional path to .env file

    Returns:
        Config instance loaded from environment
    """
    # Load .env file
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    # Build config from environment
    config = Config(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        google_client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
        google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
    )

    # Optional: credentials file path
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
    if creds_path:
        config.credentials_path = Path(creds_path)

    # Optional: custom output directories
    reports = os.getenv("HINTLY_REPORTS_DIR")
    if reports:
        config.reports_dir = Path(reports)

    solutions = os.getenv("HINTLY_SOLUTIONS_DIR")
    if solutions:
        config.solutions_dir = Path(solutions)

    exports = os.getenv("HINTLY_EXPORTS_DIR")
    if exports:
        config.exports_dir = Path(exports)

    return config


# Global config instance (lazy loaded)
_config: Optional[Config] = None


def config() -> Config:
    """Get or create the global config instance."""
    global _config
    if _config is None:
        _config = get_config()
    return _config
