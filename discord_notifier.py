from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Optional, Any
import requests


@dataclass
class DiscordDMNotifier:
    bot_token: str
    user_id: str
    timeout: int = 8
    _dm_channel_id: Optional[str] = None

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json",
        }

    def _ensure_dm_channel(self) -> Optional[str]:
        if self._dm_channel_id:
            return self._dm_channel_id

        # Create (or fetch) a DM channel with the user
        url = "https://discord.com/api/v10/users/@me/channels"
        r = requests.post(
            url,
            headers=self._headers,
            json={"recipient_id": self.user_id},
            timeout=self.timeout,
        )
        r.raise_for_status()
        self._dm_channel_id = r.json()["id"]
        return self._dm_channel_id

    def _post_message(self, payload: dict[str, Any]) -> None:
        channel_id = self._ensure_dm_channel()
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"

        while True:
            r = requests.post(
                url, headers=self._headers, json=payload, timeout=self.timeout
            )

            if r.status_code == 429:
                data = r.json()
                retry_after = float(data.get("retry_after", 1.0))
                time.sleep(retry_after)
                continue

            r.raise_for_status()
            return

    def send_dm(self, content: str) -> None:
        self._post_message({"content": content[:1900]})

    def send_embed(self, *, content: str = "", embed: dict[str, Any]) -> None:
        """
        Sends DM with an embed; can include 'content' too.
        """
        payload: dict[str, Any] = {"embeds": [embed]}
        if content:
            payload["content"] = content[:1900]
        self._post_message(payload)
