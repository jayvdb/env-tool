import argparse
import pathlib
from .utils import importUserEnvReg, exportUserEnvReg


def parseArgs():

    DESCRIPTION = \
        """
    导出/导入 用户环境变量到一个 YAML 文件中.
    需要在 管理员权限下运行!
    """

    parser = argparse.ArgumentParser(
        prog="backupWinEnv",
        description=DESCRIPTION,
        argument_default=None,
    )
    parser.add_argument("-i", "--import", dest="input",
                        required=False, metavar="xxx.yml", help="从文件导入环境变量")
    parser.add_argument("-o", "--export", dest="output",
                        required=False, metavar="yyy.yml", help="将变量导出至文件")
    parser.add_argument("-v", "--view",   dest="view",   required=False,
                        default=False, action="store_true", help="预览效果, 但不执行")
    args = parser.parse_args()

    if args.input != None and args.output == None:
        args.INPUT_not_OUTPUT = True
        args.input = str(pathlib.Path(args.input).absolute())
    elif args.output != None and args.input == None:
        args.INPUT_not_OUTPUT = False
        args.output = str(pathlib.Path(args.output).absolute())
    else:
        raise ValueError("必须在 import, export 两个参数中选择唯一一个")

    return args


def main():

    args = parseArgs()

    if args.INPUT_not_OUTPUT:
        importUserEnvReg(args.input, args.view)
    else:
        exportUserEnvReg(args.output, args.view)
    return 0
