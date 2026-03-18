"""Search service configuration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from shared.config import BaseAppSettings


class SearchSettings(BaseAppSettings):
    APP_NAME: str = "Hena Wadeena Search Service"
    APP_PORT: int = 8009
    DEBUG: bool = True
    SEARCH_DATABASE_URL: str = "mysql+aiomysql://root:root@mysql:3306/hena_search"


settings = SearchSettings()
