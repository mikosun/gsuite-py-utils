from pathlib import Path

import requests
import json
from logging import getLogger

# ロガー作成
logger = getLogger(__name__)


def send_notice(channel_id, message) -> None:
    """
    Discordに通知を送信する関数。

    :param channel_id: チャンネルID
    :param message: 通知メッセージ
    :return: None
    """

    # userディレクトリのdiscord_token.jsonからトークンを取得
    token = json.loads(open(Path.home() / ".gsuite-py-utils" / "discord_token.json", "r").read())["discord_token"]

    # ヘッダとペイロードの設定
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "content": message
    }

    try:
        response = requests.post(f"https://discord.com/api/v10/channels/{channel_id}/messages",
                                 headers=headers,
                                 data=json.dumps(payload))
        if response.status_code in (200, 201):
            logger.info("Discord通知を正常に送信しました。")
        else:
            logger.error(
                f"Discord通知の送信に失敗しました (Status:"
                f" {response.status_code}): {response.text}"
            )
    except Exception as e:
        logger.error(f"Failed to send notice to Discord: {e}")
