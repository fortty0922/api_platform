# System Specification: Backend Automation & Third-Party API Integration Exercise

## 🤖 Role & Context
You are an expert backend engineering instructor. You are designing a backend development assignment for students who have just learned a Web Framework (e.g., Express, FastAPI, Spring Boot). 

Instead of building standard HTTP endpoints for clients, students must build an **Automated Background Worker / Data Synchronization System**. They will use their backend application to fetch data from a designated external API, process it, and synchronize it into their local database automatically without any manual trigger (No Postman, No Frontend).

---

## 🏗️ System Architecture & Data Flow

```text
[Your External API] ──(Scheduled HTTPS GET)──> [Student's Backend Worker] ──(Upsert)──> [Student's Local DB]
```

1. **Source (You):** A live, third-party RESTful API emitting data streams (e.g., social media posts, system alerts, weather anomalies).
2. **Processor (Student's Backend):** A head-less background service running a cron scheduler.
3. **Sink (Student's DB):** Local database (SQL/NoSQL) storing the sanitized, transformed data.

---

## 🛠️ Student Learning Objectives (Backend Core Skills)
1. **Inbound to Outbound Shift:** Implementing HTTP Clients (`axios`, `requests`, `fetch`) inside a server environment.
2. **Asynchronous Task Scheduling:** Utilizing Cron Engines (`node-cron`, `APScheduler`) within the web framework lifecycle.
3. **Idempotency & Data Sync (Upsert):** Handling data synchronization without creating duplicate records.
4. **Data Cleansing & Transformation:** Filtering and reshaping third-party JSON objects before persistence.

---

## 📋 API Specifications (Provided by You)

### EndPoint: `GET /external/stream`
* **Authentication:** Requires Header `X-API-KEY: student_secret_2026`
* **Response Payload (JSON):**
```json
{
  "status": "success",
  "timestamp": 1779234567,
  "data": [
    {
      "id": "ext_post_001",
      "author": "TechCrunch",
      "content": "AI Agents are reshaping backend architectures in 2026. [SensitiveDataHidden]",
      "metrics": { "views": 15200, "reports": 2 },
      "category": "tech",
      "flagged": false
    },
    {
      "id": "ext_post_002",
      "author": "TrollUser99",
      "content": "Insert toxic and inappropriate content here.",
      "metrics": { "views": 450, "reports": 25 },
      "category": "general",
      "flagged": true
    }
  ]
}
```

---

## 🎯 Assignment Requirements & Milestones (For Students)

### Milestone 1: The Heartbeat (Cron & Fetch)
* **Task:** Set up a cron job that runs every **1 minute** upon server startup.
* **Validation:** The backend must successfully print the raw JSON payload from `GET /external/stream` to the console.
* **Constraint:** The `X-API-KEY` must be loaded strictly from an environment variable (`.env`). Hardcoding is an automatic failure.

### Milestone 2: Data Cleansing & ETL Pipeline
Before saving to the local database, the student's backend must process the array:
* **Filter out toxic content:** Skip any item where `flagged: true` or `metrics.reports > 10`.
* **Data Masking:** Replace any bracketed metadata (e.g., `[SensitiveDataHidden]`) with `[REDACTED]`.
* **Schema Transformation:** Flatten the object structure to match their local DB schema.

### Milestone 3: Intelligent Upsert (Idempotency)
* **Task:** Save the processed items to their local database.
* **Logic:**
    * If `id` (e.g., `ext_post_001`) does **not** exist in their DB, perform an `INSERT`.
    * If `id` already exists, compare timestamps/views and perform an `UPDATE` (Do not create duplicate rows).

---

## 🛑 Rigid Constraints for Evaluation
* **No Inbound Routes:** Students should not expose public HTTP routes (like `GET /sync`) to trigger this behavior. It must be 100% automated via background threads/loops.
* **Error Boundaries:** If Your API returns a `500 Internal Server Error` or times out, the student's backend must catch the error (`try-catch`), log it gracefully, and **must not crash** the server.
