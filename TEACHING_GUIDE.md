# 🎓 Teaching Guide — Django 討論版客戶端 (Client) 實戰教學腳本

這份文件是專為**講師或導師**準備的教學腳本。
這堂課的目標是帶領學生從零開始，使用 **Django** 打造一個帶有圖形介面的網頁應用程式 (Web App)，並透過 Python 的 `requests` 套件，在背後偷偷與您的**真實討論版 RESTful API** 進行溝通。

**⚠️ 教學前提**：
- **您（講師）**將啟動本專案 (API Platform)，並把伺服器網址提供給學生。
- **學生**將扮演「前端/客戶端開發者」，他們會在自己的電腦上建立一個全新的 Django 專案，學習如何串接您的 API 並渲染到 HTML 畫面上。

---

## 🗺️ Step-by-Step 教學流程

### Step 1：情境解說與 API 探索 (15 分鐘)
> **教學目標**：讓學生明白 API 是什麼，以及接下來要實作什麼。

1. **情境說明**：告訴學生：「大家今天要來實作一個討論版網站！但我們今天不寫資料庫，資料庫我已經幫大家架好了。我們要學習怎麼寫一個 Django 網站去跟我的伺服器要資料。」
2. **公開 API 資訊**：在白板或投影幕上公布您的 API 資訊：
   - **Base URL**: `http://<講師的IP>:8000`
3. **初探 API (終端機)**：請學生打開終端機，用指令打打看規格書：
   ```bash
   curl -s http://<講師的IP>:8000/api/help/ | python3 -m json.tool
   ```
4. **觀察規格**：告訴學生：「這就像是餐廳的菜單。未來我們寫 Django 時，就是依照這份菜單來送 Request。」

---

### Step 2：註冊與無狀態認證體驗 (20 分鐘)
> **教學目標**：體驗 POST 與無狀態認證，取得關鍵的身分憑證。

1. **任務說明**：要在討論版發言，必須先有帳號，我們現在終端機手動註冊。
2. **引導實作 (POST)**：教他們如何使用 `curl` 的 `-d` 參數，把 `username` 和 `password` 塞在 JSON Payload 裡面送出去：
   ```bash
   curl -X POST http://<講師的IP>:8000/api/auth/register/ \
     -H "Content-Type: application/json" \
     -d '{"username":"student1","password":"password123"}'
   ```
3. **防呆體驗 (400)**：請學生按鍵盤「上方向鍵」故意再發送一次一樣的帳號，觀察 `400 Bad Request`，講解後端防呆。
4. **取得 UID (身分證)**：註冊成功後會得到一組 `uid`。請學生**務必把這串 uid 記在記事本上**，稍後寫 Django 時會用到！

---

### Step 3：開始用 Django 實作 — 讀取並渲染文章 (45 分鐘)
> **教學目標**：學會在 Django View 中使用 `requests` 發送 GET 請求。

1. **初始化 Django**：帶領學生建立一個新的 Django 專案與 App。
2. **撰寫 View**：在學生的 `views.py` 中，教導他們匯入 `import requests`。
3. **實作 GET API**：
   ```python
   # 學生的 views.py 範例
   def post_list(request):
       # 向講師的 API 請求文章列表
       response = requests.get("http://<講師的IP>:8000/api/posts/?page=1&page_size=10")
       data = response.json()
       return render(request, "posts.html", {"posts": data["results"]})
   ```
4. **前端渲染**：帶領學生寫簡單的 `posts.html`，用 `{% for post in posts %}` 把文章標題與內容印在網頁上。
5. **機會教育**：解釋 Query Parameters (`?page=1`) 是怎麼過濾資料的。

---

### Step 4：實作發文功能 (POST) 與 Header (30 分鐘)
> **教學目標**：學會處理 HTML Form，並在 Python 中掛上 HTTP Header。

1. **前端表單**：在 `posts.html` 加上一個發文的 `<form>` (Method="POST")。
2. **撰寫 View (接收與轉發)**：
   - 學生需要在 `views.py` 接收使用者填寫的標題與內容。
   - **踩坑點**：故意讓他們先用 `requests.post()` 送出，結果收到 `401 Unauthorized`。
3. **加上身分證 (Header)**：引導他們把剛剛存在記事本的 UID 拿出來，放到 Header 中：
   ```python
   headers = {"X-UID": "剛剛的UID", "Content-Type": "application/json"}
   payload = {"title": request.POST['title'], "content": request.POST['content']}
   requests.post("http://<講師的IP>:8000/api/posts/", json=payload, headers=headers)
   ```
4. **驗證**：發文成功後重新整理網頁，看到自己的文章出現在畫面上！

---

### Step 5：刪除文章與權限控制 (403 Forbidden) (20 分鐘)
> **教學目標**：利用 `requests.delete` 實作刪除，並體驗資安防護。

1. **前端按鈕**：在自己的文章旁邊加上「刪除」按鈕。
2. **實作 DELETE**：
   ```python
   requests.delete(f"http://<講師的IP>:8000/api/operations/posts/{post_id}/delete/", headers=headers)
   ```
3. **震撼教育 (越權測試)**：
   - 請學生故意把刪除按鈕的 HTML 偷改成「隔壁同學文章的 ID」。
   - 按下刪除後，請學生把 API 回傳的錯誤印在終端機上，他們會看到 `403 Forbidden`。
   - **收尾講解**：藉機向學生釐清最重要的資安觀念 —— 401 是「不知道你是誰」，403 是「知道你是誰，但你沒有權限動別人的東西」。這就是後端 API 的價值！
