# 鳞迹

这是基于 `IMPLEMENTATION_PLAN.md` 落地的第一版可运行 MVP，包含 Vue 3 前端和 FastAPI 后端。

## 已实现

- JWT 注册、登录、刷新令牌和当前用户接口
- 用户隔离的宠物档案 CRUD
- 成长记录 CRUD 和体重/体长 ECharts 曲线
- 智能喂食建议、喂食记录和自动生成下次喂食提醒
- 养护提醒列表、今日待办和完成状态
- PC 侧边导航与移动端底部导航的响应式界面

## 启动后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

后端默认运行在 `http://127.0.0.1:8000`，SQLite 数据库文件会自动创建为 `backend/reptilecare.db`。

## 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://127.0.0.1:5173`，`/api` 请求会代理到后端。

## Windows 一键启动

仓库根目录提供了 `start-all.bat`，会在独立命令行窗口里依次启动：

- FastAPI API
- QQ 群机器人监听进程
- QQ 每日汇总 worker
- Vite 前端开发服务器

首次运行时，如果 `backend/.env` 不存在，脚本会自动用 `backend/.env.example` 复制一份。双击运行，或在仓库根目录执行：

```bash
start-all.bat
```

如果你只想手动启动：

```bash
cd backend
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

```bash
cd backend
venv\Scripts\python.exe -m app.workers.qq_group_bot
```

```bash
cd backend
venv\Scripts\python.exe -m app.workers.reminder_summary_worker
```

```bash
cd frontend
npm run dev
```

## 后续建议

- 引入 Alembic 管理迁移，而不是启动时自动建表
- 补邮件验证、找回密码、照片上传和 CSV 导出
- 增加后端 pytest 与前端组件/端到端测试
- 生产部署时把 `SECRET_KEY` 改为强随机值，并切换 PostgreSQL

## QQ 群提醒

后端已预留 QQ 群提醒通道，需要在 `.env` 中配置：

```bash
QQ_BOT_APP_ID=你的机器人 appid
QQ_BOT_SECRET=你的机器人 secret
QQ_BOT_SANDBOX=false
```

部署时建议拆成三个进程：

```bash
# API
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 监听群消息，处理“绑定鳞迹群 LJ-xxxxxx”
python -m app.workers.qq_group_bot

# 每分钟扫描，到设置时间后发送当天养护汇总
python -m app.workers.reminder_summary_worker
```

用户在日历页打开“通知设置”，复制绑定命令，在 QQ 群里 @ 机器人发送即可完成群绑定。
