import os.path
import sys

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from src.util.enums import FolderName
from src.util.get_credentials import GetCredentials
from src.util.get_folder_id import GetFolderId

# バックアップデータを保存するローカルファイルのパス
LOCAL_FILE = "../../resource/2026-09-10-21-15-50.zip"
# LOCAL_FILE = "../../resource/backup_data.txt"

# アップロードするファイルのメタデータを設定
CHUNK_SIZE = 256 * 1024 * 1024


def main():
    """
    Google Drive にファイルをアップロード

    :return: アップロードされたファイルのID
    """
    # バックアップするファイルのメタデータを作成
    file_metadata = {
        "name": os.path.basename(LOCAL_FILE),
        "parents": [GetFolderId.get_folder_id(FolderName.STONE_BLOCK4.value)],
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
        service = build("drive",
                        "v3",
                        credentials=GetCredentials.get_credentials())

        # アップロードのためのリクエストを作成
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


if __name__ == "__main__":
    main()
