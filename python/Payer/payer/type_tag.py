class TypeTag(object):
    def __init__(self, name): self.name = name;
    def __str__(self): return self.name;
    def __repr__(self): return self.name;
    def __call__(self, *args): return (self,) + tuple(args);

