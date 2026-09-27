from src.util.enums import FolderName
from src.util.get_folder_id import GetFolderId


# debug 用の main 関数
def main():
    result = GetFolderId.get_folder_id(FolderName.STONE_BLOCK4.value)
    print(result)


if __name__ == "__main__":
    main()
