import os.path
import argparse

from logging import getLogger
from pathlib import Path

from src.util.enums import FolderName, BackupFilePath, CredentialsType
from src.util.drive_files_utils import DriveFilesUtils
from src.util.get_credentials import CredentialsManager, AuthStrategyFactory

# ロガー作成
logger = getLogger(__name__)


def main() -> str:
    """
    コマンドライン引数（type）に指定された対象をもとに、Google Drive にファイルをアップロード。
    対象のGoogle Driveフォルダ内の既存のファイルを削除し、ローカルのバックアップファイルをアップロード。

    :return: アップロードされたファイルのID
    """
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="指定した対象に基づき、Google Driveにファイルをアップロードします。")
    parser.add_argument("type",  # 必須項目
                        help="アップロード対象のタイプを指定します。[ATM10, STONE_BLOCK4]",
                        choices=["ATM10", "STONE_BLOCK4"])
    parser.add_argument("--credentials_type",  # 任意項目
                        help="認証情報の種類を指定します。[SERVICE_ACCOUNT, USER_ACCOUNT]",
                        choices=["SERVICE_ACCOUNT", "USER_ACCOUNT"],
                        default="USER_ACCOUNT")
    args = parser.parse_args()

    # Typeに応じて、アップロード対象のフォルダの最新版を取得
    local_file = max(Path(getattr(BackupFilePath, args.type).value).glob("*.zip"),
                     key=os.path.getmtime,
                     default=None)

    if local_file is None:
        # フォルダにバックアップファイルが存在しない場合
        logger.error(f"'{getattr(BackupFilePath, args.type).value}' にバックアップファイルが存在しません。")
        raise FileNotFoundError(f"'{getattr(BackupFilePath, args.type).value}' にバックアップファイルが存在しません。")

    # 認証情報の種類に応じて、認証情報を取得し、DriveFilesUtilsのインスタンスを作成
    drive_files_utils = DriveFilesUtils(
        credentials=CredentialsManager(
            AuthStrategyFactory.create(CredentialsType[args.credentials_type])
        ).get_credentials()
    )

    # 対象のGoogle DriveフォルダIDを取得
    drive_folder_id = drive_files_utils.get_folder_id(getattr(FolderName, args.type).value)

    # Typeに応じて、Google Drive上の対象フォルダの既存ファイル(最新)を削除
    drive_file_lists = drive_files_utils.get_file_list(drive_folder_id)
    if drive_file_lists is not None and len(drive_file_lists) > 0:
        drive_files_utils.delete_file(max(drive_file_lists, key=lambda x: x["name"])["id"])

        if len(drive_file_lists) > 1:
            # 複数のファイルが存在する場合、警告ログを出力
            logger.warning(
                f"'{getattr(FolderName, args.type).value}' に複数のファイルが存在しました。最新のファイルを削除しました。")

    # Google Driveにアップロード
    return drive_files_utils.upload_file(
        local_file,
        drive_folder_id)


if __name__ == "__main__":
    main()
