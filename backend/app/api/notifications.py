from secrets import randbelow

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.notification import NotificationLog, QQGroupBinding
from app.schemas.notification import (
    QQGroupBindingRead,
    QQGroupBindingUpdate,
    QQGroupManualBind,
    TestNotificationResponse,
)
from app.services.qq_notify import QQBotNotifier, QQNotifyError, build_test_message

router = APIRouter(prefix="/notifications", tags=["notifications"])


def generate_binding_code() -> str:
    return f"LJ-{randbelow(900000) + 100000}"


def get_or_create_binding(db: DbSession, user_id: str) -> QQGroupBinding:
    binding = db.scalar(select(QQGroupBinding).where(QQGroupBinding.user_id == user_id))
    if binding:
        return binding

    binding = QQGroupBinding(user_id=user_id, binding_code=generate_binding_code())
    db.add(binding)
    db.commit()
    db.refresh(binding)
    return binding


@router.get("/qq-group", response_model=QQGroupBindingRead)
def read_qq_group_binding(current_user: CurrentUser, db: DbSession) -> QQGroupBinding:
    return get_or_create_binding(db, current_user.id)


@router.post("/qq-group/regenerate-code", response_model=QQGroupBindingRead)
def regenerate_qq_group_code(current_user: CurrentUser, db: DbSession) -> QQGroupBinding:
    binding = get_or_create_binding(db, current_user.id)
    binding.binding_code = generate_binding_code()
    db.commit()
    db.refresh(binding)
    return binding


@router.put("/qq-group", response_model=QQGroupBindingRead)
def update_qq_group_binding(
    payload: QQGroupBindingUpdate,
    current_user: CurrentUser,
    db: DbSession,
) -> QQGroupBinding:
    binding = get_or_create_binding(db, current_user.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(binding, key, value)
    db.commit()
    db.refresh(binding)
    return binding


@router.post("/qq-group/manual-bind", response_model=QQGroupBindingRead)
def manual_bind_qq_group(
    payload: QQGroupManualBind,
    current_user: CurrentUser,
    db: DbSession,
) -> QQGroupBinding:
    binding = get_or_create_binding(db, current_user.id)
    binding.group_openid = payload.group_openid
    binding.enabled = True
    db.commit()
    db.refresh(binding)
    return binding


@router.post("/qq-group/test", response_model=TestNotificationResponse)
async def test_qq_group_notification(
    current_user: CurrentUser,
    db: DbSession,
) -> TestNotificationResponse:
    binding = get_or_create_binding(db, current_user.id)
    if not binding.group_openid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QQ group is not bound")

    notifier = QQBotNotifier()
    try:
        await notifier.send_group_message(binding.group_openid, build_test_message())
    except QQNotifyError as exc:
        db.add(
            NotificationLog(
                user_id=current_user.id,
                reminder_id=None,
                channel="qq_group",
                target_id=binding.group_openid,
                status="failed",
                error_message=str(exc),
            )
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    db.add(
        NotificationLog(
            user_id=current_user.id,
            reminder_id=None,
            channel="qq_group",
            target_id=binding.group_openid,
            status="sent",
            error_message=None,
        )
    )
    db.commit()
    return TestNotificationResponse(status="sent", detail="测试消息已发送")
