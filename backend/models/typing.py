from typing import Dict, List, TypeAlias, Union

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge


# --- General purpose types ---
JSONType: TypeAlias = Union[
    None, bool, int, float, str, List["JSONType"], Dict[str, "JSONType"]
]
SerializableState: TypeAlias = Dict[str, JSONType]

# --- Tabular regressor types ---
SklearnRegressor: TypeAlias = Union[
    LinearRegression, Ridge, Lasso, RandomForestRegressor
]
