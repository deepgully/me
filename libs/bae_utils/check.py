# -*- coding: utf-8 -*-

from .exceptions import BaeParamError

def checkParamsType(params):
   for v, t in params:
      if not any(map(lambda x: isinstance(v, x), t)):
         raise BaeParamError("Invalid type", v, "Expected type is %s"%', '.join(map(lambda x: x.__name__, t)))

def checkParamsLimit(conditions):
   for v, c in conditions:
      f = [lambda x: eval(i) for i in c]
      if not all(map(lambda x: x(v), f)):
         raise BaeParamError("Bad Params", v, "Params should meet the constraint requirements: %s"%', '.join(c))
