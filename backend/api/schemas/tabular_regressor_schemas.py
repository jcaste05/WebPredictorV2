from typing import Any, Dict, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge

import backend.models as bm
from backend.models.tabular_regressor import TabularRegressor

# --- DoS protection / validation limits ---

MAX_TRAIN_ROWS: int = 1_000
MAX_PREDICT_ROWS: int = 1_000
MAX_TOTAL_COLUMNS: int = 200  # total union of feature + target columns
MAX_FEATURE_COLUMNS: int = 150
MAX_TARGET_COLUMNS: int = 10
MAX_COLUMN_NAME_LENGTH: int = 64
MAX_STRING_LENGTH: int = 64  # max length for any string cell value
MAX_INDEX_STRING_LENGTH: int = 64

# Available sklearn base models (store classes, not instances, to avoid shared state)
str_to_sk_model = {
    "LinearRegression": LinearRegression,
    "Ridge": Ridge,
    "Lasso": Lasso,
    "RandomForestRegressor": RandomForestRegressor,
}
AVAILABLE_MODELS = list(str_to_sk_model.keys())


class DataRow(BaseModel):
    """Schema for a single row of tabular data."""

    model_config = ConfigDict(extra="allow")

    index: Union[int, str]

    @field_validator("index")
    @classmethod
    def _limit_index_length(cls, v):
        if isinstance(v, str) and len(v) > MAX_INDEX_STRING_LENGTH:
            raise ValueError(f"Index string length exceeds {MAX_INDEX_STRING_LENGTH}")
        return v

    @model_validator(mode="before")
    @classmethod
    def _validate_extra_columns(cls, data: Dict[str, Any]):
        if len(data) - 1 > MAX_TOTAL_COLUMNS:  # exclude index
            raise ValueError(
                f"Number of columns ({len(data) - 1}) exceeds {MAX_TOTAL_COLUMNS}"
            )
        for k, v in list(data.items()):
            if k == "index":
                continue
            if len(k) > MAX_COLUMN_NAME_LENGTH:
                raise ValueError(
                    f"Column name '{k}' exceeds length {MAX_COLUMN_NAME_LENGTH}"
                )
            if isinstance(v, bool):
                data[k] = float(v)
                continue
            if isinstance(v, (int, float)):
                data[k] = float(v)
                continue
            if isinstance(v, str):
                if len(v) > MAX_STRING_LENGTH:
                    raise ValueError(
                        f"Column '{k}' string length exceeds {MAX_STRING_LENGTH}"
                    )
                continue
            # Reject other types
            raise TypeError(
                f"Column '{k}' invalid type '{type(v).__name__}'; only float, bool or str allowed"
            )
        return data


class TabularData(BaseModel):
    """
    Schema for tabular data represented as a list of rows.
    Performs defensive validation to prevent oversized payloads.
    """

    rows: List[DataRow] = Field(..., description="List of data rows similar to a table")

    @field_validator("rows")
    @classmethod
    def _non_empty(cls, v: List[DataRow]):
        if not v:
            raise ValueError("Rows must not be empty")
        return v

    def to_dataframe(self) -> pd.DataFrame:
        dict_rows: List[Dict[str, Any]] = []
        for row in self.rows:
            dict_rows.append(row.model_dump(by_alias=True))
        return pd.DataFrame(dict_rows)


class TrainPredictRequest(BaseModel):
    model_type: str = Field(
        ...,
        description="Model type: consult available models in /tabular_regressor/available_models",
    )
    target_columns: List[str] = Field(
        ..., description="Target columns present in training data rows"
    )
    feature_columns: Optional[List[str]] = Field(
        None, description="Feature columns; inferred if omitted"
    )
    train_data: TabularData = Field(
        ..., description="Rows including features and target columns"
    )
    predict_data: TabularData = Field(
        ..., description="Rows including features only for inference"
    )

    @field_validator("model_type")
    @classmethod
    def check_model_type(cls, v):
        if v not in AVAILABLE_MODELS:
            raise ValueError(f"model_type must be one of {AVAILABLE_MODELS}")
        return v

    @field_validator("target_columns")
    @classmethod
    def _check_targets(cls, v: List[str]):
        if len(v) == 0:
            raise ValueError("At least one target column required")
        if len(v) > MAX_TARGET_COLUMNS:
            raise ValueError(
                f"Number of target columns ({len(v)}) exceeds {MAX_TARGET_COLUMNS}"
            )
        if len(set(v)) != len(v):
            raise ValueError("Duplicate target columns detected")
        for c in v:
            if len(c) > MAX_COLUMN_NAME_LENGTH:
                raise ValueError(
                    f"Target column '{c}' exceeds length {MAX_COLUMN_NAME_LENGTH}"
                )
        return v

    @field_validator("feature_columns")
    @classmethod
    def _check_features(cls, v: Optional[List[str]]):
        if v is None:
            return v
        if len(v) == 0:
            raise ValueError("feature_columns if provided must not be empty")
        if len(v) > MAX_FEATURE_COLUMNS:
            raise ValueError(
                f"Number of feature columns ({len(v)}) exceeds {MAX_FEATURE_COLUMNS}"
            )
        if len(set(v)) != len(v):
            raise ValueError("Duplicate feature columns detected")
        for c in v:
            if len(c) > MAX_COLUMN_NAME_LENGTH:
                raise ValueError(
                    f"Feature column '{c}' exceeds length {MAX_COLUMN_NAME_LENGTH}"
                )
        return v

    @field_validator("train_data")
    @classmethod
    def _validate_train_data(cls, v: TabularData):
        if len(v.rows) > MAX_TRAIN_ROWS:
            raise ValueError(
                f"Number of training rows ({len(v.rows)}) exceeds {MAX_TRAIN_ROWS}"
            )
        return v

    @field_validator("predict_data")
    @classmethod
    def _validate_predict_data(cls, v: TabularData):
        if len(v.rows) > MAX_PREDICT_ROWS:
            raise ValueError(
                f"Number of prediction rows ({len(v.rows)}) exceeds {MAX_PREDICT_ROWS}"
            )
        return v

    def get_model_instance(self) -> TabularRegressor:
        """Create a fresh model instance each request to avoid shared mutable state."""
        base_cls = str_to_sk_model[self.model_type]
        base_model = bm.SKLearnRegressor(base_model=base_cls())
        return bm.MultiTargetRegressor(base_model=base_model)


class Prediction(BaseModel):
    index: Union[int, str]
    values: Dict[str, float]


class TrainPredictMetrics(BaseModel):
    mse: Dict[str, float]
    mae: Dict[str, float]
    baseline_mse: Dict[str, float]


class TrainPredictResponse(BaseModel):
    model_type: str
    model_version: str
    api_version: str
    targets: List[str]
    metrics: TrainPredictMetrics
    predictions: List[Prediction]
