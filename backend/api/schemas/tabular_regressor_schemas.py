from typing import Any, Dict, List, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field, validator
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge

import backend.models as bm
from backend.models.tabular_regressor import TabularRegressor

# Available sklearn base models wrapped for multi-target regression
str_to_sk_model = {
    "LinearRegression": LinearRegression(),
    "Ridge": Ridge(),
    "Lasso": Lasso(),
    "RandomForestRegressor": RandomForestRegressor(),
}
AVAILABLE_MODELS = {
    sk_model_str: bm.MultiTargetRegressor(
        base_model=bm.SKLearnRegressor(base_model=sk_model)
    )
    for sk_model_str, sk_model in str_to_sk_model.items()
}


class DataRow(BaseModel):
    """Schema for a single row of tabular data."""

    index: Union[int, str]

    class Config:
        extra = "allow"


class TabularData(BaseModel):
    """Schema for tabular data represented as a list of rows."""

    rows: List[DataRow] = Field(..., description="List of data rows similar to a table")

    def to_dataframe(self):
        dict_rows = [r.dict(by_alias=True) for r in self.rows]
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

    @validator("model_type")
    def check_model_type(cls, v):
        if v not in AVAILABLE_MODELS:
            raise ValueError(
                f"sklearn_model must be one of {list(AVAILABLE_MODELS.keys())}"
            )
        return v
    
    def get_model_instance(self) -> TabularRegressor:
        """Get an instance of the specified model type."""
        model = AVAILABLE_MODELS[self.model_type]
        return model


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
