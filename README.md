<!-- markdownlint-disable MD033 MD036 MD041 -->

<p align="center">
  <a href="https://huanxinbot.com/"><img src="https://raw.githubusercontent.com/huanxin996/nonebot_plugin_hx-yinying/main/.venv/hx_img.png" width="200" height="200" alt="这里放一张oc饭🤤"></a>
</p>

<div align="center">

# NoneBot 错误管理插件

_✨ 智能记录并可视化机器人运行时的错误信息 ✨_

</div>

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

## 🎮 使用方法

### 配置详情

- error_image_quality - 错误图片绘制质量，默认为 30
- error_image_font - 错误图片字体，默认为 "Source Han Sans CN"

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

## 📸 效果展示

<img src="https://raw.githubusercontent.com/huanxin996/nonebot_plugin_error_report/main/such.png" alt="示例图片">

## 🙏 鸣谢

- [nonebot-plugin-userinfo](https://github.com/none)
- [nonebot_plugin_alconna](https://github.com/none)
- [NoneBot2](https://github.com/nonebot/nonebot2)

## 📄 开源协议

MIT License

Copyright (c) 2025 huanxin996
