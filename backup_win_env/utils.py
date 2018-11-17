import winreg
import yaml

gUSER_ENV_REG_KEY = (winreg.HKEY_CURRENT_USER, "Environment")

class RegValue:
    """
    注册表中的键值有 name, value, type 三个属性
    都保存为 winreg 模块能直接使用的数据类型

    # Para

    - `name` 键名
    - `value` 键值
    - `type`  键类型

    # 参考文档

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

    def __init__(self, name=None, value=None, type=None):
        """
        # Para

        - `name` 键名
        - `value` 键值
        - `type`  键类型

        # Reference

        https://docs.microsoft.com/en-us/windows/desktop/SysInfo/registry-value-types
        """
        self.name = name
        self.value = value
        self.type = type
    def __repr__(self):
        return "RegValue({}, {}, {})".format(self.name, self.value, RegValue.REG_TYPE[self.type])

    def wrap(self):
        """
        将有多个项的 value 值由被 分号 分隔的字符串转化为列表
        并将 type 由整数 Flag 翻译为对应符号名

        # 返回值

        (name, values:list, type:str) 元组
        """
        values = self.value.split(";")
        type_ = RegValue.REG_TYPE[self.type]
        return (self.name, values, type_)

    def unpack(self, input):
        """
        input: [name, value, type]
            value: ["value1", "value2", ...]

        # Para

        - `input` 被解析为 RegValue 的一个列表或元组, 需要按照
            (name, values:list, type:str) 的格式组织;
            type 是在 REG_TYPE 字典中的字符串.

        # Return

        返回解析完成的 RegValue 实例
        """
        self.name = input[0]
        self.value = ";".join(input[1])
        self.type = RegValue.REG_TYPE_R[input[2]]
        return self

class RegItem:
    """
    注册表项, 项之下可能有子项
    当前项有多个键值
    """
    def __init__(self, name):
        self.name = name
        self.child_item = None
        self.values = []
    def __repr__(self):
        output = ""
        for i in self.values:
            output += str(i) + "\n"
        return output

    def addValue(self, name, value, type):
        """
        在 self.values:list 中添加一个 RegValue 实例

        # Para

        - `name`  键名
        - `value` 键值
        - `type`  键类型

        # Reference

        https://docs.microsoft.com/en-us/windows/desktop/SysInfo/registry-value-types
        """
        self.values.append(RegValue(name, value, type))

    def toYAML(self, path):
        """
        将本 RegItem 实例导出到 path 所指的 .yml 文件中

        # Para

        - `path` .yml 文件路径
        """
        package = [value.wrap() for value in self.values]
        with open(path, "wt", encoding="utf-8") as file:
            yaml.dump(data=package, stream=file)
    
    def fromYAML(self, path):
        """
        从 .yml 文件中导入, 文本格式参考导出内容

        # Para

        - `path` .yml 文件路径
        """
        with open(path, "rt", encoding="utf-8") as file:
            package = yaml.load(file)
        self.values = []
        for _ in package:
            self.values.append(RegValue(*_))

def readUserEnvReg() -> RegItem:
    """
    读取当前用户的环境变量注册表项
    使用了全局变量 `gUSER_ENV_REG_KEY`

    # Return

    返回名为 `Environment` 的 RegItem 实例.
    """
    objRegItem = RegItem("Environment")
    with winreg.OpenKeyEx(*gUSER_ENV_REG_KEY) as key:
        _ = 0
        while True:
            try:
                objRegItem.addValue(*winreg.EnumValue(key, _))
                # EnumValue 返回 元组 (reg_name, reg_value, reg_type)
                _ +=1
            except OSError:
                break
    return objRegItem

def writeUserEnvReg(objRegItem:RegItem):
    """
    覆写当前用户的环境变量注册表项, 原有值将被清空!
    使用了全局变量 `gUSER_ENV_REG_KEY`
    """
    emptyUserEnvReg()
    with winreg.OpenKeyEx(*gUSER_ENV_REG_KEY) as key:
        for reg_value in objRegItem.values:
            winreg.SetValue(key, reg_value.name, reg_value.type, reg_value.value)

def emptyUserEnvReg():
    """
    清空当前用户的环境变量注册表项!
    使用了全局变量 `gUSER_ENV_REG_KEY`
    """
    with winreg.OpenKeyEx(*gUSER_ENV_REG_KEY) as key:
        _ = 0
        while True:
            try:
                name, value, type_ = winreg.EnumValue(key, _)
                winreg.DeleteValue(key, "")
                _ += 1
            except OSError:
                break

def exportUserEnvReg(path, view):
    """
    将用户变量的注册表导出至 path 所指的 .yml 文件

    # Para

    - `path` .yml 文件路径
    - `view` 是否预览效果, 如果是, 则仅打印环境变量而不进行处理
    """
    env = readUserEnvReg()
    if not view:
        env.toYAML(path)
    else:
        print(env)

def importUserEnvReg(path, view):
    """
    从 path 所指的 .yml 文件导入环境变量至用户变量的注册表

    # Para

    - `path` .yml 文件路径
    - `view` 是否预览效果, 如果是, 则仅打印环境变量而不进行处理
    """
    env = RegItem("Environment")
    env.fromYAML(path)
    if not view:
        writeUserEnvReg(env)
    else:
        print(env)
