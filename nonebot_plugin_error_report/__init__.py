import traceback,datetime,sys
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Event
from nonebot import require
from nonebot.message import run_postprocessor
require("nonebot_plugin_userinfo")
require("nonebot_plugin_alconna")
from nonebot_plugin_userinfo import EventUserInfo, UserInfo, BotUserInfo
from nonebot_plugin_alconna import on_alconna,Alconna, Args, Option, CommandMeta,Arparma
from nonebot_plugin_alconna.uniseg import UniMessage,MsgTarget
from .config import Config,BotRunTimeError
from .model import ErrorReport
from .toimg import all_images_draw
from nonebot.log import logger


__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-animepush",
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
    homepage="https://github.com/none",
    config=Config,
    supported_adapters=None,
)


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
        keyword = result.query[str]("查找.关键词")
        value = result.query[str]("查找.vaule")
        try:
            records = await ErrorReport.filter(keyword=value).limit(10)
            if not records:
                await UniMessage.text(f"未找到包含关键词{keyword}的错误记录").send(target)
                return
            result_text = "搜索结果：\n" + "\n".join(
                f"ID: {r.id}\n时间: {r.time.strftime('%Y年%m月%d日 %H:%M:%S')}\n用户: {r.user_id}\n错误: {r.error_msg[:50]}...\n{'-'*20}"
                for r in records
            )
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
                f"错误: {record.error_msg}"
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
async def post_run(event: Event, e: Exception, target: MsgTarget, bot_info: UserInfo = BotUserInfo(), user_info: UserInfo = EventUserInfo()) -> None:
    try:
        img = await error_to_images(e)
    except BotRunTimeError:
        logger.warning("尝试制作错误报告失败，尝试使用文字发送")
        img = None
    try:
        await update_or_create(
            user_id=user_info.user_id,
            bot_id=bot_info.user_id,
            session_id=event.get_session_id(),
            message=event.get_message(),
            error_msg=str(e),
            time=datetime.datetime.now()
        )
        if img:
            await UniMessage.image(raw=img).send(target=target)
        else:
            error_msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
            result = f"抱歉，我出现了一点问题，请尝试使用其他指令，或者联系开发者\n以下是错误信息:\n{error_msg}"
            await UniMessage.text(result).send(target=target)
    except:
        raise BotRunTimeError("遇到未知错误,请自行扒拉日志!")


async def update_or_create(**kwargs) -> bool:
    try:
        total_count = await ErrorReport.all().count()
        id = total_count + 1
        _, created = await ErrorReport.update_or_create(id=id,**kwargs)
        return created
    except BotRunTimeError:
        return False

async def error_to_images(err_values: Exception = None) -> bytes:
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

    return all_images_draw(error_msg, error_detail)