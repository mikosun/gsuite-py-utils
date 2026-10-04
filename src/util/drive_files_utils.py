import os
import sys
from logging import getLogger
from pathlib import Path

from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# ロガー作成
logger = getLogger(__name__)


class DriveFilesUtils:
    """
    Google Drive のファイル操作に関するユーティリティクラス
    """

    def __init__(self, credentials: Credentials):
        self.credentials = credentials

    def get_folder_id(self, folder_name: str) -> str:
        """
        folder_name に対応するフォルダIDを取得。

        :param folder_name: フォルダ名
        :return: フォルダID
        """
        # Drive v3 API を呼び出し
        service = build("drive",
                        "v3",
                        credentials=self.credentials)

        # query パラメータを使用して、特定のフォルダ名に一致するフォルダを検索
        # 自分がオーナーのフォルダかつ、引数のフォルダ名
        query = f"mimeType='application/vnd.google-apps.folder' and name = '{folder_name}' and trashed = false"

        # files().list メソッドを使用して、フォルダを検索
        result = service.files().list(q=query).execute()

        if result is None or "files" not in result or len(result["files"]) == 0:
            logger.error(f"'{folder_name}' が見つかりませんでした。")
            raise RuntimeError(f"{folder_name} に対応するフォルダIDが見つかりませんでした。")
        else:
            logger.info(f"'{folder_name}' のIDを取得しました。")
            return result["files"][0]["id"]

    def get_file_list(self, folder_id: str) -> list:
        """
        指定されたフォルダIDに含まれるファイルのリストを取得。

        :param folder_id: フォルダID
        :return: ファイルのリスト
        """
        # Drive v3 API を呼び出し
        service = build("drive",
                        "v3",
                        credentials=self.credentials)

        # query パラメータを使用して、特定のフォルダIDに含まれるファイルを検索
        query = f"'{folder_id}' in parents and trashed = false"

        try:
            # files().list メソッドを使用して、ファイルを検索
            result = service.files().list(q=query).execute()
        except HttpError as error:
            # API呼び出し自体に失敗した場合（権限エラー、ネットワークエラーなど）
            logger.error(f"フォルダID '{folder_id}' のファイルリスト取得APIでエラーが発生しました: {error}")
            raise RuntimeError(f"フォルダID '{folder_id}' のファイルリスト取得APIでエラーが発生しました: {error}")

        # 例外が発生せずにここまで来た場合、result には必ず "files" キーが含まれる（0件の場合は空リスト）
        files = result.get("files", [])

        if not files:
            logger.info(f"フォルダID '{folder_id}' は空です（ファイルが存在しません）。")
            return []

        # 取得できた場合
        # ファイルIDとファイル名のリストにmapして返却
        logger.info(f"フォルダID '{folder_id}' に含まれるファイルのリストを取得しました。({len(files)}件)")
        return [{"id": f["id"], "name": f["name"]} for f in files]

    def get_file_list_by_folder_name(self, folder_name: str) -> list:
        """
        指定されたフォルダ名に含まれるファイルのリストを取得。

        :param folder_name: フォルダ名
        :return: ファイルのリスト
        """
        return self.get_file_list(
            self.get_folder_id(folder_name)
        )

    def delete_file(self, file_id: str) -> None:
        """
        指定されたファイルIDのファイルを削除。

        :param file_id: ファイルID
        """
        # Drive v3 API を呼び出し
        service = build("drive",
                        "v3",
                        credentials=self.credentials)

        try:
            # files().delete メソッドを使用して、ファイルを削除
            service.files().delete(fileId=file_id).execute()
            logger.info(f"ファイルID '{file_id}' のファイルを削除しました。")
        except Exception as e:
            logger.error(f"ファイルID '{file_id}' のファイルの削除中にエラーが発生しました: {e}")
            raise RuntimeError(f"ファイルID '{file_id}' のファイルの削除中にエラーが発生しました: {e}")

    def upload_file(self,
                    local_file: Path,
                    drive_folder_id: str,
                    chunk_size: int = 256 * 1024 * 1024) -> str:
        """
        指定されたローカルファイルをGoogle Driveにアップロード。

        :param local_file: アップロードするローカルファイルのパス
        :param drive_folder_id: ファイルをアップロードするGoogle Drive上のフォルダID
        :param chunk_size: アップロード時のチャンクサイズ(デフォルト: 256MB)
        :return: アップロードされたファイルのID
        """
        # Drive v3 API を呼び出し
        service = build("drive",
                        "v3",
                        credentials=self.credentials)

        try:
            # アップロードのためのリクエストを作成
            request = service.files().create(
                body={
                    # ローカルファイル名を取得して設定
                    "name": os.path.basename(local_file),
                    # Google Drive上のフォルダIDを指定
                    "parents": [drive_folder_id],
                },
                media_body=MediaFileUpload(
                    local_file,
                    mimetype=None,
                    chunksize=chunk_size,
                    resumable=True
                ),
                fields="id, name"
            )

            # チャンクごとにアップロードを行う
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    # 進捗率（%）を同じ行に上書き表示
                    progress = int(status.progress() * 100)
                    sys.stdout.write(f"\r進行状況: {progress}% 完了\r")
                    sys.stdout.flush()

            logger.info("アップロード完了！")
            logger.info(f"ファイル名: {response.get('name')}")
            logger.info(f"ファイルID: {response.get('id')}")
            return response.get('id')

        except HttpError as error:
            logger.error(f"Google Drive へのアップロード中にエラーが発生しました: {error}")
            raise RuntimeError(f"Google Drive へのアップロード中にエラーが発生しました: {error}")
