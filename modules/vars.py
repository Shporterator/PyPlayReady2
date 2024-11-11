from typing import List, Optional, Union

class Vars:
    VAR_INT = 0x01
    VAR_STR = 0x02
    MAXVARNAME = 20
    UNKNOWN_VAL = -1

    class Proto:
        def __init__(self, name: str, var_type: int):
            self._name = name
            self._type = var_type

        def name(self) -> str:
            return self._name

        def type(self) -> int:
            return self._type

    class Var:
        def __init__(self, proto: 'Vars.Proto', val: Optional[Union[int, str]] = None):
            self._proto = proto
            self._val = val

        def proto(self) -> 'Vars.Proto':
            return self._proto

        def val(self) -> Optional[Union[int, str]]:
            return self._val

        def set(self, val: Union[int, str]):
            self._val = val

    _vars: List['Vars.Var'] = []

    @classmethod
    def get_var(cls, name: str) -> Optional['Vars.Var']:
        for var in cls._vars:
            if var.proto().name() == name:
                return var
        return None

    @classmethod
    def known_var(cls, name: str) -> bool:
        return cls.get_var(name) is not None

    @staticmethod
    def str2type(s: str) -> int:
        if s == "int":
            return Vars.VAR_INT
        elif s == "str":
            return Vars.VAR_STR
        else:
            return -1

    @classmethod
    def declare(cls, name: str, stype: str):
        if cls.known_var(name):
            print(f"error: {name} is already defined")  # Assuming Shell.println()
        else:
            var_type = cls.str2type(stype)
            if var_type == -1:
                print(f"error: unknown type {stype}")  # Assuming Shell.println()
            else:
                proto = cls.Proto(name, var_type)
                cls._vars.append(cls.Var(proto))

    @classmethod
    def declare_proto(cls, proto: 'Vars.Proto'):
        if not cls.known_var(proto.name()):
            cls._vars.append(cls.Var(proto))

    @classmethod
    def set(cls, name: str, val: Union[int, str]):
        if not cls.known_var(name):
            var_type = Vars.VAR_INT if isinstance(val, int) else Vars.VAR_STR
            cls.declare_proto(cls.Proto(name, var_type))
        var = cls.get_var(name)
        if var:
            var.set(val)

    @classmethod
    def clear(cls, name: str):
        var = cls.get_var(name)
        if var:
            var.set(None)

    @classmethod
    def get_int(cls, name_or_var: Union[str, 'Vars.Var']) -> int:
        if isinstance(name_or_var, str):
            var = cls.get_var(name_or_var)
        else:
            var = name_or_var
        return int(var.val()) if var and isinstance(var.val(), int) else Vars.UNKNOWN_VAL

    @classmethod
    def get_str(cls, name_or_var: Union[str, 'Vars.Var']) -> str:
        if isinstance(name_or_var, str):
            var = cls.get_var(name_or_var)
        else:
            var = name_or_var
        return str(var.val()) if var and isinstance(var.val(), str) else "<not set>"

    @classmethod
    def print_vars(cls):
        for var in cls._vars:
            proto = var.proto()
            var_name = proto.name()
            val_str = ""
            if var.val() is not None:
                if proto.type() == cls.VAR_INT:
                    val_str = f"{Utils.hex_value(cls.get_int(var), 8)}"
                elif proto.type() == cls.VAR_STR:
                    val_str = f"\"{cls.get_str(var)}\""
            else:
                val_str = "<not set>"
            output_line = f"{Utils.padded_string(f'- {var_name}', cls.MAXVARNAME)} = {val_str}"
            print(output_line)  # Assuming Shell.println()
