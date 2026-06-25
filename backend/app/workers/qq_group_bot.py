import asyncio
import re

import botpy
from botpy import logging
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.notification import QQGroupBinding


logger = logging.get_logger()
BIND_PATTERN = re.compile(r"绑定鳞迹群\s*(LJ-\d{6})", re.IGNORECASE)


class LinjiQQGroupBot(botpy.Client):
    async def on_group_at_message_create(self, message) -> None:
        content = (message.content or "").strip()
        matched = BIND_PATTERN.search(content)
        if not matched:
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                msg_id=message.id,
                content="发送：绑定鳞迹群 LJ-123456，即可把这个群绑定为鳞迹提醒群。",
            )
            return

        code = matched.group(1).upper()
        with SessionLocal() as db:
            binding = db.scalar(select(QQGroupBinding).where(QQGroupBinding.binding_code == code))
            if not binding:
                reply = "绑定码无效或已过期，请在鳞迹通知设置里重新生成绑定码。"
            else:
                binding.group_openid = message.group_openid
                binding.enabled = True
                db.commit()
                reply = "绑定成功。之后鳞迹的每日养护汇总会发送到这个群。"

        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            content=reply,
        )


async def main() -> None:
    settings = get_settings()
    if not settings.qq_bot_app_id or not settings.qq_bot_secret:
        raise RuntimeError("QQ_BOT_APP_ID and QQ_BOT_SECRET are required")

    intents = botpy.Intents(public_messages=True)
    client = LinjiQQGroupBot(
        intents=intents,
        is_sandbox=settings.qq_bot_sandbox,
        ext_handlers=False,
    )
    await client.start(appid=settings.qq_bot_app_id, secret=settings.qq_bot_secret)


if __name__ == "__main__":
    asyncio.run(main())
