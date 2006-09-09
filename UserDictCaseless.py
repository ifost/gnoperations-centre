# A more or less complete user-defined wrapper around dictionary objects,  only the keys have to
# be strings,  and are converted to upper case on use

from string import upper
up = upper

class UserDictCaseless:
    def __init__(self, dict=None):
        self.data = {}
        if dict is not None: self.update(dict)
    def __repr__(self): return repr(self.data)
    def __cmp__(self, dict):
        if isinstance(dict, UserDictCaseless):
            return cmp(self.data, dict.data)
        else:
            return cmp(self.data, dict)
    def __len__(self): return len(self.data)
    def __getitem__(self, key): return self.data[up(key)]
    def __setitem__(self, key, item): self.data[up(key)] = item
    def __delitem__(self, key): del self.data[up(key)]
    def clear(self): self.data.clear()
    def copy(self):
        if self.__class__ is UserDictCaseless:
            return UserDictCaseless(self.data)
        import copy
        return copy.copy(self)
    def keys(self): return self.data.keys()
    def items(self): return self.data.items()
    def values(self): return self.data.values()
    def has_key(self, key): return self.data.has_key(up(key))
    def update(self, dict):
        for k, v in dict.items():
            self.data[up(k)] = v
    def get(self, key, failobj=None):
        return self.data.get(up(key), failobj)
