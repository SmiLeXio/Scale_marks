import json
import time
from datetime import date
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE_URL = "http://127.0.0.1:8000/api"


def request(method: str, path: str, payload: dict | None = None, token: str | None = None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else None
    except HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise RuntimeError(f"{method} {path} failed: {exc.code} {detail}") from exc


def wait_for_api() -> None:
    for _ in range(30):
        try:
            request("GET", "/health")
            return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("API did not become ready")


def main() -> None:
    wait_for_api()
    suffix = int(time.time())
    auth = request(
        "POST",
        "/auth/register",
        {
            "email": f"smoke-{suffix}@example.com",
            "password": "smoke-password",
            "nickname": "Smoke Tester",
        },
    )
    token = auth["access_token"]
    me = request("GET", "/auth/me", token=token)
    pet = request(
        "POST",
        "/pets",
        {
            "name": "小青",
            "species": "玉米蛇",
            "morph": "原色",
            "birth_date": "2025-05-01",
            "gender": "female",
            "weight": 120.0,
            "length": 68.0,
            "feeding_cycle": 7,
            "last_feeding_date": "2026-06-20",
            "notes": "smoke test pet",
        },
        token,
    )
    growth = request(
        "POST",
        f"/pets/{pet['id']}/growth",
        {"date": str(date.today()), "weight": 124.5, "length": 69.2, "note": "稳定增长"},
        token,
    )
    suggestion = request("GET", f"/pets/{pet['id']}/feeding/calculate", token=token)
    feeding = request(
        "POST",
        f"/pets/{pet['id']}/feeding",
        {
            "date": str(date.today()),
            "food_type": "小鼠",
            "food_weight": 18.0,
            "is_success": True,
            "refused": False,
            "note": "进食顺利",
        },
        token,
    )
    reminders = request("GET", "/reminders", token=token)
    qq_binding = request("GET", "/notifications/qq-group", token=token)
    custom_reminder = request(
        "POST",
        "/reminders",
        {
            "pet_id": pet["id"],
            "type": "calcium",
            "title": "补钙",
            "description": "每 10 天循环",
            "due_date": f"{date.today()}T09:00:00",
            "repeat_type": "custom",
            "repeat_interval_days": 10,
        },
        token,
    )

    print(
        json.dumps(
            {
                "health": "ok",
                "user": me["email"],
                "pet": pet["name"],
                "growth_record": growth["id"],
                "suggested_amount": suggestion["suggested_amount"],
                "feeding_record": feeding["id"],
                "reminder_count": len(reminders),
                "qq_binding_code": qq_binding["binding_code"],
                "custom_repeat_days": custom_reminder["repeat_interval_days"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
