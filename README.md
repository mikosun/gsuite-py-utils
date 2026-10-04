# gsuite-py-util

GoogleAPIを使用したpythonツールのユーティリティリポジトリ。

---

### 動作確認済バージョン

| Category                 | Version |
|--------------------------|---------|
| Python                   | 3.14.7  |
| google-api-python-client | 2.199.0 |
| google-api-core          | 2.34.0  |
| google-auth              | 2.57.0  |
| google-auth-httplib2     | 0.4.2   |
| google-auth-oauthlib     | 1.4.1   |

### 開発環境構築

1. リポジトリをクローン  
   ```git clone  https://github.com/mikosun/gsuite-py-utils.git```
2. 対象pythonをインストール
3. 必要なライブラリをインストール(
   詳細は[公式ドキュメント](https://developers.google.com/workspace/drive/labels/quickstart/python)参照)  
   ```pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib```
4. ビルドツールのPyInstallerをインストール  
   ```pip install pyinstaller ```

### GoogleCloudのAPIを使用するための設定

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセスし、プロジェクトを作成する。
2. 「APIとサービス」→「ライブラリ」
3. 使用するAPIを有効化する。
4. 「認証情報」→「認証情報を作成」→「OAuth クライアント ID」を作成する。

※ 詳しい手順は[公式ドキュメント](https://developers.google.com/workspace/drive/labels/quickstart/python)を参照してください。

---

## 各種ツールの使用方法

### save_backup_file.py

#### ビルド

PyInstallerを使用して単一の実行ファイルにビルドします。  
※ ファイルは`dist`ディレクトリに生成されます。

```bash
python -m PyInstaller --onefile src/save_backup_file/save_backup_file.py
```

#### 使用方法

実行には、ユーザーのホームディレクトリ配下に認証用のファイルが配置されている必要があります。  
※ OAuth 2.0での初回認証完了後、同ディレクトリに `token.json` が自動生成されます。

```text
~ (ユーザーのホームディレクトリ)
└── .gsuite-py-utils/
    ├── client_secret.json (OAuth 2.0認証用クライアントシークレット)
    └── service_account.json (サービスアカウント認証用キー ※サービスアカウント使用時)
```

また、このツールは以下のようなサーバーファイルのディレクトリ構成を想定しています。

```text
ROOT_DIR/(任意の名称)
└── FTB_StoneBlock4/(任意の名称)
    ├── save_backup_file.exe(本ツール)
    ├── ftbbackups3/
        ├── (StoneBlock4のバックアップファイル)
        └── ...
    └── ...
└── ATM10_ServerFiles-7.0/(任意の名称)
    ├── save_backup_file.exe(本ツール)
    └── ...
└── bk/
    ├── (ATM10のバックアップファイル)
    └── ...
```

#### 実行

生成されたexeファイルにバックアップ対象のタイプを引数として渡して実行します。

**コマンドライン引数**

* `type` (必須): アップロード対象のタイプを指定します。指定可能な値は `ATM10` または `STONE_BLOCK4` です。
* `--credentials_type` (任意): 認証方式を指定します。指定可能な値は `SERVICE_ACCOUNT` または `USER_ACCOUNT` です。  
  ※ 指定しない場合は、デフォルトで `USER_ACCOUNT` が使用されます。  
  ※ `SERVICE_ACCOUNT`はサービスアカウント自体のストレージ容量割り当ての関係上動きません。

**実行コマンド例**

```bash
.\save_backup_file.exe STONE_BLOCK4 --credentials_type USER_ACCOUNT
```
