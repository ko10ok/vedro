from configparser import ConfigParser, ExtendedInterpolation


class Config:

  _main_namespace = 'main'

  def __init__(self):
    self._parser = None

  def read(self, ini_path):
    self._parser = ConfigParser(interpolation=ExtendedInterpolation())
    self._parser.read(ini_path)
    return self

  def keys(self):
    return self._parser[self._main_namespace].keys()

  def __getitem__(self, key):
    return self.__getattr__(key)

  def __getattr__(self, name):
    if name in self._parser:
      return self._parser[name]
    if name in self._parser[self._main_namespace]:
      return self._parser[self._main_namespace][name]
    raise KeyError()
