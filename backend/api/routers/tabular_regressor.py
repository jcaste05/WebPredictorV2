import numpy as np
from fastapi import APIRouter, Depends, Security
from fastapi_limiter.depends import RateLimiter
from sklearn.metrics import mean_absolute_error, mean_squared_error

from backend.api.config import DEFAULT_RL
from backend.api.schemas.tabular_regressor_schemas import (
    AVAILABLE_MODELS,
    TrainPredictMetrics,
    TrainPredictRequest,
    TrainPredictResponse,
)
from backend.api.security.auth import get_current_user
from backend.api.version import __version__ as api_version
from backend.db.models import User
from backend.models.name_conventions import INDEX_COL, PRED_SUFFIX
from backend.models.version import __version__ as model_version

# Router dedicated to tabular regressor operations
router = APIRouter(
    prefix="/tabular_regressor",
    tags=["tabular_regressor"],
    dependencies=[Depends(RateLimiter(times=DEFAULT_RL[0], seconds=DEFAULT_RL[1]))],
)


def _format_predictions(preds_df):
    predictions = []
    for _, row in preds_df.iterrows():
        idx = row[INDEX_COL]
        values = {c: float(row[c]) for c in preds_df.columns if c != INDEX_COL}
        predictions.append({"index": idx, "values": values})
    return predictions


train_predict_kwargs = dict(
    summary="Train a tabular regressor model and return predictions",
    response_model=TrainPredictResponse,
)


@router.post("/train_predict", **train_predict_kwargs)
def train_and_predict(
    payload: TrainPredictRequest,
    user: User = Security(get_current_user, scopes=["client"]),
):
    train_df = payload.train_data.to_dataframe()
    predict_df = payload.predict_data.to_dataframe()
    target_cols = payload.target_columns
    feature_cols = payload.feature_columns or [
        c for c in train_df.columns if c not in (target_cols + [INDEX_COL])
    ]

    # Build X and y DataFrames
    X_train = train_df[[INDEX_COL] + feature_cols].copy()
    y_train = train_df[[INDEX_COL] + target_cols].copy()
    X_predict = predict_df[[INDEX_COL] + feature_cols].copy()

    # Create model and fit
    model = payload.get_model_instance()
    model.fit(X_train, y_train)

    # Evaluate metrics (MSE vs baseline mean predictor)
    mse = {}
    mae = {}
    baseline_mse = {}
    for t in target_cols:
        preds_df_train = model.predict(X_train)
        pred_col = t + PRED_SUFFIX
        mse[t] = float(mean_squared_error(y_train[t], preds_df_train[pred_col]))
        mae[t] = float(mean_absolute_error(y_train[t], preds_df_train[pred_col]))
        baseline_mse[t] = float(
            mean_squared_error(y_train[t], np.full_like(y_train[t], y_train[t].mean()))
        )

    predictions_df = model.predict(X_predict)
    return TrainPredictResponse(
        model_type=payload.model_type,
        model_version=model_version,
        api_version=api_version,
        targets=target_cols,
        metrics=TrainPredictMetrics(mse=mse, mae=mae, baseline_mse=baseline_mse),
        predictions=_format_predictions(predictions_df),
    )


available_models_kwargs = dict(
    summary="Get available tabular regressor models",
)


@router.post("/available_models", **available_models_kwargs)
def available_models():
    return {"available_models": AVAILABLE_MODELS}
