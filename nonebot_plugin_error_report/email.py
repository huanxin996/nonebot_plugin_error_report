import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, List, Union, Dict
from nonebot.log import logger
from .config import error_config
from .model import ErrorReportBase

async def create_error_email(
    error_records: Union[Dict, List[Dict], ErrorReportBase, List[ErrorReportBase]],
    subject: Optional[str] = None
) -> MIMEMultipart:
    """创建错误报告邮件"""
    msg = MIMEMultipart()
    if not isinstance(error_records, list):
        error_records = [error_records]
    html_content = f"""
    <html>
    <body>
    <h2>错误报告 - {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</h2>
    <hr>
    """
    
    for record in error_records:
        if isinstance(record, dict):
            record_id = record.get('id')
            record_time = record.get('time')
            if isinstance(record_time, str):
                try:
                    record_time = datetime.strptime(record_time, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    record_time = datetime.now()
            plugin_name = record.get('plugin_name', '未知')
            user_id = record.get('user_id', '未知')
            bot_id = record.get('bot_id', '未知')
            error_type = record.get('error_type', '未知')
            error_msg = record.get('error_msg', '未知')
            error_detail = record.get('error_detail')
        else:
            record_id = record.id
            record_time = record.time
            plugin_name = record.plugin_name
            user_id = record.user_id
            bot_id = record.bot_id
            error_type = record.error_type
            error_msg = record.error_msg
            error_detail = record.error_detail

        html_content += f"""
        <div style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
            <p><strong>错误ID:</strong> {record_id}</p>
            <p><strong>时间:</strong> {record_time.strftime('%Y年%m月%d日 %H:%M:%S')}</p>
            <p><strong>插件:</strong> {plugin_name}</p>
            <p><strong>用户ID:</strong> {user_id}</p>
            <p><strong>机器人ID:</strong> {bot_id}</p>
            <p><strong>错误类型:</strong> {error_type}</p>
            <p><strong>错误信息:</strong> {error_msg}</p>
            {"<p><strong>详细信息:</strong><br><pre>" + error_detail + "</pre></p>" if error_detail else ""}
            <hr>
        </div>
        """
    html_content += "</body></html>"
    msg['Subject'] = subject or f"机器人错误报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    msg['From'] = error_config.email_from
    msg['To'] = ', '.join(error_config.email_to)
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    return msg

async def send_error_email(
    records: Union[ErrorReportBase, List[ErrorReportBase]],
    subject: Optional[str] = None
) -> bool:
    """发送错误报告邮件"""
    if not error_config.enable_email:
        logger.debug("邮件通知功能未启用")
        return False
    try:
        msg = await create_error_email(records, subject)
        if error_config.smtp_port == 465:
            smtp = aiosmtplib.SMTP(
                hostname=error_config.smtp_host,
                port=error_config.smtp_port,
                use_tls=True,
                tls_context=True
            )
        else:
            smtp = aiosmtplib.SMTP(
                hostname=error_config.smtp_host,
                port=error_config.smtp_port
            )
        
        try:
            await smtp.connect()
            if error_config.smtp_port == 587:
                await smtp.starttls()
            await smtp.login(error_config.smtp_user, error_config.smtp_password)
            await smtp.send_message(msg)
        finally:
            try:
                await smtp.quit()
            except:
                pass
        logger.info(f"错误报告邮件已发送至 {', '.join(error_config.email_to)}")
        return True
    except Exception as e:
        logger.error(f"发送错误报告邮件失败: {str(e)}")
        return False

async def send_batch_error_report(error_records: List[Dict]) -> bool:
    """批量发送错误报告"""
    if not error_records:
        logger.debug("没有需要发送的错误记录")
        return True
    if not error_config.enable_email:
        logger.debug("邮件通知功能未启用")
        return False
    try:
        total = len(error_records)
        batch_size = error_config.email_batch_size
        success = True
        for i in range(0, total, batch_size):
            batch = error_records[i:i + batch_size]
            subject = f"机器人错误报告 ({i+1}-{min(i+batch_size, total)}/{total})"
            if await send_error_email(batch, subject):
                logger.info(f"成功发送第 {i+1}-{min(i+batch_size, total)} 批错误报告")
            else:
                success = False
                logger.error(f"发送第 {i+1}-{min(i+batch_size, total)} 批错误报告失败")
                break
        return success
    except Exception as e:
        logger.error(f"批量发送错误报告失败: {str(e)}")
        return False