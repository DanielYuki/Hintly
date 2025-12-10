"""
OAuth2 authentication flow for Google Classroom.

Generates login URLs and handles token persistence.
"""

import json
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from core.config import Config, get_config


class OAuth2Flow:
    """
    Manages OAuth2 authentication for Google Classroom API.

    This class handles:
    - Generating login URLs for user authentication
    - Exchanging authorization codes for tokens
    - Token persistence and refresh
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize OAuth2 flow.

        Args:
            config: Configuration instance (uses global config if not provided)
        """
        self.config = config or get_config()
        self._credentials: Optional[Credentials] = None

    @property
    def token_path(self) -> Path:
        """Path to stored token file."""
        return self.config.token_path

    def check_auth(self) -> bool:
        """
        Check if valid authentication exists.

        Returns:
            True if valid credentials exist, False otherwise
        """
        if self._credentials and self._credentials.valid:
            return True

        if self.token_path.exists():
            try:
                self._credentials = Credentials.from_authorized_user_file(
                    str(self.token_path), self.config.scopes
                )
                if self._credentials.valid:
                    return True
                if self._credentials.expired and self._credentials.refresh_token:
                    self._credentials.refresh(Request())
                    self._save_token()
                    return True
            except Exception:
                return False

        return False

    def get_credentials(self) -> Optional[Credentials]:
        """
        Get valid credentials if available.

        Returns:
            Valid Credentials instance or None
        """
        if self.check_auth():
            return self._credentials
        return None

    def get_login_url(self) -> str:
        """
        Generate OAuth2 login URL for user authentication.

        The user should visit this URL to grant access to their
        Google Classroom data.

        Returns:
            OAuth2 authorization URL
        """
        flow = self._create_flow()
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return auth_url

    def authenticate_with_code(self, auth_code: str) -> bool:
        """
        Complete authentication with authorization code.

        Args:
            auth_code: Authorization code from OAuth2 callback

        Returns:
            True if authentication successful
        """
        try:
            flow = self._create_flow()
            flow.fetch_token(code=auth_code)
            self._credentials = flow.credentials
            self._save_token()
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def run_local_server(self, port: int = 8080) -> bool:
        """
        Run OAuth2 flow with local server callback.

        This opens a browser window for the user to authenticate.
        More convenient for local development.

        Args:
            port: Local server port for callback

        Returns:
            True if authentication successful
        """
        try:
            flow = self._create_flow()
            self._credentials = flow.run_local_server(port=port)
            self._save_token()
            return True
        except Exception as e:
            print(f"Local server authentication failed: {e}")
            return False

    def revoke(self) -> bool:
        """
        Revoke and clear stored credentials.

        Returns:
            True if credentials were cleared
        """
        if self.token_path.exists():
            self.token_path.unlink()
        self._credentials = None
        return True

    def _create_flow(self) -> InstalledAppFlow:
        """Create OAuth2 flow from config."""
        # Check for credentials file first
        if self.config.credentials_path and self.config.credentials_path.exists():
            return InstalledAppFlow.from_client_secrets_file(
                str(self.config.credentials_path),
                self.config.scopes,
                redirect_uri="http://localhost:8080/",
            )

        # Otherwise, create from client ID/secret
        client_config = {
            "installed": {
                "client_id": self.config.google_client_id,
                "client_secret": self.config.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8080/"],
            }
        }
        return InstalledAppFlow.from_client_config(
            client_config,
            self.config.scopes,
            redirect_uri="http://localhost:8080/",
        )

    def _save_token(self) -> None:
        """Save credentials to token file."""
        if self._credentials:
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, "w") as f:
                f.write(self._credentials.to_json())


def get_auth_status() -> dict:
    """
    Get current authentication status.

    Returns:
        Dict with 'authenticated' bool and optional 'email'
    """
    flow = OAuth2Flow()
    if flow.check_auth():
        return {"authenticated": True, "token_path": str(flow.token_path)}
    return {"authenticated": False, "token_path": str(flow.token_path)}
