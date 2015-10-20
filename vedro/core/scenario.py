class Scenario:

  def __init__(self, subject, steps, scope):
    self._subject = subject
    self._steps = steps
    self._scope = scope

  @property
  def subject(self):
    return self._subject

  @property
  def steps(self):
    return [self._scope[step] for step in self._steps]
