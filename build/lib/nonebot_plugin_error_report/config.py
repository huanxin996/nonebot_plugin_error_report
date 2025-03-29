__author__ = "HuanXin"

import nonebot
from pydantic import BaseModel, Field
from nonebot import get_plugin_config


class Config(BaseModel):
    # 错误报告配置
    error_image_quality: int = Field(default=30, ge=1, le=100, description="报错图片渲染质量(1-100)")
    error_image_font: str = Field(default=None, description="报错图片字体文件路径")

    # 错误记录配置
    enable_error_report: bool = Field(default=True, description="是否启用错误自动发送功能")
    enable_error_logs: bool = Field(default=True, description="是否启用错误记录功能")
    use_orm_database: bool = Field(default=True, description="是否启用数据库存储错误记录,默认启用，不启用则将使用json文件存储错误信息")
    
    # 邮件配置
    enable_email: bool = Field(default=False, description="是否启用邮件通知功能")
    smtp_host: str = Field(default="smtp.qq.com", description="SMTP服务器地址")
    smtp_port: int = Field(default=465, description="SMTP服务器端口")
    smtp_ssl: bool = Field(default=True, description="是否使用SSL连接")
    smtp_user: str = Field(default="", description="SMTP用户名")
    smtp_password: str = Field(default="", description="SMTP密码或授权码")
    email_batch_size: int = Field(default=10, ge=1, description="批量发送邮件时每批次的大小")
    email_from: str = Field(default="", description="发件人邮箱")
    email_to: list[str] = Field(default_factory=list, description="收件人邮箱列表")
    
    # 定时发送配置
    enable_scheduled_report: bool = Field(default=False, description="是否启用定时发送报告")
    report_mode: str = Field(
        default="count",
        description="报告触发模式: count(达到数量触发) / time(定时触发)"
    )
    report_count: int = Field(
        default=10,
        ge=1,
        description="新增错误达到多少条时发送报告(report_mode=count时生效)"
    )
    report_interval: str = Field(
        default="0 0 * * *",
        description="定时发送的cron表达式(report_mode=time时生效),默认每天0点"
    )
    report_template: str = Field(
        default="new_errors_{date}.html",
        description="报告模板文件名,支持{date}变量"
    )
    clear_after_report: bool = Field(
        default=False,
        description="发送报告后是否清空已发送的错误记录"
    )
    
    ignored_plugins: list[str] = Field(
        default_factory=list,
        description="忽略的插件列表,这些插件的错误将不会被记录"
    )
    ignore_patterns: list[str] = Field(
        default_factory=list, 
        description="忽略的错误模式,支持正则表达式"
    )   


class BotBaseError(Exception):
    """机器人错误的基类"""
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)

class BotRunTimeError(BotBaseError):
    """运行时错误"""
    pass

class BotConfigError(BotBaseError):
    """配置错误"""
    pass

class BotNetworkError(BotBaseError):
    """网络错误"""
    pass

class BotDatabaseError(BotBaseError):
    """数据库错误"""
    pass

class BotPermissionError(BotBaseError):
    """权限错误"""
    pass

class BotResourceError(BotBaseError):
    """资源错误(如文件不存在)"""
    pass

class BotTimeoutError(BotBaseError):
    """超时错误"""
    pass

global_config = nonebot.get_driver().config
error_config = get_plugin_config(Config)

