<!-- markdownlint-disable MD033 MD036 MD041 -->

<p align="center">
  <a href="https://huanxinbot.com/"><img src="https://raw.githubusercontent.com/huanxin996/nonebot_plugin_hx-yinying/main/.venv/hx_img.png" width="200" height="200" alt="这里放一张oc饭🤤"></a>
</p>

<div align="center">

# NoneBot 错误管理插件

_✨ 智能记录并可视化机器人运行时的错误信息 ✨_

</div>

> [!note]
> 如有建议或错误，请提交 issue。\
> 本人代码水平很烂，将就着用罢()

## 📝 插件介绍

这是一个基于 NoneBot2 的错误处理插件，提供以下功能：

- 实时捕获并绘制错误详细信息为图片
- 支持错误信息的持久化存储与管理
- 多样化的错误查询与统计功能
- 支持多平台适配

## 🎯 功能特点

- 自动将错误信息转换为图片发送(失败时自动切换为文本模式)
- 支持错误信息的数据库存储
- 提供丰富的错误管理命令
- 基于 nonebot-plugin-userinfo 获取用户信息
- 使用 nonebot_plugin_alconna 提供优雅的命令交互

## 💿 安装方式

```bash
pip install nonebot-plugin-error-manager
```

```bash
nb plugin install nonebot_plugin_error_manager
```

## ⚙️ 配置说明

### 基础配置

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|--------|-----|
| error_image_quality | int | 30 | 错误图片渲染质量(1-100) |
| error_image_font | str | None | 错误图片字体文件路径 |
| enable_error_report | bool | True | 是否启用错误记录功能 |
| use_orm_database | bool | True | 是否使用数据库存储(False则使用JSON文件) |

### 邮件通知配置

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|--------|-----|
| enable_email | bool | False | 是否启用邮件通知 |
| smtp_host | str | "smtp.qq.com" | SMTP服务器地址 |
| smtp_port | int | 465 | SMTP服务器端口 |
| smtp_ssl | bool | True | 是否使用SSL连接 |
| smtp_user | str | "" | SMTP用户名 |
| smtp_password | str | "" | SMTP密码或授权码 |
| email_from | str | "" | 发件人邮箱 |
| email_to | list[str] | [] | 收件人邮箱列表 |

### 定时报告配置

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|--------|-----|
| enable_scheduled_report | bool | False | 是否启用定时报告 |
| report_mode | str | "count" | 触发模式: count(累计触发)/time(定时触发) |
| report_count | int | 10 | 累计错误触发阈值(count模式) |
| report_interval | str | "0 0 `*` `*` `*`" | 定时发送cron表达式(time模式) |
| clear_after_report | bool | False | 发送后是否清空记录 |

### 错误过滤配置

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|--------|-----|
| ignored_plugins | list[str] | [] | 忽略的插件列表 |
| ignore_patterns | list[str] | [] | 忽略的错误模式 |

### 配置示例

```python
error_manager_config = {
    # 基础配置
    "error_image_quality": 50,
    "error_image_font": "C:/Windows/Fonts/msyh.ttc",
    
    # 邮件配置
    "enable_email": True,
    "smtp_user": "your_email@qq.com",
    "smtp_password": "your_password",
    "email_to": ["admin@example.com"],
    
    # 定时报告
    "enable_scheduled_report": True,
    "report_mode": "time",
    "report_interval": "0 0 * * *",
    
    # 错误过滤
    "ignored_plugins": ["plugin1", "plugin2"],
    "ignore_patterns": ["*timeout*", "*connection refused*"]
}
```

## 🎮 使用方法

### 基础命令

- `/错误管理 查看 [页数]` - 分页查看错误记录
- `/错误管理 详情 [id]` - 查看指定ID的错误详情
- `/错误管理 删除 [id]` - 删除指定ID的错误记录
- `/错误管理 统计` - 查看错误统计信息

### 高级查询

- `/错误管理 查找 <字段名> <值>` - 精确查找错误记录
- `/错误管理 搜索 <关键词>` - 模糊搜索错误记录
- `/错误管理 清空 <类型> <值>` - 批量清理错误记录
  - 类型：all/user/bot/date
  - 值：all/用户ID/机器人ID/日期

### 别名支持

支持使用 `错误` 或 `err` 作为命令别名。

### 自定义引入方法

```python
from nonebot_plugin_error_manager import error_to_images

try:
  #代码内容
except Exception as e:
  img = error_to_images(e)
  #这里填你发送图片的方法
```

## 📑 开发计划

### 已完成功能

- ✅ 邮件通知系统
  - 支持定时发送错误报告
  - 支持实时错误通知推送
- ✅ 错误信息增强
  - 优化依赖注入机制
  - 扩展错误信息采集范围
  - 优化发送错误信息的显示
- ✅ 跨平台兼容性
  - 支持主流聊天平台错误推送
  - 统一错误处理接口
- ✅ 报错处理增强
  - 忽略指定插件的报错
  - 忽略指定报错类型

### 进行中功能

- 🚧 数据存储优化
  - ORM数据库动态加载/卸载
  - JSON文件导入导出支持
  - 数据迁移工具开发

### 计划中功能

- 📋 代码重构与优化
  - 性能优化
  - 代码结构重组
  - 测试覆盖率提升
  - 错误信息格式优化
  - 尝试使用ai来处理错误信息
  - 尝试自动化运维
- 📋 平台适配扩展
  - 新增平台支持
  - 统一适配器接口

## 📸 效果展示

<img src="https://raw.githubusercontent.com/huanxin996/nonebot_plugin_error_report/main/example_image/test0.png" alt="示例图片-1">
<img src="https://raw.githubusercontent.com/huanxin996/nonebot_plugin_error_report/main/example_image/test1.jpg" alt="示例图片-2">
<img src="https://raw.githubusercontent.com/huanxin996/nonebot_plugin_error_report/main/example_image/test2.jpg" alt="示例图片-3">
<img src="https://raw.githubusercontent.com/huanxin996/nonebot_plugin_error_report/main/example_image/test3.jpg" alt="示例图片-4">
<img src="https://raw.githubusercontent.com/huanxin996/nonebot_plugin_error_report/main/example_image/test4.jpg" alt="示例图片-5">
<img src="https://raw.githubusercontent.com/huanxin996/nonebot_plugin_error_report/main/example_image/test5.jpg" alt="示例图片-6">
<img src="https://raw.githubusercontent.com/huanxin996/nonebot_plugin_error_report/main/example_image/test6.jpg" alt="示例图片-7">
<img src="https://raw.githubusercontent.com/huanxin996/nonebot_plugin_error_report/main/example_image/test7.jpg" alt="示例图片-8">

## 🙏 鸣谢

- [nonebot-plugin-userinfo](https://github.com/none)
- [nonebot_plugin_alconna](https://github.com/none)
- [NoneBot2](https://github.com/nonebot/nonebot2)

## 📄 开源协议

MIT License

Copyright (c) 2025 huanxin996

## 📄 更新日志

### v0.0.2 (2025-03-27)

#### ✨ 新特性

- 新增邮件通知功能
  - 支持错误报告邮件推送
  - 可配置邮件发送触发条件
  - 自定义邮件模板支持
- 新增更好的配置项
  - 指定忽略错误类型
  - 指定忽略错误插件

#### 🔧 优化

- 改进错误信息显示格式
  - 添加报错插件名称
  - 优化堆栈信息可读性
  - 增加错误上下文展示
  - 新增更详细的错误信息存储格式
- 完善配置项说明文档

#### 🐛 修复

- 修复图片生成失败时的异常处理

### v0.0.1 (2025-03-26)

#### 🎉 初始发布

- 实现基础错误捕获功能
- 支持错误信息图片化展示
- 添加基本的错误管理命令
- 完成数据库存储功能
