import functools
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# これらのスコープを変更した場合は、token.json ファイルを削除してください。
SCOPES = ["https://www.googleapis.com/auth/drive"]

class GetCredentials:

    @staticmethod
    @functools.cache
    def get_credentials() -> Credentials:
        """
        Google Drive API の認証情報を取得。
        :return: 認証情報
        """
        creds = None
        # token.json ファイルにはユーザーのアクセストークンとリフレッシュトークンが保存され、
        # 認証フローが初回完了したときに自動的に作成されます。
        if os.path.exists("../../.gcp/token.json"):
            creds = Credentials.from_authorized_user_file("../../.gcp/token.json", SCOPES)
        # 有効な認証情報がない場合は、ユーザーにログインしてもらいます。
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "../../.gcp/credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # 次回実行のために認証情報を保存します
            with open("../../.gcp/token.json", "w") as token:
                token.write(creds.to_json())
        return creds