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

from settings import RUNTIME_ENV, QINIU_SETTINGS

__all__ = [
    "secret_hash", "unquote", "save_photo", "delete_file", "make_blob_file_header",
    "fail_safe_func",
]

from common import *

exec("from tools_%s import *" % RUNTIME_ENV.split("_")[0]) in locals()

if QINIU_SETTINGS.Enabled:
    delete_file = delete_file_qiniu
