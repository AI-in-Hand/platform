import sys
from unittest.mock import Mock

import backend.services.oai_client

original_oai_client = backend.services.oai_client
oai_mock = Mock()

sys.modules["backend.services.oai_client"] = oai_mock
