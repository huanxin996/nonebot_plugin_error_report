import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nonebot_plugin_error_report",
    version="0.1.0",
    author="huanxin996",
    author_email="mc.xiaolang@foxmail.com",
    description="基于nonebot的报错处理插件，支持图片/文字发送、数据库存储及跨平台",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/huanxin996/nonebot_plugin_error_report",
    packages=setuptools.find_packages(),
    install_requires=[
        'nonebot2>=2.3.0,<3.0.0',
        'nonebot_plugin_alconna>=0.54.0',
        'nonebot_plugin_tortoise_orm>=0.1.0,<0.2.0',
        'nonebot_plugin_userinfo>=0.2.0,<0.3.0',
        'nonebot_plugin_apscheduler>=0.3.0,<0.6.0',
        'pillow>=9.0.0,<12.0.0',
        'aiosmtplib>=2.0.0,<5.0.0',
        'aiohttp>=3.0.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)