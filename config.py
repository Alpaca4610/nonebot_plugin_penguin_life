from pydantic import Extra, BaseModel
from typing import Optional


class Config(BaseModel, extra=Extra.ignore):
    token = ""     #   胖乖生活token

class ConfigError(Exception):
    pass
