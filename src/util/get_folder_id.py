import logging

from googleapiclient.discovery import build

from src.util.get_credentials import GetCredentials


class GetFolderId:

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
            logging.error(f"'{folder_name}' が見つかりませんでした。")
            raise RuntimeError(f"{folder_name} に対応するフォルダIDが見つかりませんでした。")
        else:
            logging.info(f":'{folder_name}' のIDを取得しました。")
            return result["files"][0]["id"]
