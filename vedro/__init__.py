import sys
from district42 import SchemaType
from valeera import Validator, Formatter
from .core import TestRunner


def eq(self, other):
  validator = Validator(Formatter()).validate(other, self)
  if validator.fails():
    raise Exception('\n'.join(validator.errors()))
  return True

SchemaType.__eq__ = eq

def run():
  test_runner = TestRunner()
  test_runner.load_config()
  test_runner.create_init_files()
  test_runner.set_globals()
  test_runner.inject_variables()
  test_runner.load_scenarios()

  res = test_runner.run_scenarios()

  test_runner.remove_init_files()

  sys.exit(int(not res))
