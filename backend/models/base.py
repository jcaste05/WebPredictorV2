import json
import os
import shutil
from abc import abstractmethod
from typing import Generic, TypeVar

from backend.models.version import __version__
from backend.models.name_conventions import METADATA_FILE
from backend.models.typing import SerializableState


class ModelRegistry(type):
    """
    Metaclass for registering models.
    """

    registry = {}

    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        mcs.registry[name] = cls
        return cls

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.__version__ = __version__
        return instance

    @classmethod
    def get_model_class(mcs, name):
        return mcs.registry.get(name)


class BaseModel(metaclass=ModelRegistry):
    """
    Base interface for all models.
    """

    def _serialize(self) -> SerializableState:
        """
        Return a serializable dictionary representing the internal state.
        """
        return dict(__version__=self.__version__)

    def _deserialize(self, state: SerializableState):
        """
        Fill serializable attributes from state dictionary.
        """
        self.__version__ = state.get("__version__")
        pass

    def _save(self, path: str):
        """
        Save non-serializable attributes.
        """
        pass

    def _load(self, path: str):
        """
        Fill non-serializable attributes from path.
        """
        pass

    def save(self, path: str, overwrite: bool = True):
        """Save the model including serializable and non-serializable attributes."""
        if os.path.exists(path):
            if not overwrite:
                raise FileExistsError(f"Path {path} already exists.")
            shutil.rmtree(path)
        os.makedirs(path)
        # Serializable attributes
        metadata = {
            "__name__": self.__class__.__name__,
            "serializable_state": self._serialize(),
        }
        with open(os.path.join(path, METADATA_FILE), "w") as f:
            json.dump(metadata, f)
        # Non-serializable attributes
        self._save(path)

    @classmethod
    def load(cls, path: str):
        """Load the model from a given path."""
        # Load serializable attributes
        with open(os.path.join(path, METADATA_FILE), "r") as f:
            metadata = json.load(f)
        model_name = metadata["__name__"]
        model_class = ModelRegistry.get_model_class(model_name)
        if model_class is None:
            raise ValueError(f"Model class {model_name} not found in registry.")
        instance = model_class.__new__(model_class)
        instance._deserialize(metadata["serializable_state"])
        # Load non-serializable attributes
        instance._load(path)
        return instance


# --- Base models that extend the base contract by adding the new methods ---

XTypeFitPredict = TypeVar("XTypeFitPredict")
yTypeFitPredict = TypeVar("yTypeFitPredict")


class BaseFitPredictModel(BaseModel, Generic[XTypeFitPredict, yTypeFitPredict]):
    """
    Base interface for all fit and predict models.
    """

    @abstractmethod
    def fit(self, X: XTypeFitPredict, y: yTypeFitPredict):
        pass

    @abstractmethod
    def predict(self, X: XTypeFitPredict) -> yTypeFitPredict:
        pass
