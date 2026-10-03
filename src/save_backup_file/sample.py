import  logging
import os
from pathlib import Path

from src.util.enums import FolderName
from src.util.drive_files_utils import DriveFilesUtils

# INFOレベル以上を出力する
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] : %(message)s [%(name)s]'
)

# debug 用の main 関数
def main():
    # StoneBlock4 フォルダの中身を取得
    result = DriveFilesUtils.get_file_list_by_folder_name(FolderName.STONE_BLOCK4.value)
    print(result)

    # ファイル名が最大のファイルのIDを取得
    print(max(result, key=lambda x: x["name"])["id"])
    DriveFilesUtils.delete_file(max(result, key=lambda x: x["name"])["id"])

    print(DriveFilesUtils.get_file_list_by_folder_name(FolderName.STONE_BLOCK4.value))

# def main():
#     local_file = max(Path(r"C:\Users\skysh\SERVER\FTB_StoneBlock4\ftbbackups3").glob("*.zip"), key=os.path.getmtime,default=None)
#     print(local_file)

if __name__ == "__main__":
    main()
