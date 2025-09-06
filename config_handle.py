import os
from dataclasses import dataclass
from typing import Self

from briefconf.v0 import BriefConfig

configfile = os.getenv("ONECLICKOPEN_CONFIG_FILE", default="config.yaml")


@dataclass(frozen=True, slots=True)
class Config(BriefConfig):
    # 用户关心、需要手动配置的参数
    cap_instance_url: str | None
    site_key: str | None
    key_secret: str | None

    @classmethod
    def load(cls, config_path: str) -> Self:
        try:
            configs = cls._load_config(config_path)
        except FileNotFoundError as e:
            print(e)
            return cls(None, None, None)

        return cls(
            cap_instance_url=configs.get("cap_instance_url"),
            site_key=configs.get("site_key"),
            key_secret=configs.get("key_secret"),
        )


config = Config.load(os.path.abspath(configfile))

__all__ = ["config"]
