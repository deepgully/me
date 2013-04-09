# -*- coding: utf-8 -*-
# Copyright 2013 Gully Chen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys

if sys.platform == 'win32':
    pybabel = r"C:\Python27\Scripts\pybabel.exe"
else:
    pybabel = "pybabel"

from config import LANGUAGES
os.system(pybabel + ' extract -F babel.cfg -k lazy_gettext -k T -o messages.pot ..\\')

for lang in LANGUAGES.keys():
    os.system('%s update -i messages.pot -d . -l "%s"' % (pybabel, lang.replace("-","_")))

os.system("pause")
os.unlink('messages.pot')

