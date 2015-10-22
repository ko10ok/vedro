import builtins
import os
import sys
import inspect
import json
import traceback
import importlib
from colorama import Fore, Back, Style
from . import Config, Scope, Scenario, Profiler


class TestRunner:

  def __init__(self):
    self.init_files = []
    self.scenarios = []
    self.cfg = None

  def load_config(self):
    self.cfg = Config().read('config.ini')

  def set_globals(self):
    builtins.cfg = self.cfg
    builtins.dump = lambda obj: print(json.dumps(obj, ensure_ascii=False, indent=2))
    builtins.Scope = Scope

  def inject_variables(self):
    for path in ('schemas', 'repositories', 'helpers', 'contexts'):
      if not os.path.exists(path): continue
      for filename in os.listdir(path):
        if filename.startswith('_'): continue
        module = importlib.__import__(path + '.' + os.path.splitext(filename)[0])
        for variable in dir(module):
          if variable.startswith('_'): continue
          setattr(builtins, variable, getattr(module, variable))

  def create_init_files(self):
    for path in ('schemas', 'repositories', 'helpers', 'contexts'):
      if not os.path.exists(path): continue
      py_files = [filename for filename in os.listdir(path) if filename.endswith('.py')]
      if '__init__.py' in py_files: continue
      filename = os.path.join(path, '__init__.py')
      self.init_files += [filename]
      content = '\n'.join(['from .{} import *'.format(x[:-3]) for x in py_files])
      with open(filename, 'w') as init_file:
        init_file.write(content)

  def remove_init_files(self):
    for path in self.init_files:
      os.remove(path)

  def load_scenarios(self):
    for path, subdirs, files in os.walk('scenarios'):
      for filename in files:
        if path.endswith('_') or filename.startswith('_'): continue
        module_path = os.path.join(path, os.path.splitext(filename)[0])
        module = importlib.import_module(module_path.replace('/', '.'))
        for variable in dir(module):
          if not variable.endswith('scenario'): continue
          if variable.startswith('skip'): continue

          profiler = Profiler()
          profiler.register()
          try:
            getattr(module, variable)()
          finally:
            profiler.deregister()

          constants = getattr(module, variable).__code__.co_consts
          steps = [x.co_name for x in constants if inspect.iscode(x)]

          scope = Scope(profiler.get_locals())
          if variable.startswith('only'):
            self.scenarios = [Scenario(scope.subject, steps, scope)]
            return None
          self.scenarios += [Scenario(scope.subject, steps, scope)]

  def run_scenarios(self):
    print(Style.BRIGHT + cfg.app_name + Style.NORMAL)

    passed_scenarios = 0
    for scenario in self.scenarios:
      status = 'OK'
      
      errors = []
      for step in scenario.steps:
        try:
          step()
        except Exception as e:
          exc_type, exc_value, exc_traceback = sys.exc_info()
          status = 'FAIL'
          errors.append(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
          errors.append('Scope:\n{}'.format(scenario.scope['scope']))
      
      color = Fore.RED
      if status == 'OK':
        passed_scenarios += 1
        color = Fore.GREEN
      
      print(color + ' * {} - {}'.format(scenario.subject, status))
      
      if errors:
        print(Style.RESET_ALL)
        print('\n'.join(errors))
        return False

    print(Style.RESET_ALL)
    print('Scenarios: {} passed / {} total'.format(passed_scenarios, len(self.scenarios)))
    return True
