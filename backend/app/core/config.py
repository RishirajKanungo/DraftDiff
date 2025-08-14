from pydantic import BaseModel
from pydantic import Field
import os
from typing import Optional, List


class Settings(BaseModel):
    environment: str = Field(default=os.getenv("ENVIRONMENT", "development"))
    cors_allow_origins: List[str] = Field(
        default=os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000").split(",")
    )

    # Model serving
    model_path: str = Field(default=os.getenv("MODEL_PATH", "./models/model.joblib"))

    # Riot API config
    riot_api_key: Optional[str] = Field(default=os.getenv("RIOT_API_KEY"))
    riot_platform: str = Field(default=os.getenv("RIOT_PLATFORM", "na1"))  # e.g., na1, euw1
    riot_region: str = Field(default=os.getenv("RIOT_REGION", "americas"))  # americas, europe, asia

    # DDragon (static data)
    ddragon_version: Optional[str] = Field(default=os.getenv("DDRAGON_VERSION"))


settings = Settings()
