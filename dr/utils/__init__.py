class lazystr:
    def __init__(self, o):
        self.o = o

    def __str__(self):
        return str(self.o)


class lazycall:
    def __init__(self, callable):
        self.callable = callable

    def __str__(self):
        return self.callable()


class dump_path:
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return '->'.join([t.content for t in reversed(self.path)])
