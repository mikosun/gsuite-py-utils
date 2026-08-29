import json
import os.path
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# これらのスコープを変更した場合は、token.json ファイルを削除してください。
SCOPES = ["https://www.googleapis.com/auth/drive"]

# バックアップデータを保存するローカルファイルのパス
# LOCAL_FILE = "../resource/ATM10_ServerFiles-7.0_bk20260727_0024.zip"
LOCAL_FILE = "../../resource/backup_data.txt"

# アップロードするファイルのメタデータを設定
CHUNK_SIZE = 256 * 1024 * 1024


def main():
    """
    Google Drive にファイルをアップロード
    :return: アップロードされたファイルのID
    """
    # .gcp/config.json から FOLDER_ID を読み込む
    with open("../../.gcp/config.json", "r") as f:
        config = json.load(f)
        folder_id = config.get("folder_id")

    # バックアップするファイルのメタデータを作成
    file_metadata = {
        "name": os.path.basename(LOCAL_FILE),
        "parents": [folder_id],
    }
    # メディアボディを作成
    media = MediaFileUpload(
        LOCAL_FILE,
        mimetype=None,
        chunksize=CHUNK_SIZE,
        resumable=True
    )

    try:
        print("INFO: 新規アップロード準備中...")

        # Drive v3 API を呼び出し
        service = build("drive", "v3", credentials=get_credentials())

        # アップロードのためのリクエストを作成し
        request = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, name"
        )

        # チャンクごとにアップロードを行う
        print(f"INFO: アップロードを開始します: {LOCAL_FILE}")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                # 進捗率（%）を同じ行に上書き表示
                progress = int(status.progress() * 100)
                sys.stdout.write(f"\r進行状況: {progress}% 完了\r")
                sys.stdout.flush()

        print("INFO: アップロード完了！")
        print(f"INFO: ファイル名: {response.get('name')}")
        print(f"INFO: ファイルID: {response.get('id')}")
        return response.get('id')

    except HttpError as error:
        print(f"An error occurred: {error}")


def get_credentials():
    """
    Google Drive API の認証情報を取得します。
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


if __name__ == "__main__":
    main()
