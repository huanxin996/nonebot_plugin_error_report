import traceback,datetime,sys
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot import require
from nonebot.message import run_postprocessor
require("nonebot_plugin_userinfo")
require("nonebot_plugin_alconna")
from nonebot_plugin_userinfo import EventUserInfo, UserInfo, BotUserInfo
from nonebot_plugin_alconna import on_alconna,Alconna, Args, Option, CommandMeta,Arparma
from nonebot_plugin_alconna.uniseg import UniMessage,MsgTarget
from .config import Config,BotRunTimeError,error_config,BotDatabaseError,BotNetworkError
from .model import ErrorReport,ErrorCache
from .toimg import all_images_draw
from .email import send_batch_error_report
from nonebot.log import logger


__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_error_report",
    description="幻歆",
    usage=(
        "报错处理\n",
        "绘制为图片并发送,绘制失败自动切换为文字发送\n",
        "支持将报错信息存入数据库内，支持查看\n",
        "伪全平台支持⭐\n"
        "使用nonebot-plugin-userinfo获取用户信息\n"
        "使用nonebot_plugin_alconna发送信息\n"
        "鸣谢以上插件作者以及nonebot"
    ),
    type="application",
    homepage="https://github.com/huanxin996/nonebot_plugin_error_report",
    config=Config,
    supported_adapters=None,
)

error_cache = ErrorCache()
scheduler = None


error_manager = on_alconna(
    Alconna(
        "错误管理",
        Option("查找", Args["关键词", str]["vaule", str], help_text="查找指定错误记录，关键词为字段名，vaule为字段值"),
        Option("搜索", Args["关键词", str], help_text="搜索错误记录，关键词为错误信息"),
        Option("查看", Args["页数?", int], help_text="查看错误记录，页数默认为1"),
        Option("详情", Args["id?", int], help_text="查看错误详情，id为错误记录的ID"), 
        Option("删除", Args["id?", int], help_text="删除错误记录，id为错误记录的ID"),
        Option("清空", Args["type",str]["vaule",str], help_text="清空错误记录，type为all/user/bot/date，vaule为all/user_id/bot_id/date"),
        Option("统计", help_text="输出现有统计错误数量"),
        meta=CommandMeta(
            description="管理机器人运行时的错误记录",
            usage="错误管理 查看 [页数]\n错误管理 删除 [id]\n错误管理 统计"
        )
    ),
    aliases={"错误", "err"},
    use_cmd_start=True,
    block=True
)


@error_manager.handle()
async def handle_error_management(result: Arparma, target: MsgTarget,user_info: UserInfo = EventUserInfo(), bot_info: UserInfo = BotUserInfo()):
    if result.find("查找"):
        field = result.query[str]("查找.关键词")
        value = result.query[str]("查找.vaule")
        allowed_fields = [
            'bot_id', 'error_detail', 'error_msg', 'error_type',
            'id', 'message', 'plugin_name', 'session_id', 'user_id'
        ]
        
        if field not in allowed_fields:
            await UniMessage.text(
                f"无效的字段名: {field}\n"
                f"允许的字段名包括: {', '.join(allowed_fields)}"
            ).send(target)
            return
        try:
            filter_kwargs = {field: value}
            records = await ErrorReport.filter(**filter_kwargs).limit(10)
            if not records:
                await UniMessage.text(f"未找到包含关键词{keyword}的错误记录").send(target)
                return
            result_text = "搜索结果：\n" + "\n".join(
                f"ID: {r.id}\n"
                f"时间: {r.time.strftime('%Y年%m月%d日 %H:%M:%S')}\n"
                f"用户: {r.user_id}\n"
                f"错误: {r.error_msg[:50]}...\n"
                f"{'-'*20}"
                for r in records
            )
            await UniMessage.text(result_text).send(target)
        except Exception as e:
            await UniMessage.text(f"查询失败: {str(e)}").send(target)
    elif result.find("搜索"):
        keyword = result.query[str]("搜索.关键词")
        try:
            records = await ErrorReport.filter(error_msg__icontains=keyword).limit(10)
            if not records:
                await UniMessage.text(f"未找到包含关键词{keyword}的错误记录").send(target)
                return
            result_text = "搜索结果：\n" + "\n".join(
                f"ID: {r.id}\n时间: {r.time.strftime('%Y年%m月%d日 %H:%M:%S')}\n用户: {r.user_id}\n错误: {r.error_msg[:50]}...\n{'-'*20}"
                for r in records
            )
            await UniMessage.text(result_text).send(target)
        except Exception as e:
            await UniMessage.text(f"查询失败: {str(e)}").send(target)
    elif result.find("查看"):
        page = result.query[int]("查看.页数", 1)
        try:
            records = await ErrorReport.all().limit(10).offset((page-1)*10)
            if not records:
                await UniMessage.text("没有找到任何错误记录").send(target)
                return
            result_text = f"错误记录(第{page}页)：\n" + "\n".join(
                f"ID: {r.id}\n时间: {r.time.strftime('%Y年%m月%d日 %H:%M:%S')}\n用户: {r.user_id}\n错误: {r.error_msg[:50]}...\n{'-'*20}"
                for r in records
            )
            await UniMessage.text(result_text).send(target)
        except Exception as e:
            await UniMessage.text(f"查询失败: {str(e)}").send(target)
    elif result.find("详情"):
        error_id = result.query[int]("详情.id")
        try:
            record = await ErrorReport.filter(id=error_id).first()
            if not record:
                await UniMessage.text(f"未找到ID为{error_id}的错误记录").send(target)
                return
            result_text = (
                f"错误详情(ID: {record.id})：\n"
                f"时间: {record.time}\n"
                f"用户: {record.user_id}\n"
                f"插件: {record.plugin_name}\n"
                f"类型: {record.error_type}\n"
                f"错误: {record.error_msg}"
                f"\n错误详情: \n{record.error_detail}" if record.error_detail else ""
            )
            await UniMessage.text(result_text).send(target)
        except Exception as e:
            await UniMessage.text(f"查询失败: {str(e)}").send(target)
    elif result.find("删除"):
        error_id = result.query[int]("删除.id")
        try:
            if error_id:
                count = await ErrorReport.filter(id=error_id).delete()
                msg = f"已删除ID为{error_id}的错误记录" if count else "未找到该记录"
            else:
                count = await ErrorReport.all().delete()
                msg = f"已清空所有错误记录，共{count}条"
            await UniMessage.text(msg).send(target)
        except Exception as e:
            await UniMessage.text(f"删除失败: {str(e)}").send(target)
    elif result.find("清空"):
        type = result.query[str]("清空.type")
        value = result.query[str]("清空.vaule")
        try:
            msg = "请按照以下格式输入指令：\n错误管理 清空 [type] [value]\n" \
                  "type: all/user/bot/date\n" \
                    "value: all/user_id/bot_id/date\n" \
                    "例如：错误管理 清空 user all"
            if type not in ["all", "user", "bot", "date"]:
                await UniMessage.text(msg).send(target)
                return
            if value == "all":
                count = await ErrorReport.all().delete()
                msg = f"已清空所有错误记录，共{count}条"
            if type == "user" and value == "all":
                count = await ErrorReport.filter(user_id=user_info.user_id).delete()
                msg = f"已清空用户{user_info.user_id}的所有错误记录，共{count}条"
            elif type =="user" and value not in ["all",None]:
                try:
                    count = await ErrorReport.filter(user_id=value).delete()
                    msg = f"已清空用户{value}的所有错误记录，共{count}条"
                except ValueError as e:
                    msg = f"用户ID格式错误: {str(e)}"
            if type == "bot" and value == "all":
                count = await ErrorReport.filter(bot_id=bot_info.user_id).delete()
                msg = f"已清空机器人{bot_info.user_id}的记录的所有错误记录，共{count}条"
            elif type == "bot" and value not in ["all",None]:
                try:
                    count = await ErrorReport.filter(bot_id=value).delete()
                    msg = f"已清空机器人{value}的记录的所有错误记录，共{count}条"
                except ValueError as e:
                    msg = f"机器人ID格式错误: {str(e)}"
            if type == "date" and value == "all":
                count = await ErrorReport.filter(time__lt=datetime.datetime.now()).delete()
                msg = f"已清空所有早于当前时间的错误记录，共{count}条"
            elif type == "date" and value not in ["all",None]:
                try:
                    time_obj = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    count = await ErrorReport.filter(time__lt=time_obj).delete()
                    msg = f"已清空所有早于 {time_obj.strftime('%Y年%m月%d日 %H:%M:%S')} 的错误记录，共{count}条"
                except ValueError as e:
                    msg = f"时间格式错误: {str(e)}，请使用 %Y-%m-%d %H:%M:%S 格式"
            await UniMessage.text(msg).send(target)
        except Exception as e:
            await UniMessage.text(f"清空失败: {str(e)}").send(target)
    elif result.find("统计"):
        try:
            count = await ErrorReport.all().count()
            await UniMessage.text(f"当前共有 {count} 条错误记录").send(target)
        except Exception as e:
            await UniMessage.text(f"统计失败: {str(e)}").send(target)
    else:
        help_text = "请按以下格式输入指令：\n错误管理 查看 [页数]\n错误管理 删除 [id]\n错误管理 统计"
        await UniMessage.text(help_text).send(target)

@run_postprocessor
async def post_run(matcher:Matcher,event: Event, e: Exception, target: MsgTarget, bot_info: UserInfo = BotUserInfo(), user_info: UserInfo = EventUserInfo()) -> None:
    plugin_name = matcher.plugin.name
    error_type = type(e).__name__
    logger.debug(f"插件：【{matcher.plugin.name}】 运行时错误: {str(e)}")
    if plugin_name in error_config.ignored_plugins or error_type in error_config.ignore_patterns:
        logger.debug(f"因为插件【{plugin_name}】在忽略列表中，所以不进行处理" if plugin_name in error_config.ignored_plugins else f"因为错误类型【{error_type}】在忽略列表中，所以不进行处理")
        return
    try:
        if hasattr(e, "__traceback__"):
            tb_list = traceback.format_exception(type(e), e, e.__traceback__)
            error_detail = "".join(tb_list)
        else:
            error_detail = "\n".join(e.args)
        img = await error_to_images(plugin_name,err_values=e)
    except BotRunTimeError:
        logger.warning(f"生成 [{plugin_name}]:{error_type} 错误报告图片失败，将使用文字方式发送")
        img = None
    try:
        await update_or_create(
            user_id=user_info.user_id,
            bot_id=bot_info.user_id,
            session_id=event.get_session_id(),
            message=event.get_message(),
            error_type=error_type,
            error_msg=e,
            error_detail=error_detail,
            plugin_name=plugin_name,
            time=datetime.datetime.now()
        )
        if img:
            await UniMessage.image(raw=img).send(target=target)
        else:
            error_msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
            result = f"抱歉，我出现了一点问题，请尝试使用其他指令，或者联系开发者\n以下是错误信息:\n{error_msg}"
            await UniMessage.text(result).send(target=target)
    except Exception as handle_err:
        logger.error(f"处理错误时发生异常: {handle_err}")
        if isinstance(handle_err, BotDatabaseError):
            await UniMessage.text("数据库操作失败,请检查配置").send(target=target)
        elif isinstance(handle_err, BotNetworkError):
            await UniMessage.text("网络连接失败,请稍后重试").send(target=target)
        else:
            raise BotRunTimeError(f"未知错误: {str(handle_err)}")

async def update_or_create(**kwargs) -> bool:
    """更新或创建错误记录"""
    try:
        total_count = await ErrorReport.all().count()
        new_id = total_count + 1
        kwargs["id"] = new_id
        error_record = await ErrorReport.create(**kwargs)
        if not error_record:
            raise BotDatabaseError("创建错误记录失败")
        error_cache.add_error(kwargs)
        if error_config.enable_scheduled_report and error_config.report_mode == "count":
            unsent_count = len(error_cache.get_unsent_errors())
            if unsent_count >= error_config.report_count:
                await check_error_count()
        return True
    except Exception as e:
        logger.error(f"更新错误记录失败: {str(e)}")
        if isinstance(e, BotDatabaseError):
            raise
        return False

async def error_to_images(plugin_name:str = None,err_values: Exception = None) -> bytes:
    """生成错误报告图片"""
    if err_values == None:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_detail = traceback.format_exc()
        error_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
        error_msg = "".join(error_list)
    else:
        error_msg = f"异常类型: {type(err_values).__name__}&hx&"
        error_msg += f"错误信息: {str(err_values)}"
        if hasattr(err_values, "__traceback__"):
            tb_list = traceback.format_exception(type(err_values), err_values, err_values.__traceback__)
            error_detail = "".join(tb_list)
        else:
            error_detail = "\n".join(err_values.args)

    return all_images_draw(plugin_name, error_msg, error_detail)

def parse_cron(cron_expr: str) -> dict:
    """解析cron表达式为调度器参数"""
    parts = cron_expr.split()
    if len(parts) != 5:
        raise ValueError("无效的cron表达式格式")
    return {
        "minute": parts[0],
        "hour": parts[1],
        "day": parts[2],
        "month": parts[3],
        "day_of_week": parts[4]
    }

def setup_scheduler():
    """初始化定时任务"""
    if error_config.enable_scheduled_report:
        try:
            global scheduler
            from nonebot import require
            require("nonebot_plugin_apscheduler")
            from nonebot_plugin_apscheduler import scheduler as _scheduler
            scheduler = _scheduler
            if error_config.report_mode == "time":
                scheduler.add_job(
                    scheduled_error_report,
                    "cron",
                    **parse_cron(error_config.report_interval),
                    id="error_report_scheduled"
                )
                logger.success("已启用定时发送错误报告")   
            if error_config.report_mode == "count":
                scheduler.add_job(
                    check_error_count,
                    "interval",
                    minutes=1,
                    id="error_report_count"
                )
                logger.success("已启用错误数量监控")
        except ImportError:
            logger.warning("未安装 nonebot_plugin_apscheduler，定时发送功能将不可用")
            return
        except Exception as e:
            logger.error(f"初始化定时任务失败: {str(e)}")
            return

async def scheduled_error_report():
    """定时发送错误报告"""
    if not scheduler:
        return
    try:
        unsent_errors = error_cache.get_unsent_errors()
        if not unsent_errors:
            logger.debug("没有需要发送的错误记录")
            return
        success = await send_batch_error_report(unsent_errors)
        if success:
            error_cache.mark_sent([error["id"] for error in unsent_errors])
            logger.info(f"定时任务: 已发送{len(unsent_errors)}条错误报告")
            if error_config.clear_after_report:
                #TODO: 清空错误记录
                return
        else:
            logger.error("定时发送错误报告失败")
    except Exception as e:
        logger.error(f"定时发送错误报告时发生异常: {str(e)}")

async def check_error_count():
    """检查错误数量是否达到发送阈值"""
    if not scheduler:
        return
    try:
        unsent_errors = error_cache.get_unsent_errors()
        if len(unsent_errors) >= error_config.report_count:
            await send_batch_error_report(unsent_errors)
            error_cache.mark_sent([error["id"] for error in unsent_errors])
            logger.info(f"已发送{len(unsent_errors)}条错误报告")
            if error_config.clear_after_report:
                #TODO: 清空错误记录
                return
    except Exception as e:
        logger.error(f"检查错误数量时发生异常: {str(e)}")

setup_scheduler()