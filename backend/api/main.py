from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import Depends, FastAPI, Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import Response, JSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from backend.api.config import DEFAULT_RL, REDIS_URL
from backend.api.routers.admin import router as admin_router
from backend.api.routers.auth import router as auth_router
from backend.api.routers.tabular_regressor import router as tabular_regressor_router
from backend.api.schemas.main_schemas import WelcomeResponse
from backend.api.security.config import DEFAULT_CSP, DOCS_CSP
from backend.api.security.limiter import real_ip
from backend.api.version import __version__ as api_version
from backend.models.version import __version__ as model_version


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code that runs on app startup
    r = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r, identifier=real_ip)

    # Point where the app is running
    yield

    # When the application is shutting down
    if FastAPILimiter.redis:
        await FastAPILimiter.redis.close()


app = FastAPI(
    title="WebPredictorAPI",
    version=api_version,
    lifespan=lifespan,
    default_response_class=JSONResponse,
    docs_url=None,
    redoc_url=None,
    contact={
        "name": "Javier Castellano Soria",
        "email": "webpredictorapi@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)


# Middleware to add security headers to each response
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = (
        "max-age=63072000; includeSubDomains; preload"
    )
    if "Content-Security-Policy" not in response.headers:
        response.headers["Content-Security-Policy"] = DEFAULT_CSP

    return response


docs_kwargs = dict(
    include_in_schema=False,
    dependencies=[Depends(RateLimiter(times=DEFAULT_RL[0], seconds=DEFAULT_RL[1]))],
)


@app.get("/docs", **docs_kwargs)
def custom_swagger_ui():
    resp = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
    )
    resp.headers["Content-Security-Policy"] = DOCS_CSP
    return resp


redoc_kwargs = dict(
    include_in_schema=False,
    dependencies=[Depends(RateLimiter(times=DEFAULT_RL[0], seconds=DEFAULT_RL[1]))],
)


@app.get("/redoc", **redoc_kwargs)
def custom_redoc():
    resp = get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
    )
    resp.headers["Content-Security-Policy"] = DOCS_CSP
    return resp


app.include_router(auth_router)
app.include_router(tabular_regressor_router)
app.include_router(admin_router)


welcome_kwargs = dict(
    tags=["welcome"],
    summary="API welcome endpoint",
    response_model=WelcomeResponse,
    dependencies=[Depends(RateLimiter(times=DEFAULT_RL[0], seconds=DEFAULT_RL[1]))],
)


@app.get("/", **welcome_kwargs)
def welcome_root() -> WelcomeResponse:
    resource_paths = sorted(
        {
            r.path
            for r in app.routes
            if getattr(r, "include_in_schema", False) and "admin" not in r.path
        }
    )
    links = {
        "docs": "/docs",
        "redoc": "/redoc",
        "API details": "/openapi.json",
    }
    description = "Training and inference service for several purposes"
    return WelcomeResponse(
        status="ok",
        service_name="WebPredictorV2 API",
        description=description,
        api_version=api_version,
        model_version=model_version,
        resources=resource_paths,
        links=links,
    )
