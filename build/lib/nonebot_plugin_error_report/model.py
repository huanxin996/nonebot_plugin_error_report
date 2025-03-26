from nonebot import require
from tortoise import fields
from tortoise.models import Model
require("nonebot_plugin_tortoise_orm")
from nonebot_plugin_tortoise_orm import add_model
add_model("nonebot_plugin_error_report.model")

class ErrorReport(Model):
    id = fields.IntField(pk=True)
    user_id = fields.CharField(max_length=64)
    bot_id = fields.CharField(max_length=64)
    session_id = fields.CharField(max_length=64)
    message = fields.TextField()
    error_msg = fields.TextField()
    time = fields.DatetimeField()