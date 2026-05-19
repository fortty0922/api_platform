# 📡 Client Guide — 客戶端 API 串接指南

本文件說明如何串接此後端 API，包含使用者系統與貼文功能的完整規格、範例程式碼與除錯指南。

---

## 📋 API 總覽

| Method | URL | 說明 | 認證 |
|---|---|---|---|
| `GET` | `/api/help/` | 取得即時動態 API 規格書 | 不需要 |
| `POST` | `/api/auth/register/` | 註冊帳號，取得 uid | 不需要 |
| `POST` | `/api/auth/login/` | 登入帳號，取得 uid | 不需要 |
| `GET` | `/api/posts/` | 取得貼文列表（支援分頁、搜尋、排序） | 不需要 |
| `GET` | `/api/posts/<id>/` | 取得單一貼文詳細資料 | 不需要 |
| `POST` | `/api/posts/` | 發布新貼文（支援圖片） | `X-UID` Header |
| `PUT` | `/api/operations/posts/<id>/put/` | 完整替換自己的貼文 | `X-UID` Header |
| `PATCH` | `/api/operations/posts/<id>/patch/` | 部分修改自己的貼文 | `X-UID` Header |
| `DELETE` | `/api/operations/posts/<id>/delete/` | 刪除自己的貼文 | `X-UID` Header |

> **Base URL（本地開發）**：`http://127.0.0.1:8000`

---

## 🔑 認證機制：X-UID Header

本系統使用自訂的 **UID 認證**，不使用 JWT 或 Session。

流程：
1. 呼叫 `/api/auth/register/` 取得你的 `uid`
2. 之後所有需要認證的 API，在 Request Header 帶入 `X-UID: <你的uid>`

```
X-UID: 3
```

- 沒帶 Header → 公開端點（GET /api/posts/）可正常存取，私有端點回傳 `401`
- uid 不存在 → `401 Unauthorized`
- 刪除不屬於自己的貼文 → `403 Forbidden`

---

## 0️⃣ GET `/api/help/` — 動態 API 規格書

### 說明

取得目前系統上所有可用的 API 路由、HTTP Method 與所需的參數格式。這支 API 會自動反映系統的最新狀態，是開發串接時最好的參考文件。

### Request

不需要帶任何 Header 或參數。

### Code Example

#### 範例：Mac / Linux (curl)
```bash
curl -s http://127.0.0.1:8000/api/help/ | python3 -m json.tool
```

#### 範例：Windows (PowerShell)
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/help/
```

#### Python (requests)
```python
import requests

url = "http://127.0.0.1:8000/api/help/"
response = requests.get(url)
print(response.json())
```

---

## 1️⃣ POST `/api/auth/register/` — 註冊

### 說明

建立新帳號。只需要 `username` 和 `password`，成功後回傳你的 `uid`，**請務必記住 uid**，後續所有操作都需要它。

### Request

```
Content-Type: application/json
```

```json
{
  "username": "alice",
  "password": "Pass1234"
}
```

**欄位說明：**
- `username`：使用者名稱，不可重複
- `password`：密碼，最少 6 個字元

### Response `201 Created`

```json
{
  "uid": 3,
  "username": "alice"
}
```

### Response `400 Bad Request`（帳號已存在）

```json
{
  "username": ["A user with that username already exists."]
}
```

### 範例：Mac / Linux (curl)

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"Pass1234"}'
```

### 範例：Windows (PowerShell)

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/auth/register/ `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"username":"alice","password":"Pass1234"}'
```

### 範例：Python

```python
import requests

resp = requests.post(
    "http://127.0.0.1:8000/api/auth/register/",
    json={"username": "alice", "password": "Pass1234"},
)

if resp.status_code == 201:
    data = resp.json()
    uid = data["uid"]
    print(f"✅ 註冊成功！你的 UID = {uid}，請記住它！")
else:
    print(f"❌ 註冊失敗：{resp.json()}")
```

---

## 2️⃣ POST `/api/auth/login/` — 登入

### 說明

如果你已經註冊過，可以透過這隻 API 輸入帳號密碼來找回你的 `uid`。這也是前端介面用來實現「登入」狀態的端點。

### Request

不用帶 Header。請在 Body 傳入 JSON：

```json
{
  "username": "alice",
  "password": "Pass1234"
}
```

### Response

- **200 OK**：驗證成功
  ```json
  {
    "uid": 3,
    "username": "alice"
  }
  ```
- **400 Bad Request**：沒帶帳號或密碼。
- **401 Unauthorized**：帳號或密碼錯誤。

### Code Example

#### 範例：Mac / Linux (curl)
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"Pass1234"}'
```

#### 範例：Windows (PowerShell)
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/auth/login/ `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"username":"alice","password":"Pass1234"}'
```

### 範例：Python

```python
import requests

resp = requests.post(
    "http://127.0.0.1:8000/api/auth/login/",
    json={"username": "alice", "password": "Pass1234"},
)

if resp.status_code == 200:
    data = resp.json()
    print(f"✅ 登入成功！歡迎回來，你的 UID = {data['uid']}")
else:
    print("❌ 登入失敗：帳號或密碼錯誤！")
```

---

## 3️⃣ GET `/api/posts/` — 取得貼文列表

### 說明

取得所有貼文，按建立時間**由新到舊**排序。支援分頁，不需要認證。

### 分頁參數

| 參數 | 說明 | 預設值 | 最大值 |
|---|---|---|---|
| `page` | 頁碼（從 1 開始） | 1 | 無限制 |
| `page_size` | 每頁筆數 | 10 | 100 |
| `search` | 關鍵字搜尋（比對標題與內容） | - | - |
| `ordering` | 排序方式（例如 `title`, `-created_at`） | `-created_at` | - |
| `author_id` | 過濾特定作者的貼文 | - | - |

### Request

```
GET /api/posts/?page=1&page_size=5
```

### Response `200 OK`

```json
{
  "count": 42,
  "next": "http://127.0.0.1:8000/api/posts/?page=2&page_size=5",
  "previous": null,
  "results": [
    {
      "id": 10,
      "title": "My Latest Post",
      "content": "Content here...",
      "image_url": "http://127.0.0.1:8000/media/posts/photo.jpg",
      "author": 3,
      "author_username": "alice",
      "created_at": "2026-05-19T11:00:00Z",
      "updated_at": "2026-05-19T11:00:00Z"
    }
  ]
}
```

**欄位說明：**

| 欄位 | 說明 |
|---|---|
| `count` | 資料庫中的總貼文數 |
| `next` | 下一頁的完整 URL，最後一頁為 `null` |
| `previous` | 上一頁的完整 URL，第一頁為 `null` |
| `results` | 本頁的貼文陣列 |
| `image_url` | 圖片的完整 URL，無圖片時為 `null` |

### 範例：Mac / Linux (curl)

```bash
# 第 1 頁，每頁 5 筆
curl "http://127.0.0.1:8000/api/posts/?page=1&page_size=5"

# 第 2 頁，每頁 10 筆（預設）
curl "http://127.0.0.1:8000/api/posts/?page=2"
```

### 範例：Windows (PowerShell)

```powershell
# 第 1 頁，每頁 5 筆
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/posts/?page=1&page_size=5"

# 第 2 頁，每頁 10 筆（預設）
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/posts/?page=2"
```

### 範例：Python（翻頁遍歷所有貼文）

```python
import requests

BASE_URL = "http://127.0.0.1:8000"
url = f"{BASE_URL}/api/posts/?page_size=10"

all_posts = []
page = 1

while url:
    resp = requests.get(url)
    data = resp.json()
    all_posts.extend(data["results"])
    print(f"第 {page} 頁，取得 {len(data['results'])} 筆，共 {data['count']} 筆")
    url = data["next"]  # 最後一頁時 next 為 None，迴圈結束
    page += 1

print(f"\n✅ 共取得 {len(all_posts)} 筆貼文")
```

---

## 3️⃣ POST `/api/posts/` — 發新貼文

### 說明

建立新貼文。**需要** `X-UID` Header。圖片為選填，若要上傳圖片，必須使用 `multipart/form-data` 格式。

### Request（純文字）

```
X-UID: 3
Content-Type: application/json
```

```json
{
  "title": "My Post Title",
  "content": "This is the content of my post."
}
```

### Request（含圖片）

```
X-UID: 3
Content-Type: multipart/form-data
```

```
title=My Post Title
content=This is the content.
image=<file>
```

> ⚠️ 上傳圖片時**必須**使用 `multipart/form-data`，不能用 `application/json`

### Response `201 Created`

```json
{
  "id": 5,
  "title": "My Post Title",
  "content": "This is the content of my post.",
  "image_url": null,
  "author": 3,
  "author_username": "alice",
  "created_at": "2026-05-19T11:30:00Z",
  "updated_at": "2026-05-19T11:30:00Z"
}
```

### Response `401 Unauthorized`（未帶 X-UID）

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 範例：Mac / Linux (curl)（純文字）

```bash
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "X-UID: 3" \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello World","content":"My first post!"}'
```

### 範例：Windows (PowerShell)（純文字）

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/posts/ `
  -Method POST `
  -Headers @{"X-UID"="3"; "Content-Type"="application/json"} `
  -Body '{"title":"Hello World","content":"My first post!"}'
```

### 範例：Mac / Linux (curl)（含圖片）

```bash
curl -X POST http://127.0.0.1:8000/api/posts/ \
  -H "X-UID: 3" \
  -F "title=Photo Post" \
  -F "content=Check out this photo!" \
  -F "image=@/path/to/photo.jpg"
```

### 範例：Windows (PowerShell)（含圖片）

```powershell
# PowerShell 原生上傳 Multipart/form-data 較為繁瑣，在 Windows 建議強制呼叫 curl.exe
curl.exe -X POST http://127.0.0.1:8000/api/posts/ `
  -H "X-UID: 3" `
  -F "title=Photo Post" `
  -F "content=Check out this photo!" `
  -F "image=@/path/to/photo.jpg"
```

### 範例：Python（純文字）

```python
import requests

UID = 3  # 你的 uid（從 register 取得）

resp = requests.post(
    "http://127.0.0.1:8000/api/posts/",
    headers={"X-UID": str(UID)},
    json={
        "title": "Hello World",
        "content": "My first post via Python!",
    },
)

if resp.status_code == 201:
    post = resp.json()
    print(f"✅ 發文成功！貼文 ID = {post['id']}")
else:
    print(f"❌ 發文失敗 {resp.status_code}：{resp.json()}")
```

### 範例：Python（含圖片）

```python
import requests

UID = 3

with open("photo.jpg", "rb") as img:
    resp = requests.post(
        "http://127.0.0.1:8000/api/posts/",
        headers={"X-UID": str(UID)},
        data={
            "title": "Photo Post",
            "content": "Check out this photo!",
        },
        files={"image": ("photo.jpg", img, "image/jpeg")},
    )

if resp.status_code == 201:
    post = resp.json()
    print(f"✅ 發文成功！圖片 URL = {post['image_url']}")
```

---

## 4️⃣ GET `/api/posts/<id>/` — 取得單一貼文

### 說明
取得指定 ID 的貼文詳細資料。不需要認證。

### Request
```
GET /api/posts/5/
```

### Response `200 OK`
與列表回傳的單筆物件格式相同。

---

## 5️⃣ PUT `/api/operations/posts/<id>/put/` — 完整修改貼文

### 說明
完整替換**自己的**貼文內容。**需要** `X-UID` Header，必須提供 `title` 與 `content`。

### Request
```
PUT /api/operations/posts/5/put/
X-UID: 3
Content-Type: application/json

{
  "title": "New Title",
  "content": "Completely new content"
}
```

---

## 6️⃣ PATCH `/api/operations/posts/<id>/patch/` — 部分修改貼文

### 說明
部分修改**自己的**貼文內容。**需要** `X-UID` Header，可選擇性提供要修改的欄位。

### Request
```
PATCH /api/operations/posts/5/patch/
X-UID: 3
Content-Type: application/json

{
  "title": "Updated Title Only"
}
```

---

## 7️⃣ DELETE `/api/operations/posts/<id>/delete/` — 刪除貼文

### 說明

刪除**自己的**貼文。**需要** `X-UID` Header，且只能刪除自己建立的貼文。

### Request

```
DELETE /api/operations/posts/5/delete/
X-UID: 3
```

### Response `204 No Content`（成功）

回應 body 為空。

### Response `403 Forbidden`（不是你的貼文）

```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Response `404 Not Found`（貼文不存在）

```json
{
  "detail": "No Post matches the given query."
}
```

### Response `401 Unauthorized`（未帶 X-UID）

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 範例：Mac / Linux (curl)

```bash
curl -s -o /dev/null -w "HTTP Status: %{http_code}" \
  -X DELETE http://127.0.0.1:8000/api/operations/posts/5/delete/ \
  -H "X-UID: 3"
# HTTP Status: 204
```

### 範例：Windows (PowerShell)

```powershell
try {
    $resp = Invoke-WebRequest -Uri http://127.0.0.1:8000/api/operations/posts/5/delete/ `
      -Method DELETE `
      -Headers @{"X-UID"="3"}
    Write-Host "HTTP Status:" $resp.StatusCode
} catch {
    Write-Host "HTTP Status:" $_.Exception.Response.StatusCode.value__
}
```

### 範例：Python

```python
import requests

UID = 3
POST_ID = 5

resp = requests.delete(
    f"http://127.0.0.1:8000/api/operations/posts/{POST_ID}/delete/",
    headers={"X-UID": str(UID)},
)

if resp.status_code == 204:
    print(f"✅ 貼文 {POST_ID} 已刪除")
elif resp.status_code == 403:
    print(f"❌ 無權限：{resp.json()['detail']}")
elif resp.status_code == 404:
    print(f"❌ 貼文不存在")
else:
    print(f"❌ 錯誤 {resp.status_code}：{resp.json()}")
```

---

## 🔄 完整工作流程範例（Python）

從頭到尾示範所有功能：

```python
import requests

BASE = "http://127.0.0.1:8000"
s = requests.Session()

# ── 1. 註冊 ─────────────────────────────────────────────────────────────────
print("=== 1. 註冊 ===")
resp = s.post(f"{BASE}/api/auth/register/",
              json={"username": "bob", "password": "Pass1234"})

if resp.status_code == 201:
    uid = resp.json()["uid"]
    print(f"✅ 成功，UID = {uid}")
elif resp.status_code == 400:
    print("帳號已存在，用現有帳號繼續...")
    uid = 1  # 替換為你的 uid

# 之後每個請求都帶上 X-UID
s.headers.update({"X-UID": str(uid)})

# ── 2. 發文 ──────────────────────────────────────────────────────────────────
print("\n=== 2. 發文 ===")
resp = s.post(f"{BASE}/api/posts/",
              json={"title": "Hello!", "content": "My first post via Python."})
assert resp.status_code == 201, f"Failed: {resp.text}"
post_id = resp.json()["id"]
print(f"✅ 貼文建立成功，ID = {post_id}")

# ── 3. 查看列表 ───────────────────────────────────────────────────────────────
print("\n=== 3. 取得貼文列表（page_size=3）===")
resp = s.get(f"{BASE}/api/posts/", params={"page": 1, "page_size": 3})
data = resp.json()
print(f"總筆數: {data['count']}，本頁: {len(data['results'])} 筆")
for p in data["results"]:
    print(f"  [{p['id']}] {p['title']} by {p['author_username']}")

# ── 4. 刪除貼文 ───────────────────────────────────────────────────────────────
print(f"\n=== 4. 刪除貼文 ID={post_id} ===")
resp = s.delete(f"{BASE}/api/operations/posts/{post_id}/delete/")
assert resp.status_code == 204, f"Failed: {resp.text}"
print(f"✅ 貼文 {post_id} 已刪除")
```

---

## ❓ 常見問題

### Q1：為什麼我的請求回傳 `401`？

- 確認有帶 `X-UID` Header（不是 `X-Uid` 或 `uid`）
- 確認 uid 是整數且該使用者存在
- 端點是否需要認證（`GET /api/posts/` 不需要）

### Q2：上傳圖片為什麼回傳 `400`？

上傳圖片時**不能**使用 `Content-Type: application/json`，必須是 `multipart/form-data`（curl 用 `-F`，Python 用 `files=` 參數）。

### Q3：`image_url` 是 `null` 但我有傳圖片？

確認 Django 伺服器已設定 `MEDIA_URL` 和 `MEDIA_ROOT`，且 `DEBUG=True`（開發環境下才會自動提供 media 靜態服務）。

### Q4：`403 Forbidden` 是什麼意思？

你嘗試刪除的貼文不是你建立的。每個使用者只能刪除自己的貼文（`author == 你的 uid`）。

### Q5：`next` 是什麼？

分頁回應中的 `next` 是下一頁的**完整 URL**，可以直接 `requests.get(data["next"])` 取下一頁。最後一頁時 `next` 為 `null`。

### Q6：在 PowerShell 打 API，印出來的資料一半變成 `...` 怎麼辦？

這是 PowerShell 預設的顯示限制（當陣列或字串太長時會自動折疊）。
**解法**：在指令最後面加上 `| ConvertTo-Json -Depth 10`，強制把它轉成完整的 JSON 格式印出來：
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/help/ | ConvertTo-Json -Depth 10
```
