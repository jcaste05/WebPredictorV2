import json
import os
from abc import abstractmethod
from copy import deepcopy
from typing import Optional, Union

import joblib
import numpy as np
import pandas as pd

from backend.models.base import BaseFitPredictModel
from backend.models.name_conventions import (
    INDEX_COL,
    MODEL_FOLDER,
    PRED_SUFFIX,
    SK_JOBLIB_MODEL_FILE,
    SK_METADATA_FILE,
)
from backend.models.typing import SerializableState, SklearnRegressor


# Models from external libraries that can be safely saved/loaded with joblib
JOBLIB_MODELS = [
    "LinearRegression",
    "Ridge",
    "Lasso",
    "RandomForestRegressor",
]


class TabularRegressor(BaseFitPredictModel[pd.DataFrame, pd.DataFrame]):
    """
    Base class for tabular regression models. Handles input and output DataFrames.
    Methods _fit and _predict need to be implemented in subclasses.
    """

    def __init__(
        self,
        x_columns: Optional[list[str]] = None,
        y_columns: Optional[list[str]] = None,
    ):
        self.__x_columns = x_columns
        self.__y_columns = y_columns

    def fit(self, X: pd.DataFrame, y: pd.DataFrame):
        if self.x_columns is None:
            self.__x_columns = [c for c in X.columns if c != INDEX_COL]
        if self.y_columns is None:
            self.__y_columns = [c for c in y.columns if c != INDEX_COL]
        X_copy = X[[INDEX_COL] + self.x_columns].copy()
        y_copy = y[[INDEX_COL] + self.y_columns].copy()
        self._fit(X_copy, y_copy)

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        X_copy = X[[INDEX_COL] + self.x_columns].copy()
        return self._predict(X_copy)

    def _serialize(self) -> SerializableState:
        state = super()._serialize()
        state.update(
            {
                "x_columns": self.x_columns,
                "y_columns": self.y_columns,
            }
        )
        return state

    def _deserialize(self, state: SerializableState):
        super()._deserialize(state)
        self.__x_columns = state["x_columns"]
        self.__y_columns = state["y_columns"]

    @property
    def x_columns(self) -> list[str]:
        if self.__x_columns is None:
            return None
        else:
            return [c for c in self.__x_columns if c != INDEX_COL]

    @property
    def y_columns(self) -> list[str]:
        if self.__y_columns is None:
            return None
        else:
            return [c for c in self.__y_columns if c != INDEX_COL]

    @abstractmethod
    def _fit(self, X: pd.DataFrame, y: pd.DataFrame):
        pass

    @abstractmethod
    def _predict(self, X: pd.DataFrame) -> pd.DataFrame:
        pass


class SKLearnRegressor(TabularRegressor):
    """Sklearn-based tabular regressor wrapper."""

    def __init__(
        self,
        base_model: SklearnRegressor,
        x_columns: Optional[list[str]] = None,
        y_columns: Optional[list[str]] = None,
    ):
        super().__init__(x_columns, y_columns)
        self.base_model = base_model

    def _fit(self, X: pd.DataFrame, y: pd.DataFrame):
        if len(self.y_columns) > 1:
            raise ValueError(
                "SKLearnRegressor does not support more than one target column."
            )
        self.base_model.fit(X[self.x_columns], y[self.y_columns[0]])

    def _predict(self, X: pd.DataFrame) -> pd.DataFrame:
        result = X[[INDEX_COL]].copy()
        preds = self.base_model.predict(X[self.x_columns])
        preds = np.squeeze(preds)
        result[self.y_columns[0] + PRED_SUFFIX] = preds
        return result

    def _save(self, path: str):
        super()._save(path)
        model_folder_path = os.path.join(path, MODEL_FOLDER)
        os.makedirs(model_folder_path, exist_ok=True)
        # Save sklearn metadata
        metadata_path = os.path.join(model_folder_path, SK_METADATA_FILE)
        name = self.base_model.__class__.__name__
        metadata = {
            "model_type": name,
        }
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)
        # Save sklearn model
        if name in JOBLIB_MODELS:
            model_path = os.path.join(model_folder_path, SK_JOBLIB_MODEL_FILE)
            joblib.dump(self.base_model, model_path)
        else:
            raise ValueError(f"Model type {name} not supported for saving.")

    def _load(self, path: str):
        super()._load(path)
        model_folder_path = os.path.join(path, MODEL_FOLDER)
        # Load sklearn metadata
        metadata_path = os.path.join(model_folder_path, SK_METADATA_FILE)
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        name = metadata["model_type"]
        # Load sklearn model
        if name in JOBLIB_MODELS:
            model_path = os.path.join(model_folder_path, SK_JOBLIB_MODEL_FILE)
            self.base_model = joblib.load(model_path)
        else:
            raise ValueError(f"Model type {name} not supported for loading.")


class MultiTargetRegressor(TabularRegressor):
    """
    Tabular regressor that handles multiple target variables by maintaining
    separate models for each target variable.
    """

    def __init__(
        self,
        base_model: Union[TabularRegressor, dict[str, TabularRegressor]],
        x_columns=None,
        y_columns=None,
    ):
        super().__init__(x_columns, y_columns)
        self.base_model = base_model

    def _fit(self, X: pd.DataFrame, y: pd.DataFrame):
        models = dict()
        if isinstance(self.base_model, dict):
            for target in self.y_columns:
                if target in self.base_model:
                    models[target] = deepcopy(self.base_model[target])
                else:
                    raise ValueError(
                        f"Base model dictionary does not contain a model for target: {target}."
                    )
        else:
            for target in self.y_columns:
                models[target] = deepcopy(self.base_model)

        self.base_model = models
        for target in self.y_columns:
            self.base_model[target].fit(X, y[[INDEX_COL, target]])

    def _predict(self, X: pd.DataFrame) -> pd.DataFrame:
        result = X[[INDEX_COL]].copy()
        for target, model in self.base_model.items():
            preds = model.predict(X)
            pred_col = target + PRED_SUFFIX
            result[pred_col] = preds[pred_col].values
        return result

    def _save(self, path: str):
        super()._save(path)
        model_folder_path = os.path.join(path, MODEL_FOLDER)
        os.makedirs(model_folder_path, exist_ok=True)
        for target, model in self.base_model.items():
            sub_path = os.path.join(model_folder_path, target)
            model.save(sub_path)

    def _load(self, path: str):
        super()._load(path)
        model_folder_path = os.path.join(path, MODEL_FOLDER)
        self.base_model = dict()
        for target in self.y_columns:
            sub_path = os.path.join(model_folder_path, target)
            self.base_model[target] = self.load(sub_path)
