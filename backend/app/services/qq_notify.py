import httpx

from app.core.config import get_settings


class QQNotifyError(RuntimeError):
    pass


class QQBotNotifier:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def configured(self) -> bool:
        return bool(self.settings.qq_bot_app_id and self.settings.qq_bot_secret)

    async def get_access_token(self) -> str:
        if not self.configured:
            raise QQNotifyError("QQ bot credentials are not configured")

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "https://bots.qq.com/app/getAppAccessToken",
                json={
                    "appId": self.settings.qq_bot_app_id,
                    "clientSecret": self.settings.qq_bot_secret,
                },
            )
        if response.status_code >= 400:
            raise QQNotifyError(f"Failed to fetch QQ access token: {response.text}")

        payload = response.json()
        token = payload.get("access_token") or payload.get("accessToken")
        if not token:
            raise QQNotifyError(f"QQ access token missing in response: {payload}")
        return token

    async def send_group_message(self, group_openid: str, content: str) -> None:
        token = await self.get_access_token()
        base_url = "https://sandbox.api.sgroup.qq.com" if self.settings.qq_bot_sandbox else "https://api.sgroup.qq.com"
        content = content if content.startswith("@everyone") else f"@everyone\n{content}"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{base_url}/v2/groups/{group_openid}/messages",
                headers={
                    "Authorization": f"QQBot {token}",
                    "Content-Type": "application/json",
                },
                json={
                    "msg_type": 0,
                    "content": content,
                },
            )
        if response.status_code >= 400:
            raise QQNotifyError(f"QQ group message failed: {response.status_code} {response.text}")


def build_test_message() -> str:
    return "鳞迹测试提醒\n\nQQ群提醒已配置成功。之后每日养护汇总会发送到这个群。"
