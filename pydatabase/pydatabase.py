class Table:

    def __new__(cls, *args, **ignore_kwargs):
        if not hasattr(cls, '__instances__'):
            cls.__instances__ = set()
        inst = super().__new__(cls, *args)
        cls.__instances__.add(inst)
        return inst

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


class Column:

    def __init__(self):
        self.instance_values = {}

    def __get__(self, instance, cls=None):
        if instance:
            return self.instance_values[instance]
        return self

    def __set__(self, instance, value):
        self.instance_values[instance] = value
