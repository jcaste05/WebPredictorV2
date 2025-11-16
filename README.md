# WebPredictorV2

WebPredictorV2 is a small full‑stack project demonstrating a secure machine‑learning inference and training service for tabular regression. It provides:

* A static frontend (HTML/CSS/JavaScript) to login, select a regression model, paste CSV train / predict datasets, and inspect metrics and predictions.
* A FastAPI backend exposing authenticated endpoints for training and inference, plus documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc).
* Token‑based authentication (JWT style) with scope support.
* Security hardening using HTTP security headers and a middleware layer.
* Basic DoS mitigation via request rate limiting backed by Redis.
* Request payload validation and serialization using Pydantic models.
* Two data stores: a SQL database (SQLite by default) for users & auth data, and Redis for rate limit state.

Live (free tier) deployment is available on Render: https://webpredictor-api.onrender.com (see `render.yaml` blueprint). You can also run everything locally with Docker.

---

## Architecture Overview

```
frontend/ (static assets served by FastAPI or a static server)
	index.html, styles/, js/ (dom.js, api.js, auth.js, tabular_regressor.js, config.js)

backend/
	api/ (FastAPI application: main.py, routers/, schemas/, security/, version info)
	models/ (ML model loader & abstractions)
	db/ (SQLAlchemy session, models, init script)
	tests/ (pytest examples)

Data Stores:
	Users DB: SQLite (default) or PostgreSQL (configurable via env var `USERS_DB_URL`)
	Rate limiting store: Redis
```

### Frontend
* Plain HTML/CSS/JS (no framework) for simplicity and transparency.
* Communicates with the backend via `fetch` wrapper in `js/api.js`.
* Shows API / model version obtained from `/health` endpoint.
* Links to interactive API docs `/docs` and `/redoc` added to both header nav and footer.

### Backend (FastAPI)
* Organized by routers: auth, admin, tabular_regressor.
* Pydantic schemas enforce strict validation for training and prediction payloads.
* Security middleware sets headers: `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy`, `Strict-Transport-Security`, plus a Content Security Policy (CSP).
* Rate limiting provided by `fastapi-limiter` + Redis (per IP using a custom identifier).
* Version endpoints: `/health` returns service, API, and model version metadata.

### Machine Learning Layer
* Basic tabular regression models (e.g., linear regression) loaded through abstraction in `backend/models/`.
* Training + prediction performed synchronously (future improvement: offload to task queue).

---

## Security Features

| Feature                | Purpose |
|------------------------|---------|
| Token Authentication   | Restrict access to protected endpoints; scopes refine authorization. |
| Security Headers       | Mitigate common browser attacks (clickjacking, MIME sniffing, XSS). |
| CSP                    | Limit external resource loading and reduce XSS injection surface. |
| Rate Limiting (Redis)  | Throttle abusive clients to reduce DoS risk. |
| Pydantic Validation    | Ensure request structure & types; early rejection of malformed data. |
| In-memory Token Only   | Token not persisted in `localStorage`, lowering persistent XSS exposure. |

---

## Deployment Options

### 1. Render (Managed Hosting)
* Uses `render.yaml` as a blueprint.
* Accessible at: `https://webpredictor-api.onrender.com`
* Contact me for credentials.
* Free tier limitations may apply (cold starts, resource caps).
* Built automatically from the repository; environment variables configured in Render dashboard.

### 2. Local Development (Manual)

Prerequisites:
* Python 3.10+
* Redis server running locally (`redis://localhost:6379/0` or Docker equivalent)

Environment setup (Windows CMD style):
```
set API_HOST_SECRET_KEY=changeme
set IP_KEY_SALT=changeme
set USERS_DB_URL=sqlite:///./users.db
set ADMIN_PASSWORD=adminpass
set REDIS_URL=redis://localhost:6379/0
```
Initialize users database and run development server:
```
python backend/db/dev_init_db.py
uvicorn backend.api.main:app --reload --port 8000
```
Visit: `http://localhost:8000/` (frontend), plus `/docs` and `/redoc`.

---

## Pytest
To test the code using pytest, you can run the pytest workflow.

---

## Quick Test Payload Example
Sample request body for `/tabular_regressor/train_predict`:
```json
{
	"model_type": "LinearRegression",
	"target_columns": ["target"],
	"feature_columns": ["feature1", "feature2"],
	"train_data": {
		"rows": [
			{ "index": 0, "feature1": 1.0, "feature2": 2.0, "target": 5.0 },
			{ "index": 1, "feature1": 2.0, "feature2": 1.0, "target": 4.5 },
			{ "index": 2, "feature1": 3.0, "feature2": 3.0, "target": 7.0 }
		]
	},
	"predict_data": {
		"rows": [
			{ "index": 0, "feature1": 1.5, "feature2": 2.5 },
			{ "index": 1, "feature1": 2.0, "feature2": 2.0 },
			{ "index": 2, "feature1": 3.5, "feature2": 1.5 }
		]
	}
}
```

---

## License
MIT License.

---

## Contact
Maintainer: Javier Castellano Soria
