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
    max_hanota: int

    @classmethod
    def load(cls, config_path: str) -> Self:
        try:
            configs = cls._load_config(config_path)
        except FileNotFoundError as e:
            print(e)
            configs = {}

        return cls(
            cap_instance_url=configs.get("cap_instance_url"),
            site_key=configs.get("site_key"),
            key_secret=configs.get("key_secret"),
            max_hanota=configs.get("max_hanota", 10),
        )


config = Config.load(os.path.abspath(configfile))

__all__ = ["config"]
