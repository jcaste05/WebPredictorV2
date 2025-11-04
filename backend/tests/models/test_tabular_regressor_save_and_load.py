import os
import shutil
import tempfile

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_squared_error

from backend.models import MultiTargetRegressor, SKLearnRegressor, load_model
from backend.models.name_conventions import INDEX_COL, PRED_SUFFIX


@pytest.fixture
def simulated_data():
    """Generate simple linear data with two target variables."""
    rng = np.random.default_rng(42)
    n = 200
    X = pd.DataFrame(
        {
            INDEX_COL: np.arange(n),
            "x1": rng.normal(0, 1, n),
            "x2": rng.normal(0, 1, n),
        }
    )
    y1 = 3 * X["x1"] + 2 * X["x2"] + rng.normal(0, 0.1, n)
    y2 = -1.5 * X["x1"] + 4 * X["x2"] + rng.normal(0, 0.1, n)
    y = pd.DataFrame({INDEX_COL: X[INDEX_COL], "y1": y1, "y2": y2})
    return X, y


@pytest.fixture
def temp_models_dir():
    """Temporary directory for model tests."""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp)


@pytest.mark.models
@pytest.mark.parametrize(
    "sk_model_cls",
    [LinearRegression, Ridge, Lasso, RandomForestRegressor],
)
def test_multitarget_regressor_train_save_load(
    simulated_data, temp_models_dir, sk_model_cls
):
    X, y = simulated_data

    base = SKLearnRegressor(base_model=sk_model_cls())
    model = MultiTargetRegressor(base_model=base)
    model.fit(X.copy(), y.copy())
    preds = model.predict(X.copy())

    expected_cols = [INDEX_COL, "y1" + PRED_SUFFIX, "y2" + PRED_SUFFIX]
    assert list(preds.columns) == expected_cols

    mse_y1 = mean_squared_error(y["y1"], preds["y1" + PRED_SUFFIX])
    mse_y2 = mean_squared_error(y["y2"], preds["y2" + PRED_SUFFIX])
    baseline_y1 = mean_squared_error(y["y1"], np.full_like(y["y1"], y["y1"].mean()))
    baseline_y2 = mean_squared_error(y["y2"], np.full_like(y["y2"], y["y2"].mean()))

    assert mse_y1 < baseline_y1 * 0.5, f"High MSE for y1 with {sk_model_cls.__name__}"
    assert mse_y2 < baseline_y2 * 0.5, f"High MSE for y2 with {sk_model_cls.__name__}"

    model_dir = os.path.join(temp_models_dir, "multitarget_model")
    model.save(model_dir, overwrite=False)
    loaded = load_model(model_dir)
    shutil.rmtree(model_dir)
    preds_loaded = loaded.predict(X)
    pd.testing.assert_frame_equal(preds, preds_loaded)


@pytest.mark.models
@pytest.mark.parametrize(
    "sk_model_cls",
    [LinearRegression, Ridge, Lasso, RandomForestRegressor],
)
def test_sklearn_regressor_train_save_load(simulated_data, temp_models_dir, sk_model_cls):
    X, y = simulated_data
    y_single = y[[INDEX_COL, "y1"]].copy()

    base = SKLearnRegressor(base_model=sk_model_cls())
    base.fit(X.copy(), y_single)
    preds = base.predict(X.copy())

    expected_cols = [INDEX_COL, "y1" + PRED_SUFFIX]
    assert list(preds.columns) == expected_cols

    mse_y1 = mean_squared_error(y_single["y1"], preds["y1" + PRED_SUFFIX])
    baseline_y1 = mean_squared_error(
        y_single["y1"], np.full_like(y_single["y1"], y_single["y1"].mean())
    )

    assert mse_y1 < baseline_y1 * 0.5, f"High MSE for y1 with {sk_model_cls.__name__}"

    model_dir = os.path.join(
        temp_models_dir, f"single_target_model_{sk_model_cls.__name__}"
    )
    base.save(model_dir, overwrite=False)
    loaded = load_model(model_dir)
    shutil.rmtree(model_dir)
    preds_loaded = loaded.predict(X)
    pd.testing.assert_frame_equal(preds, preds_loaded)
