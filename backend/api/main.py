from fastapi import FastAPI

from backend.api.routers.auth import router as auth_router
from backend.api.routers.tabular_regressor import router as tabular_regressor_router
from backend.api.routers.experiments import router as experiments_router
from backend.api.schemas.main_schemas import WelcomeResponse
from backend.api.version import __version__ as api_version
from backend.models.version import __version__ as model_version

app = FastAPI(title="WebPredictorV2 API", version=api_version)

app.include_router(auth_router)
app.include_router(tabular_regressor_router)
app.include_router(experiments_router)


welcome_kwargs = dict(
    tags=["welcome"],
    summary="API welcome endpoint",
    response_model=WelcomeResponse,
)


@app.get("/", **welcome_kwargs)
def welcome_root() -> WelcomeResponse:
    resource_paths = sorted(
        {r.path for r in app.routes if getattr(r, "include_in_schema", False)}
    )
    links = {
        "docs": "/docs",
        "redoc": "/redoc",
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
