# 🤖 API Platform — Backend Automation & Social Posts System

> 一個以 Django 實作的雙功能後端平台：**自動化資料同步背景服務** + **使用者發文 REST API**。

---

## 📖 專案簡介

本專案包含兩個獨立的子系統：

### 🔄 子系統一：自動化背景同步（Headless Worker）
每分鐘自動從外部 API 拉取資料、ETL 清洗後 Upsert 至本地資料庫，全程無需人工觸發。

### 📝 子系統二：使用者發文 API
提供使用者**註冊、發文（含圖片）、刪除貼文**的 REST API，以自訂 UID 認證機制保護私有端點。

---

## 🏗️ 系統架構

```text
┌─────────────────────────────────────────────────────────┐
│                   Django Backend                         │
│                                                          │
│  ┌────────────────────┐   ┌───────────────────────────┐ │
│  │  Background Worker │   │  REST API (DRF)           │ │
│  │  (APScheduler)     │   │                           │ │
│  │  每分鐘自動執行     │   │  POST /api/auth/register/ │ │
│  │                    │   │  GET  /api/posts/         │ │
│  │  Fetch → Filter    │   │  POST /api/posts/         │ │
│  │  → Mask → Flatten  │   │  DELETE /api/posts/<id>/  │ │
│  │  → Upsert          │   │                           │ │
│  └────────┬───────────┘   └──────────────┬────────────┘ │
│           │                              │               │
│  ┌────────▼──────────────────────────────▼────────────┐  │
│  │              SQLite Database (db.sqlite3)           │  │
│  │   sync_worker_externalpost  │  posts_post           │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 專案結構

```
api_platform/                        ← 專案根目錄
├── README.md                        ← 本文件
├── SERVER_GUIDE.md                  ← 伺服器端操作指南
├── CLIENT_GUIDE.md                  ← 客戶端 API 串接指南
├── backend_automation_spec-v2.md    ← 原始需求規格
│
└── api_platform/                    ← Django 專案目錄
    ├── manage.py
    ├── db.sqlite3                   ← SQLite 資料庫
    ├── .env                         ← 環境變數（不提交 Git）
    ├── media/                       ← 使用者上傳圖片
    │
    ├── api_platform/                ← Django 設定模組
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    │
    ├── core/                        ← 共用工具
    │   └── authentication.py        ← 自訂 UID 認證
    │
    ├── users/                       ← 使用者系統
    │   ├── serializers.py
    │   ├── views.py                 ← RegisterView
    │   └── urls.py
    │
    ├── posts/                       ← 貼文系統
    │   ├── models.py                ← Post model
    │   ├── serializers.py
    │   ├── views.py                 ← List / Create / Delete
    │   └── urls.py
    │
    ├── sync_worker/                 ← 背景同步 App
    │   ├── apps.py
    │   ├── models.py                ← ExternalPost model
    │   ├── tasks.py                 ← ETL pipeline
    │   └── scheduler.py            ← APScheduler
    │
    └── mock_api/                    ← 本地模擬外部 API
        └── views.py                 ← GET /external/stream
```

---

## 🔌 完整 API 清單

| Method | URL | 說明 | 認證 |
|---|---|---|---|
| `POST` | `/api/auth/register/` | 註冊，回傳 `uid` | 不需要 |
| `GET` | `/api/posts/` | 取得貼文列表（支援分頁） | 不需要 |
| `POST` | `/api/posts/` | 發新貼文 | `X-UID` Header |
| `DELETE` | `/api/posts/<id>/` | 刪除自己的貼文 | `X-UID` Header |
| `GET` | `/external/stream` | 模擬外部資料源 | `X-API-KEY` Header |
| `GET` | `/api/help/` | 查詢可用 API 清單 | 不需要 |
| `*` | `/admin/` | Django 後台管理 | Django 帳密 |

---

## 📦 技術棧

| 類別 | 套件 |
|---|---|
| Web Framework | Django 5.0.7 |
| ASGI Server | Daphne 4.x |
| REST API | Django REST Framework 3.17 |
| 圖片處理 | Pillow 11.x |
| 排程引擎 | APScheduler 3.x |
| HTTP Client | requests 2.x |
| 環境變數 | python-dotenv 1.x |
| 資料庫 | SQLite |
| Python 環境 | `venv` 或 `conda` 皆可 |

---

## ⚡ 快速啟動

```bash
# 選擇 A：使用 venv
python -m venv venv
source venv/bin/activate    # Windows 請使用 venv\Scripts\activate

# 選擇 B：使用 Conda
# conda create -n stream python=3.11
# conda activate stream

# 安裝套件
pip install -r requirements.txt
```

**啟動伺服器 (macOS / Linux)：**
```bash
chmod +x start_server.sh
./start_server.sh
```

**啟動伺服器 (Windows)：**
雙擊 `start_server.bat` 或在命令提示字元執行：
```cmd
start_server.bat
```

**驗證系統運作：**

```bash
# 1. 註冊
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"Pass1234"}'
# → {"uid": 1, "username": "alice"}

# 2. 發文
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "X-UID: 1" \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello","content":"My first post!"}'

# 3. 看貼文列表
curl "http://127.0.0.1:8000/api/posts/?page=1&page_size=5"
```

---

## 📋 相關文件

- **[SERVER_GUIDE.md](./SERVER_GUIDE.md)** — 部署、啟動、監控、排程調整
- **[CLIENT_GUIDE.md](./CLIENT_GUIDE.md)** — API 規格、認證方式、程式碼範例
