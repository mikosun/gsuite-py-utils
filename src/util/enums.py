from enum import StrEnum, IntEnum


class FolderName(StrEnum):
    """
    Google Drive 上のフォルダ名を定義する列挙型クラス
    """
    STONE_BLOCK4 = "Backup4StoneBlock4"
    ATM10 = "Backup4ATM10"

class BackupFilePath(StrEnum):
    """
    バックアップファイルのパスを定義する列挙型クラス
    """
    STONE_BLOCK4 = "./ftbbackups3"
    ATM10 = "../bk"

class CredentialsType(IntEnum):
    """
    認証情報の種類を定義する列挙型クラス
    """
    SERVICE_ACCOUNT = 1
    USER_ACCOUNT = 2