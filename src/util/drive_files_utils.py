import os
import sys
from logging import getLogger
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from src.util.get_credentials import GetCredentials

# ロガー作成
logger = getLogger(__name__)


class DriveFilesUtils:
    """
    Google Drive のファイル操作に関するユーティリティクラス
    """

    @staticmethod
    def get_folder_id(folder_name: str) -> str:
        """
        folder_name に対応するフォルダIDを取得。

        :param folder_name: フォルダ名
        :return: フォルダID
        """
        # Drive v3 API を呼び出し
        service = build("drive",
                        "v3",
                        credentials=GetCredentials.get_credentials())

        # query パラメータを使用して、特定のフォルダ名に一致するフォルダを検索
        # 自分がオーナーのフォルダかつ、引数のフォルダ名
        query = ("'me' in owners "
                 "and mimeType='application/vnd.google-apps.folder' "
                 "and name = '" + folder_name + "'")

        # files().list メソッドを使用して、フォルダを検索
        result = service.files().list(q=query).execute()

        if result is None or "files" not in result or len(result["files"]) == 0:
            logger.error(f"'{folder_name}' が見つかりませんでした。")
            raise RuntimeError(f"{folder_name} に対応するフォルダIDが見つかりませんでした。")
        else:
            logger.info(f"'{folder_name}' のIDを取得しました。")
            return result["files"][0]["id"]

    @staticmethod
    def get_file_list(folder_id: str) -> list:
        """
        指定されたフォルダIDに含まれるファイルのリストを取得。

        :param folder_id: フォルダID
        :return: ファイルのリスト
        """
        # Drive v3 API を呼び出し
        service = build("drive",
                        "v3",
                        credentials=GetCredentials.get_credentials())

        # query パラメータを使用して、特定のフォルダIDに含まれるファイルを検索
        query = f"'{folder_id}' in parents and trashed = false"

        # files().list メソッドを使用して、ファイルを検索
        result = service.files().list(q=query).execute()

        if result is None or "files" not in result:
            # 取得できなかった場合はエラーを返す
            logger.error(f"フォルダID '{folder_id}' に含まれるファイルが見つかりませんでした。")
            raise RuntimeError(f"フォルダID '{folder_id}' に含まれるファイルが見つかりませんでした。")

        # 取得できた場合
        # ファイルIDとファイル名のリストにmapして返却
        logger.info(f"フォルダID '{folder_id}' に含まれるファイルのリストを取得しました。")
        return list(map(lambda f: {"id": f["id"], "name": f["name"]}, result["files"]))

    @staticmethod
    def get_file_list_by_folder_name(folder_name: str) -> list:
        """
        指定されたフォルダ名に含まれるファイルのリストを取得。

        :param folder_name: フォルダ名
        :return: ファイルのリスト
        """
        return DriveFilesUtils.get_file_list(
            DriveFilesUtils.get_folder_id(folder_name)
        )

    @staticmethod
    def delete_file(file_id: str) -> None:
        """
        指定されたファイルIDのファイルを削除。

        :param file_id: ファイルID
        """
        # Drive v3 API を呼び出し
        service = build("drive",
                        "v3",
                        credentials=GetCredentials.get_credentials())

        try:
            # files().delete メソッドを使用して、ファイルを削除
            service.files().delete(fileId=file_id).execute()
            logger.info(f"ファイルID '{file_id}' のファイルを削除しました。")
        except Exception as e:
            logger.error(f"ファイルID '{file_id}' のファイルの削除中にエラーが発生しました: {e}")
            raise RuntimeError(f"ファイルID '{file_id}' のファイルの削除中にエラーが発生しました: {e}")

    @staticmethod
    def upload_file(local_file: Path,
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
                        credentials=GetCredentials.get_credentials())

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
