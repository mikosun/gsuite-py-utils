from enum import StrEnum

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