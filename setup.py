import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nonebot_plugin_error_report",
    version="0.0.4",
    author="huanxin996",
    author_email="mc.xiaolang@foxmail.com",
    description="基于nonebot的报错处理插件，支持图片/文字发送、数据库存储及跨平台",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/huanxin996/nonebot_plugin_error_report",
    packages=setuptools.find_packages(),
    install_requires=['nonebot_plugin_alconna<=0.56.2','nonebot_plugin_tortoise_orm<=0.1.4','nonebot_plugin_userinfo<=0.2.6', 'nonebot_plugin_apscheduler<=0.5.0','pillow<=11.1.0', 'aiosmtplib<=4.0.0'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)