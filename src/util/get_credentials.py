from abc import ABC, abstractmethod
from pathlib import Path

# Google Auth 関連のインポート
from google.auth.credentials import Credentials
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials as UserCredentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from src.util.enums import CredentialsType

SCOPES = ["https://www.googleapis.com/auth/drive"]


# ==========================================
# 1. Strategy Interface (抽象戦略)
# ==========================================
class AuthStrategy(ABC):
    """
    認証アルゴリズムの共通インターフェース
    """

    @abstractmethod
    def get_credentials(self) -> Credentials:
        pass


# ==========================================
# 2. Concrete Strategy (具体的な戦略の実装)
# ==========================================
class ServiceAccountAuthStrategy(AuthStrategy):
    """
    サービスアカウントを使用した認証戦略
    """

    def __init__(self, scopes: list[str] = None):
        self.scopes = scopes or SCOPES

    def get_credentials(self) -> Credentials:
        key_path = self._get_service_account_path()

        # サービスアカウント認証情報を生成
        return service_account.Credentials.from_service_account_file(
            str(key_path),
            scopes=self.scopes
        )

    def _get_service_account_path(self) -> Path:
        """
        ホームディレクトリ (~/.gsuite-py-utils/service_account.json) から
        サービスアカウントキーのパスを取得します。
        """
        key_path = Path.home() / ".gsuite-py-utils" / "service_account.json"

        if not key_path.exists():
            raise FileNotFoundError(
                f"サービスアカウントのキーファイルが見つかりません。\n"
                f"以下の場所に 'service_account.json' を配置してください:\n"
                f"  -> {key_path}"
            )

        return key_path


class UserAccountAuthStrategy(AuthStrategy):
    """
    個人アカウント (OAuth 2.0) を使用した認証戦略
    """

    def __init__(self, scopes: list[str] = None):
        self.scopes = scopes or SCOPES

    def get_credentials(self) -> Credentials:
        client_secret_path = self._get_client_credentials_path()
        token_path = Path.home() / ".gsuite-py-utils" / "token.json"

        creds = None

        # 既存のトークンがあれば読み込む
        if token_path.exists():
            creds = UserCredentials.from_authorized_user_file(str(token_path), self.scopes)

        # 有効な認証情報がない、または期限切れの場合は再認証プロセスへ
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(client_secret_path), self.scopes
                )
                # ブラウザを起動して認証
                creds = flow.run_local_server(port=0)

            # 新しいトークンを保存
            with open(token_path, "w") as token_file:
                token_file.write(creds.to_json())

        return creds

    def _get_client_credentials_path(self) -> Path:
        """
        OAuth 2.0 用のクレデンシャルファイルのパスを取得します。
        """
        credential_path = Path.home() / ".gsuite-py-utils" / "credentials.json"

        if not credential_path.exists():
            raise FileNotFoundError(
                f"OAuth 2.0 用のクレデンシャルファイルが見つかりません。\n"
                f"Google Cloud Console から OAuth 2.0 クライアント ID を作成し、\n"
                f"以下の場所に 'credentials.json' を配置してください:\n"
                f"  -> {credential_path}"
            )
        return credential_path


# ==========================================
# 3. Context (コンテキスト・利用側クラス)
# ==========================================
class CredentialsManager:
    """
    認証の実行を管理するコンテキストクラス。
    キャッシュを保持し、不要なファイル読み込みやAPI通信を防ぎます。
    """

    def __init__(self, strategy: AuthStrategy):
        self._strategy = strategy
        self._cached_credentials = None

    def set_strategy(self, strategy: AuthStrategy) -> None:
        """
        実行時に認証アルゴリズムを動的に切り替えます。
        切り替えた場合、キャッシュはクリアされます。
        """
        self._strategy = strategy
        self._cached_credentials = None

    def get_credentials(self) -> Credentials:
        """
        キャッシュされた認証情報を返すか、新たに取得します。
        """
        if self._cached_credentials is None:
            self._cached_credentials = self._strategy.get_credentials()
        return self._cached_credentials


# ==========================================
# 4. Factory (列挙型から生成するファクトリ)
# ==========================================
class AuthStrategyFactory:
    """
    列挙型（CredentialsType）から適切な認証戦略を生成するファクトリ
    """

    @staticmethod
    def create(auth_type: CredentialsType) -> AuthStrategy:
        if auth_type == CredentialsType.SERVICE_ACCOUNT:
            return ServiceAccountAuthStrategy()
        elif auth_type == CredentialsType.USER_ACCOUNT:
            return UserAccountAuthStrategy()
        else:
            raise ValueError(f"未対応の認証タイプです: {auth_type}")
