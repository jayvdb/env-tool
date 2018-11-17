try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

NAME = "backup_win_env"
VERSION = "1.0.0"
AUTHOR = "Zombie110year"
EMAIL = "zombie110year@outlook.com"
URL = "https://github.com/zombie110year/backup_win_env"
DESCRIPTION = \
"""
使用 pywin32, pyyaml 包, 用于导入/导出用户环境变量

操作 Windows 系统的注册表, 导出的文本格式为 yaml
"""
LICENSE = open("LICENSE", "rt", encoding="utf-8").read()

setup(
    entry_points={
        "console_scripts":[
            "backupUserEnv = backup_win_env.__main__"
        ]
    },
    requires=[
        "pyyaml",
        "pywin32"
    ],
    packages=find_packages(),
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    description=".yml <-> User's Environment Variables in Windows register table",
    long_description=DESCRIPTION,
    url=URL,
    license=LICENSE,
    platforms=["win"]
)
