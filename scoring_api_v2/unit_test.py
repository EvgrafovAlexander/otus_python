import pytest
import hashlib
import datetime

import api

char = api.CharField(required=False, nullable=False).is_valid(2)
print(char)