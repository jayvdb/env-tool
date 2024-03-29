"""
.. module:: envtool.utils
    :platform: Windows
    :synopsis: Python 与 Windows NT 系统注册表中 "Environment" 项的交互.

.. moduleauthor:: Zombie110year <zombie110year@outlook.com>

.. class:: RegValue

    是注册表项中一组 键值 对应的 Python Object

.. class:: RegItem

    是注册表中一个 项 对应的 Python Object
"""

import winreg

import yaml

gUSER_ENV_REG_KEY = (winreg.HKEY_CURRENT_USER, "Environment")


class RegValue:
    """这个类的作用在于定义注册表中一个 **键** 的行为.

    注册表中的键值有 ``name`` , ``value`` , ``type_`` 三个属性.
    都保存为 :mod:`winreg` 模块能直接使用的数据类型.
    除此之外, 还有便于 Python 操作而设置的其他属性.

    :param name: 键名
    :param value: 键值, 必须是一个元组, 根据其中值的个数与类型有不同的处理方式
    :param type_: 键注册表类型
    :param sep: 多值键的分隔符, 默认为 ; 分号
    :param multi_value: 判断是否为多值键, 影响到 :method update: 的处理方法
    :type name: str
    :type value: tuple
    :type type_: str
    :type sep: str
    :type multi_value: bool, True or False

    对 ``value`` 的处理
        1. 若 value 中只有一个元素, 那么判断该组键值为单值键, 若更新时传入了同名键
        值, 将会被覆盖.
        2. 若 value 中有多个元组, 那么更新时传入了同名键值, 将会合并.
        3. 若 value 为字符串构成, 那么每一项在写入实际注册表前, 会用 ; 号合并

    在 Python 程序运行时, 所有数据都是便于 Python 操作的类型, 只有在写入实际注册
    表前转换. 例如

    - ``value`` 是一个列表, 就算里面只有一个元素
    - ``type_`` 是一个字符串, 而不是 winreg.REG_TYPE 对应的整数值.

    转换后格式为 ``(name, value, type)``

    关于注册表的参考文档

    https://docs.microsoft.com/en-us/windows/desktop/SysInfo/registry-value-types
    """
    REG_TYPE = {
        winreg.REG_BINARY: "REG_BINARY",
        winreg.REG_DWORD: "REG_DWORD",
        winreg.REG_DWORD_BIG_ENDIAN: "REG_DWORD_BIG_ENDIAN",
        winreg.REG_DWORD_LITTLE_ENDIAN: "REG_DWORD_LITTLE_ENDIAN",
        winreg.REG_EXPAND_SZ: "REG_EXPAND_SZ",
        winreg.REG_LINK: "REG_LINK",
        winreg.REG_MULTI_SZ: "REG_MULTI_SZ",
        winreg.REG_NONE: "REG_NONE",
        winreg.REG_QWORD: "REG_QWORD",
        winreg.REG_QWORD_LITTLE_ENDIAN: "REG_QWORD_LITTLE_ENDIAN",
        winreg.REG_SZ: "REG_SZ",
    }
    REG_TYPE_R = {
        "REG_BINARY": winreg.REG_BINARY,
        "REG_DWORD": winreg.REG_DWORD,
        "REG_DWORD_BIG_ENDIAN": winreg.REG_DWORD_BIG_ENDIAN,
        "REG_DWORD_LITTLE_ENDIAN": winreg.REG_DWORD_LITTLE_ENDIAN,
        "REG_EXPAND_SZ": winreg.REG_EXPAND_SZ,
        "REG_LINK": winreg.REG_LINK,
        "REG_MULTI_SZ": winreg.REG_MULTI_SZ,
        "REG_NONE": winreg.REG_NONE,
        "REG_QWORD": winreg.REG_QWORD,
        "REG_QWORD_LITTLE_ENDIAN": winreg.REG_QWORD_LITTLE_ENDIAN,
        "REG_SZ": winreg.REG_SZ,
    }

    def __init__(self, name=None, value=None, type_=None, sep=';', multi_value=False):
        self.name = name
        self.value = value
        self.type_ = type_
        self.sep = sep
        self.multi_value = multi_value

    def __repr__(self):
        return "RegValue({}, {}, {})".format(self.name, self.value, self.type_)

    def transValue(self) -> tuple:
        """在设置了 ``name`` , ``value`` , ``type_`` 属性后转换为可通过 :mod:`winreg` 模块写入到注册表的形式,
        在写入注册表之前运行.

        :return: ``(self.name, true_value, RegValue.REG_TYPE_R[self.type_])``
        :rtype: tuple
        """
        if self.type_ in ("REG_SZ", "REG_EXPAND_SZ", "REG_MULTI_SZ"):
            true_value = ";".join(self.value)
        else:
            true_value = self.value[0]

        return (self.name, true_value, RegValue.REG_TYPE_R.get(self.type_))

    def wrap(self):
        """将 Reg Obj 转化为 Python Obj, 在读取注册表后立刻运行

        1. 处理 ``value`` , 若 ``value`` 为一个字符串, 则用 ``sep`` 分割, 若为其他值, 则转化为列表.
        2. 将 ``type_`` 由整数 Flag 翻译为对应符号名

        :return: ``self``
        :rtype: ``RegValue``
        """

        if self.type_ in (
            self.REG_TYPE_R.get("REG_SZ"),
            self.REG_TYPE_R.get("REG_EXPAND_SZ"),
            self.REG_TYPE_R.get("REG_MULTI_SZ"),
        ):
            values = self.value.split(";")
        else:
            values = [self.value]
        self.type_ = RegValue.REG_TYPE.get(self.type_)
        self.value = values
        return self

    def packYAML(self) -> tuple:
        """
        将自身打包成 YAML 所需的元组, 和 :method transValue: 不一样, 这个返回的
        ``type_`` 是可读的字符串.

        :return: ``(self.name, self.value, self.type_)``
        """
        return self.name, self.value, self.type_

    def unpackYAML(self, input_: (list, tuple)):
        """
        ``input_: [name, value, type]``
            ``value: ["value1", "value2", ...]``

        处理由 YAML 读入的数据, 将其转化为 Python Obj.

        :param input_: 被解析为 RegValue 的一个列表或元组, 需要按照
            (name, values:list, type:str) 的格式组织;
            type 是在 REG_TYPE 字典中的字符串.
        :type input_: tuple or list

        :return: 返回解析完成的 RegValue 实例
        :rtype: ``RegValue``
        """
        self.name = input_[0]
        self.value = input_[1]
        self.type_ = input_[2]
        return self

    def update(self, other):
        """合并 other 或被覆写

        :param other: 另一个 RegValue 实例
        """
        if self.multi_value:
            value = set(self.value)
            value.update(set(other.value))
            self.value = list(value)
        else:
            self.value = other.value


class RegItem:
    """
    注册表项, 项之下可能有子项, 当前项可能有多个键值.

    :param name: 该注册表项的名称.

    其他属性不应在初始化时定义:

    - ``child_item`` 该注册表项目的子项, 类似目录树的结构.
    - ``parent`` 该注册表项目的亲项.
    - ``values`` 该注册表下的值, 是一个字典, 按照 ``value_name: value`` 的形式存储. 其中的每一个元素都是 RegValue 实例
    """
    NAME_KEY = {
        "Environment": winreg.HKEY_CURRENT_USER
    }

    def __init__(self, name):
        self.name = name
        self.child_item = []
        self.parent = None
        self.values = dict()
        self.key = RegItem.NAME_KEY.get(self.name, winreg.HKEY_CURRENT_USER)

    def __str__(self):
        output = ["--Name--------Value-------------Type"]
        for i in self.values:
            output.append(str(self.values.get(i)))
        return "\n".join(output)

    def updateValue(self, reg_value):
        """
        在 self.values:dict 中添加一个 RegValue 实例

        :param reg_value: 一个 RegValue 实例.

        处理方式
            1. 若 self.values 中无该组键值, 则直接添加
            2. 若 self.values 中有该组键值, 且为单值键, 则覆盖
            3. 若 self.values 中有该组键值, 且为多值键, 则合并

        参考文档

        https://docs.microsoft.com/en-us/windows/desktop/SysInfo/registry-value-types
        """
        if reg_value.name not in self.values:
            self.values[reg_value.name] = reg_value
        else:
            self.values[reg_value.name].update(reg_value)

    def getValue(self):
        """一个获取所有 self.values 元素的生成器(Generator)

        :return: ``self.values`` 中的一项.
        """
        for i in self.values:
            yield self.values.get(i)

    def toYAML(self, path: str):
        """
        将本 RegItem 实例导出到 path 所指的 .yml 文件中

        :param path: .yml 文件路径
        :type path: str
        """
        package = [value.packYAML() for value in self.getValue()]
        # content = StringIO()
        # file.write(content)  # todo: 格式美化, 列表中每一项单行输出
        with open(path, "wt", encoding="utf-8") as file:
            yaml.dump(package, file)

    def fromYAML(self, path: str):
        """从 .yml 文件中导入, 文本格式参考导出内容

        :param path: .yml 文件路径
        :type path: str
        """
        with open(path, "rt", encoding="utf-8") as file:
            package = yaml.load(file)
        for _ in package:
            reg_value = RegValue().unpackYAML(_)
            self.updateValue(reg_value)

    def update(self, other):
        """
        将自身与另一个注册表项合并

        :param other: 另一个注册表项, 需要名称相同
        :type other: RegItem
        """
        if isinstance(other, RegItem) and self.name == other.name:
            for value in other.getValue():
                self.updateValue(value)
        else:
            raise TypeError("self other 不是同一个注册表")

    def updateReg(self):
        """
        将自身与实际注册表合并
        """
        reality = RegItem(self.name)
        self.update(reality)

    def toReg(self):
        """
        将自身写入注册表
        """
        with winreg.OpenKeyEx(self.key, self.name, 0, winreg.KEY_SET_VALUE) as key:
            for item in self.getValue():
                name, value, type_ = item.transValue()
                winreg.SetValueEx(key, name, 0, type_, value)

    def readReg(self):
        """
        读取注册表项目
        """
        with winreg.OpenKeyEx(self.key, self.name, 0, winreg.KEY_READ) as key:
            _ = 0
            while True:
                try:
                    reg_value = RegValue(*winreg.EnumValue(key, _)).wrap()
                    self.updateValue(reg_value)
                    # EnumValue 返回 元组 (reg_name, reg_value, reg_type)
                    _ += 1
                except OSError:
                    break


def readUserEnvReg() -> RegItem:
    """
    读取当前用户的环境变量注册表项
    使用了全局变量 `gUSER_ENV_REG_KEY`

    :return: 名为 ``Environment`` 的 RegItem 实例.
    :rtype: RegItem
    """
    reg_environment = RegItem("Environment")
    reg_environment.readReg()
    return reg_environment


def writeUserEnvReg(objRegItem: RegItem):
    """更新注册表后写入
    使用了全局变量 ``gUSER_ENV_REG_KEY``
    """
    objRegItem.updateReg()
    objRegItem.toReg()


def emptyUserEnvReg():
    """.. danger:: 清空当前用户的环境变量注册表项!

    使用了全局变量 ``gUSER_ENV_REG_KEY``
    """
    with winreg.OpenKeyEx(*gUSER_ENV_REG_KEY, 0, winreg.KEY_SET_VALUE) as key:
        _ = 0
        while True:
            try:
                name, value, type_ = winreg.EnumValue(key, _)
                winreg.DeleteValue(key, "")
                _ += 1
            except OSError:
                break


def exportUserEnvReg(path: str, view: bool):
    """将用户变量的注册表导出至 path 所指的 .yml 文件

    :param path: .yml 文件路径
    :param view: 是否预览效果, 如果是, 则仅打印环境变量而不进行处理
    """
    env = readUserEnvReg()
    if not view:
        env.toYAML(path)
    else:
        print(env)


def importUserEnvReg(path: str, view: bool):
    """从 path 所指的 .yml 文件导入环境变量至用户变量的注册表

    :param path: .yml 文件路径
    :param view: 是否预览效果, 如果是, 则仅打印环境变量而不进行处理
    """
    env = RegItem("Environment")
    env.fromYAML(path)
    if not view:
        writeUserEnvReg(env)
    else:
        print(env)
