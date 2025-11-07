from typing import Dict, List
from pydantic import BaseModel


class WelcomeResponse(BaseModel):
    status: str
    service_name: str
    description: str
    api_version: str
    model_version: str
    resources: List[str]
    links: Dict[str, str]
