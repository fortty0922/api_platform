# 🖥️ Server Guide — 伺服器端操作指南

本文件說明如何**部署、啟動、監控**此 Django 後端平台，包含背景同步系統與使用者 REST API。

---

## 🛠️ 環境需求

| 項目 | 需求 |
|---|---|
| Python | 3.11+ |
| Python 環境 | `venv` 或 `conda` 皆可 |
| 作業系統 | macOS / Linux / Windows |

---

## 1️⃣ 安裝與初始化

### Step 1：建立並啟用虛擬環境

本專案支援任意 Python 虛擬環境，您可以選擇使用 `venv` 或 `conda`。

**選項 A：使用原生的 `venv`（推薦）**
```bash
# 建立虛擬環境
python -m venv venv

# macOS / Linux 啟用環境:
source venv/bin/activate

# Windows 啟用環境:
venv\Scripts\activate
```

**選項 B：使用 Conda**
```bash
conda create -n stream python=3.11
conda activate stream
```

啟用環境後，安裝所有必要套件：

```bash
pip install -r requirements.txt
```

---

### Step 2：設定 `.env` 環境變數

在 `api_platform/api_platform/`（`manage.py` 同層）建立 `.env`：

```bash
cd api_platform/api_platform

cat > .env << 'EOF'
# 外部資料 API 的認證金鑰
EXTERNAL_API_KEY=student_secret_2026

# 外部 API 的完整 URL（本地測試用 mock）
EXTERNAL_API_URL=http://127.0.0.1:8000/external/stream
EOF
```

> ⚠️ `.env` 不應提交至 Git。請確認 `.gitignore` 已包含：
> ```
> .env
> *.sqlite3
> media/
> ```

---

### Step 3：初始化資料庫

```bash
cd api_platform/api_platform
python manage.py migrate
```

成功輸出應包含：

```
Applying posts.0001_initial... OK
Applying sync_worker.0001_initial... OK
```

---

## 2️⃣ 啟動伺服器

我們提供了一個自動化啟動腳本，它會自動檢查資料庫更新並以正確的參數啟動 Daphne 伺服器與排程器。

**👉 macOS / Linux：**
```bash
chmod +x start_server.sh
./start_server.sh
```

**👉 Windows：**
雙擊 `start_server.bat` 檔案，或在命令提示字元執行：
```cmd
start_server.bat
```

這等同於手動進入 `api_platform/` 後執行：
```bash
daphne -b 127.0.0.1 -p 8000 api_platform.asgi:application
```

> **⚠️ 注意事項：**
> 如果您手動用 `runserver` 啟動，請務必加上 `--noreload`。
> 預設的 `runserver` 會啟動 file watcher 子行程，導致 APScheduler 被初始化兩次，造成背景任務重複執行。`--noreload` 或直接使用 `daphne` 則不會有此問題。

同時在 `settings.py` 的 `ALLOWED_HOSTS` 加入對應 IP：

```python
ALLOWED_HOSTS = ['192.168.1.xxx', 'localhost', '127.0.0.1']
```

---

## 3️⃣ 確認系統運作

### 確認背景排程

伺服器啟動後，console 應出現：

```
[11:00:00] INFO sync_worker.scheduler: ⏱️  [SCHEDULER] Started — sync job will run every 1 minute.
[11:01:00] INFO sync_worker.tasks: ⏰ [SYNC] Starting sync job at 2026-05-19T11:01:00
[11:01:00] INFO sync_worker.tasks: ✅ [FETCH] status=success  records=3
[11:01:00] INFO sync_worker.tasks: 🚫 [FILTER] Skipping flagged item id=ext_post_002
[11:01:00] INFO sync_worker.tasks: 💾 [UPSERT] UPDATE id=ext_post_001
[11:01:00] INFO sync_worker.tasks: ✅ [SYNC] Job completed successfully.
```

### 確認使用者 API

```bash
# 註冊
curl -s -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Pass1234"}'
# 預期：{"uid": 1, "username": "testuser"}

# 發文
curl -s -X POST http://127.0.0.1:8000/api/posts/ \
  -H "X-UID: 1" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content":"Hello"}'
# 預期：{"id": 1, "title": "Test", ...}

# 列出貼文
curl -s "http://127.0.0.1:8000/api/posts/?page=1&page_size=5"
# 預期：{"count": 1, "next": null, "previous": null, "results": [...]}
```

---

## 4️⃣ 查看資料庫

### Django Shell

```bash
python manage.py shell
```

```python
# 查看已同步的外部文章
from sync_worker.models import ExternalPost
ExternalPost.objects.values('ext_id', 'author', 'views', 'synced_at')

# 查看使用者發的貼文
from posts.models import Post
for p in Post.objects.select_related('author'):
    print(p.id, p.author.username, p.title, p.image.name if p.image else 'no image')

# 查看所有使用者
from django.contrib.auth.models import User
User.objects.values('id', 'username', 'date_joined')
```

### Django Admin 介面

1. 建立 superuser（第一次）：
   ```bash
   python manage.py createsuperuser
   ```
2. 開啟瀏覽器：[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
3. 可管理：**Users**、**Posts**、**External Posts**

---

## 5️⃣ 手動觸發同步（Debug 用）

```bash
python manage.py shell -c "
from sync_worker.tasks import sync_external_posts
sync_external_posts()
"
```

---

## 6️⃣ 圖片上傳設定

上傳的圖片存放於 `api_platform/media/posts/`。開發環境下由 Django 自動提供靜態服務（`DEBUG=True` 時）。

查看已上傳圖片：

```bash
ls api_platform/media/posts/
```

存取圖片 URL 格式：

```
http://127.0.0.1:8000/media/posts/<filename>
```

---

## 7️⃣ 認證機制說明

本系統使用自訂的 **UID 認證**（`core/authentication.py`）：

- 客戶端在 Request Header 帶入 `X-UID: <uid>`
- Server 用此 uid 查詢 `auth_user` 資料表
- 找到對應使用者 → 認證通過（`request.user` 被設定）
- uid 不存在 → `401 Unauthorized`
- 未帶 Header → 匿名請求（公開端點可通過）

| 端點 | 認證需求 |
|---|---|
| `POST /api/auth/register/` | 不需要 |
| `GET /api/posts/` | 不需要 |
| `POST /api/posts/` | 需要 `X-UID` |
| `DELETE /api/posts/<id>/` | 需要 `X-UID`，且必須是貼文作者 |
| `GET /external/stream` | 需要 `X-API-KEY`（不同機制） |

---

## 8️⃣ Log 等級說明

| Log 等級 | 觸發情況 |
|---|---|
| `DEBUG` | 完整的 API raw response payload |
| `INFO` | 每次 fetch/filter/upsert 操作，API 請求/回應 |
| `ERROR` | 連線失敗、HTTP 錯誤、逾時 |

調整 `sync_worker` log 等級（`settings.py`）：

```python
'loggers': {
    'sync_worker': {
        'level': 'INFO',   # 改為 DEBUG 可看完整 payload
    },
}
```

---

## 9️⃣ 排程設定調整

排程設定於 `sync_worker/scheduler.py`：

```python
scheduler.add_job(
    sync_external_posts,
    trigger=IntervalTrigger(minutes=1),  # ← 修改此處
    max_instances=1,  # 防止執行時間超過間隔時重疊
)
```

| 需求 | 寫法 |
|---|---|
| 每 30 秒 | `IntervalTrigger(seconds=30)` |
| 每 5 分鐘 | `IntervalTrigger(minutes=5)` |
| 每天凌晨 3 點 | `CronTrigger(hour=3, minute=0)` |

---

## 🔒 安全注意事項

1. `.env` 不提交版控
2. 生產環境設定 `DEBUG = False`
3. `SECRET_KEY` 使用強隨機值
4. `ALLOWED_HOSTS` 明確列出 hosts，不使用 `'*'`
5. 圖片上傳建議加大小與格式驗證（目前無限制）
