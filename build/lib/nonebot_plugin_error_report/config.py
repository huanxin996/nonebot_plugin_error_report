__author__ = "HuanXin"

import nonebot
from pydantic import BaseModel, Field
from nonebot import get_plugin_config


class Config(BaseModel):
    version: str = "0.0.1"
    error_image_quality: int = Field(default=30, ge=1, le=100, description="报错图片渲染质量(1-100)")
    error_image_font : str = Field(default=None, description="报错图片字体文件路径")


class BotRunTimeError(Exception):
    """bot runtime error"""

global_config = nonebot.get_driver().config
error_config = get_plugin_config(Config)

