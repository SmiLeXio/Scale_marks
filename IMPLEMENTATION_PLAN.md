# 爬宠记录网站 - 实现方案

## 1. 项目概述

### 1.1 项目定位
- **产品名称**：爬宠档案 (ReptileCare)
- **核心价值**：帮助爬宠爱好者科学记录宠物档案、追踪成长曲线、智能管理养护计划
- **目标用户**：爬宠爱好者（蛇、蜥蜴、守宫、龟等）
- **适配平台**：PC端 + 移动端（H5响应式）

### 1.2 核心功能矩阵
| 模块 | 功能点 | 优先级 |
|------|--------|--------|
| 宠物档案 | 基础信息、品种基因、体重体长、蜕皮记录、产蛋记录 | P0 |
| 成长追踪 | 体重曲线图、体长曲线图、对比分析 | P0 |
| 成长相册 | 照片上传、时间线展示、相册管理 | P1 |
| 智能喂食 | 喂食量计算、喂食周期、补钙周期 | P0 |
| 养护计划 | 日历提醒（喂食/泡澡/温控）、月度统计 | P0 |
| 账号系统 | 注册/登录/找回密码、多用户数据隔离 | P0 |

---

## 2. 技术方案

### 2.1 技术栈选择

| 层级 | 技术选型 | 理由 |
|------|----------|------|
| **前端框架** | Vue 3 + Vite | 渐进式框架，上手快，生态成熟 |
| **移动端适配** | Tailwind CSS | 原子化CSS，快速响应式开发 |
| **图表库** | ECharts | 功能强大，支持多种图表，Vue友好 |
| **状态管理** | Pinia | Vue官方推荐，轻量且支持持久化 |
| **路由** | Vue Router 4 | Vue官方路由 |
| **后端框架** | FastAPI | 现代化Python异步框架，高性能 |
| **数据库** | SQLite（开发）/ PostgreSQL（生产） | 开发简洁，生产可扩展 |
| **ORM** | SQLAlchemy + Alembic | 成熟稳定，支持迁移 |
| **认证** | JWT + 邮箱验证 | 无状态认证，支持刷新令牌 |
| **邮件** | SMTP（可配置） | 发送验证/重置邮件 |

> **架构说明**：前后端分离架构，JWT无状态认证，支持水平扩展。前端纯静态部署，后端负责业务逻辑和数据存储。

### 2.2 项目结构

```
reptile-care/
├── frontend/                    # Vue前端项目
│   ├── src/
│   │   ├── components/         # 公共组件
│   │   │   ├── common/        # Button、Input、Card等
│   │   │   ├── charts/        # ECharts图表组件
│   │   │   └── layout/        # 布局组件
│   │   ├── views/             # 页面
│   │   │   ├── auth/          # 登录/注册
│   │   │   ├── home/          # 首页/仪表盘
│   │   │   ├── pets/          # 宠物相关
│   │   │   ├── growth/        # 成长记录
│   │   │   ├── feeding/       # 喂食管理
│   │   │   └── calendar/      # 日历
│   │   ├── stores/            # Pinia状态
│   │   ├── api/               # API请求封装
│   │   ├── router/            # 路由配置
│   │   └── utils/             # 工具函数
│   └── package.json
│
├── backend/                    # Python后端项目
│   ├── app/
│   │   ├── api/               # API路由
│   │   │   ├── auth.py        # 认证接口
│   │   │   ├── pets.py        # 宠物接口
│   │   │   ├── growth.py      # 成长记录接口
│   │   │   ├── feeding.py     # 喂食接口
│   │   │   └── reminder.py    # 提醒接口
│   │   ├── models/            # SQLAlchemy模型
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # 业务逻辑
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 应用配置
│   │   │   ├── security.py    # JWT/密码加密
│   │   │   └── database.py    # 数据库连接
│   │   └── main.py            # FastAPI入口
│   ├── alembic/               # 数据库迁移
│   ├── requirements.txt
│   └── alembic.ini
│
└── docker-compose.yml          # 本地开发部署
```

### 2.3 数据模型（ER图核心）

```
User (用户)
├── id, email, password_hash, nickname
├── is_verified, verification_token
└── created_at, updated_at
    │
    └── Pet (宠物) [1:N]
        ├── id, user_id, name, species, morph
        ├── birth_date, gender, feeding_cycle
        └── created_at, updated_at
            │
            ├── GrowthRecord (成长记录) [1:N]
            ├── Photo (照片) [1:N]
            ├── ShedRecord (蜕皮记录) [1:N]
            ├── EggRecord (产蛋记录) [1:N]
            ├── FeedingRecord (喂食记录) [1:N]
            └── Reminder (提醒) [1:N]
```

---

## 3. 功能模块详解

### 3.1 账号系统模块 (P0)

#### 注册流程
```
用户注册 → 发送验证邮件 → 点击链接验证 → 账号激活
```

#### 登录流程
```
登录请求 → 验证账号密码 → 生成JWT + RefreshToken → 返回令牌
```

#### 接口设计
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 注册（发送验证邮件） |
| `/api/auth/verify/{token}` | GET | 邮箱验证激活 |
| `/api/auth/login` | POST | 登录 |
| `/api/auth/refresh` | POST | 刷新令牌 |
| `/api/auth/forgot-password` | POST | 忘记密码（发送重置邮件） |
| `/api/auth/reset-password` | POST | 重置密码 |
| `/api/auth/me` | GET | 获取当前用户信息 |

#### 数据安全
- 密码：bcrypt哈希加密
- 令牌：JWT AccessToken(15min) + RefreshToken(7days)
- 敏感操作需携带AccessToken

---

### 3.2 宠物档案模块 (P0)

#### 数据模型
```python
class Pet(Base):
    id: UUID
    user_id: UUID              # 关联用户，数据隔离
    name: str                  # 宠物名称
    species: str               # 品种：玉米蛇、王蛇、豹纹守宫等
    morph: str                 # 基因表型：原色、白化、超级等
    birth_date: date           # 出生/入手日期
    gender: GenderEnum         # male/female
    weight: float              # 当前体重(g)
    length: float              # 当前体长(cm)
    feeding_cycle: int         # 喂食周期(天)
    last_feeding_date: date    # 上次喂食日期
    avatar_url: str            # 头像URL
    created_at: datetime
    updated_at: datetime
```

#### 功能点
- 新建/编辑/删除宠物档案
- 品种快速选择（预设品种库）
- 基因标签管理（支持多选）
- 基础信息编辑
- **数据隔离**：用户只能访问自己的宠物

---

### 3.3 成长记录模块 (P0)

#### 数据模型
```python
class GrowthRecord(Base):
    id: UUID
    pet_id: UUID
    date: date
    weight: float              # 体重(g)
    length: float              # 体长(cm)
    note: str
```

#### 功能点
- 新增/编辑/删除成长记录
- **体重变化曲线图**：折线图 + 趋势线
- **体长变化曲线图**：同上
- 关键节点标记（蜕皮、产蛋后）
- 数据导出CSV

---

### 3.4 蜕皮/产蛋记录 (P0)

#### 蜕皮记录
```python
class ShedRecord(Base):
    id: UUID
    pet_id: UUID
    date: date
    quality: ShedQualityEnum   # good/incomplete/stuck
    note: str
```

#### 产蛋记录
```python
class EggRecord(Base):
    id: UUID
    pet_id: UUID
    lay_date: date
    egg_count: int
    fertile: bool
    incubate_date: date
    hatch_date: date
    hatch_count: int
    note: str
```

---

### 3.5 成长相册模块 (P1)

#### 数据模型
```python
class Photo(Base):
    id: UUID
    pet_id: UUID
    url: str                    # OSS URL或本地路径
    thumbnail_url: str          # 缩略图
    date: date
    tag: PhotoTagEnum           # growth/shed/feeding/other
    note: str
```

#### 功能点
- 照片上传（支持拍照）
- 时间线展示（瀑布流）
- 按标签筛选
- 照片备注

---

### 3.6 智能喂食计算 (P0)

#### 核心算法
```python
# 喂食量计算公式
FEEDING_RATIOS = {
    '玉米蛇': 0.15,      # 喂食量 = 体重 × 比例
    '王蛇': 0.15,
    '球蟒': 0.12,
    '豹纹守宫': 0.10,
    '睫角守宫': 0.08,
    '鬃狮蜥': 0.05,
    '绿鬣蜥': 0.03,
    '龟类': 0.02
}

def calculate_feeding_amount(species: str, weight: float) -> float:
    ratio = FEEDING_RATIOS.get(species, 0.10)
    return round(weight * ratio, 1)

# 喂食周期计算
def calculate_feeding_cycle(weight: float) -> int:
    if weight < 100:    return 5   # 幼体
    elif weight < 500:  return 7   # 亚成
    else:               return 14  # 成体

# 补钙周期
def calculate_calcium_cycle(has_uvb: bool) -> int:
    return 14 if has_uvb else 7
```

#### 功能点
- 自动计算建议喂食量
- 自动计算下次喂食日期
- 补钙周期提醒
- 维生素周期提醒
- 泡澡周期（适用于蛇类、守宫）

---

### 3.7 喂食记录模块 (P0)

```python
class FeedingRecord(Base):
    id: UUID
    pet_id: UUID
    date: date
    food_type: str             # 饲料类型：小鼠/蟋蟀/杜比亚等
    food_weight: float         # 饲料重量(g)
    is_success: bool          # 是否成功
    refused: bool              # 是否拒食
    note: str
```

#### 功能点
- 记录每次喂食详情
- 标记拒食情况
- 喂食历史查询
- 拒食统计

---

### 3.8 日历提醒模块 (P0)

```python
class Reminder(Base):
    id: UUID
    pet_id: UUID
    type: ReminderTypeEnum     # feeding/bathing/calcium/vitamin/temperature/cleaning
    title: str
    description: str
    due_date: datetime
    repeat_type: RepeatEnum    # once/daily/weekly/biweekly/monthly
    is_completed: bool
    completed_at: datetime
```

#### 功能点
- 月历视图展示待办
- 今日任务卡片
- 快速标记完成
- 重复任务自动生成
- 逾期任务高亮
- **系统自动生成**：根据喂食周期自动创建提醒

---

### 3.9 月度统计模块 (P0)

#### 功能点
- 喂食次数统计
- 喂食量统计（克）
- 蜕皮次数统计
- 产蛋统计（如有）
- 体重变化汇总
- 月度数据导出CSV

---

## 4. API设计

### 4.1 认证相关
| 接口 | 方法 | 描述 |
|------|------|------|
| `POST /api/auth/register` | 注册 | 发送验证邮件 |
| `GET /api/auth/verify/{token}` | 验证 | 激活账号 |
| `POST /api/auth/login` | 登录 | 返回JWT |
| `POST /api/auth/refresh` | 刷新 | 刷新Token |
| `POST /api/auth/forgot-password` | 忘记密码 | 发送重置邮件 |
| `POST /api/auth/reset-password` | 重置密码 | 新密码 |
| `GET /api/auth/me` | 当前用户 | 获取用户信息 |

### 4.2 宠物相关
| 接口 | 方法 | 描述 |
|------|------|------|
| `GET /api/pets` | 列表 | 获取用户所有宠物 |
| `POST /api/pets` | 创建 | 新建宠物 |
| `GET /api/pets/{id}` | 详情 | 获取宠物详情 |
| `PUT /api/pets/{id}` | 更新 | 更新宠物 |
| `DELETE /api/pets/{id}` | 删除 | 删除宠物 |

### 4.3 成长记录
| 接口 | 方法 | 描述 |
|------|------|------|
| `GET /api/pets/{id}/growth` | 列表 | 成长记录 |
| `POST /api/pets/{id}/growth` | 创建 | 添加记录 |
| `PUT /api/pets/{id}/growth/{rid}` | 更新 | 编辑记录 |
| `DELETE /api/pets/{id}/growth/{rid}` | 删除 | 删除记录 |

### 4.4 喂食相关
| 接口 | 方法 | 描述 |
|------|------|------|
| `GET /api/pets/{id}/feeding` | 列表 | 喂食记录 |
| `POST /api/pets/{id}/feeding` | 创建 | 记录喂食 |
| `GET /api/pets/{id}/feeding/calculate` | 计算 | 获取喂食建议 |

### 4.5 提醒相关
| 接口 | 方法 | 描述 |
|------|------|------|
| `GET /api/reminders` | 列表 | 所有提醒 |
| `GET /api/reminders/today` | 今日 | 今日待办 |
| `POST /api/reminders` | 创建 | 创建提醒 |
| `PUT /api/reminders/{id}/complete` | 完成 | 标记完成 |

---

## 5. 响应式设计方案

### 5.1 断点策略
| 断点 | 宽度 | 布局 |
|------|------|------|
| Mobile | < 640px | 单列，卡片式，底部导航 |
| Tablet | 640-1024px | 双列，表格 |
| Desktop | > 1024px | 多列，侧边导航 |

### 5.2 移动端优先设计
- 触控友好的按钮尺寸（≥ 44px）
- 底部导航栏（移动端）
- 侧边导航栏（PC端）
- 图表支持手势缩放

---

## 6. 页面路由

| 路径 | 页面 | 说明 |
|------|------|------|
| `/auth/login` | 登录 | 登录页 |
| `/auth/register` | 注册 | 注册页 |
| `/auth/forgot-password` | 忘记密码 | 找回密码 |
| `/` | 仪表盘 | 今日待办、宠物卡片、快速记录 |
| `/pets` | 宠物列表 | 所有宠物卡片 |
| `/pets/:id` | 宠物详情 | 基础信息、快捷操作 |
| `/pets/:id/growth` | 成长记录 | 曲线图、记录列表 |
| `/pets/:id/photos` | 成长相册 | 照片时间线 |
| `/pets/:id/feeding` | 喂食计划 | 喂食记录、计算器 |
| `/pets/:id/shed` | 蜕皮记录 | 蜕皮历史 |
| `/pets/:id/eggs` | 产蛋记录 | 产蛋历史（仅雌性） |
| `/calendar` | 日历 | 所有待办日历视图 |
| `/stats` | 统计 | 月度数据汇总 |

---

## 7. 开发阶段划分

### Phase 1：基础框架 + 账号系统
- [ ] 项目初始化（Vue + FastAPI）
- [ ] 账号系统（注册/登录/JWT）
- [ ] 数据库模型 + 迁移
- [ ] 布局组件（导航、响应式容器）

### Phase 2：核心功能
- [ ] 宠物档案CRUD
- [ ] 成长记录CRUD + 体重曲线图
- [ ] 智能喂食计算
- [ ] 提醒日历
- [ ] 今日待办面板

### Phase 3：增强功能
- [ ] 蜕皮/产蛋记录
- [ ] 成长相册（照片上传）
- [ ] 月度统计
- [ ] 数据导出CSV

### Phase 4：优化完善
- [ ] 邮件服务集成
- [ ] 照片OSS存储
- [ ] 性能优化
- [ ] 错误处理完善

---

## 8. 环境配置

### 开发环境
```bash
# 前端
cd frontend
npm install
npm run dev  # localhost:5173

# 后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # localhost:8000
```

### 生产环境
```yaml
# docker-compose.yml
services:
  frontend:
    image: nginx
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
    ports:
      - "80:80"

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/reptilecare
    depends_on:
      - db

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

---

## 9. 技术风险与应对

| 风险 | 应对方案 |
|------|----------|
| 图片存储占用大量空间 | OSS存储 + 压缩 + 限制分辨率 |
| 邮件发送失败 | 队列重试 + 页面引导重发 |
| JWT泄露 | 短期AccessToken + RefreshToken轮换 |
| 并发数据冲突 | 乐观锁/版本号控制 |

---

## 10. 后续扩展方向

- [ ] 数据同步（多设备登录）
- [ ] 家庭共享（多宠物管理员）
- [ ] 社区功能（晒宠、求鉴定）
- [ ] AI品种识别
- [ ] 健康异常预警
