from backend.models.base import BaseModel


def load_model(path: str) -> BaseModel:
    """Simple wrapper of load method from BaseModel."""
    return BaseModel.load(path)
