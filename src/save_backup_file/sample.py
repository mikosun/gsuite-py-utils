import logging
import os
from pathlib import Path

from src.util.enums import FolderName, CredentialsType
from src.util.drive_files_utils import DriveFilesUtils
from src.util.get_credentials import CredentialsManager, AuthStrategyFactory

# INFOレベル以上を出力する
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] : %(message)s [%(name)s]'
)


# debug 用の main 関数
# def main():
#     # StoneBlock4 フォルダの中身を取得
#     result = DriveFilesUtils.get_file_list_by_folder_name(FolderName.STONE_BLOCK4.value)
#     print(result)
#
#     # ファイル名が最大のファイルのIDを取得
#     print(max(result, key=lambda x: x["name"])["id"])
#     DriveFilesUtils.delete_file(max(result, key=lambda x: x["name"])["id"])
#
#     print(DriveFilesUtils.get_file_list_by_folder_name(FolderName.STONE_BLOCK4.value))

def main():
    # アルゴリズムを選択して認証情報を取得
    drive_files_utils = DriveFilesUtils(
        credentials=CredentialsManager(
            AuthStrategyFactory.create(CredentialsType.USER_ACCOUNT)
        ).get_credentials()
    )

    result = drive_files_utils.get_file_list_by_folder_name(FolderName.STONE_BLOCK4.value)
    print(result)


if __name__ == "__main__":
    main()
