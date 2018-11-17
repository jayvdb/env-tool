backup_win_env 是一个备份 Windows 系统用户环境变量的工具.

# 安装

## 从 Pypi 下载

```sh
pip install backup_win_env --user
```

## 从源码安装

```sh
git clone https://github.com/zombie110year/backup_win_env.git
cd backup_win_env
python setup.py install
```

# 使用

## 命令行工具

提供了 `backupUserEnv` 命令工具, 用于将用户变量导入/导出.

```
$> backupUserEnv -h

usage: backupWinEnv [-h] [-i xxx.yml] [-o yyy.yml] [-v]

导出/导入 用户环境变量到一个 YAML 文件中. 需要在 管理员权限下运行!

optional arguments:
  -h, --help            show this help message and exit
  -i xxx.yml, --import xxx.yml
                        从文件导入环境变量
  -o yyy.yml, --export yyy.yml
                        将变量导出至文件
  -v, --view            预览效果, 但不执行
```

## 导入模块

导入这个包, 使用 `utils` 下的类或函数, 详情见源码注释.
