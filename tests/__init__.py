import sys
from unittest.mock import Mock

import nalgonda.services.oai_client

original_oai_client = nalgonda.services.oai_client
oai_mock = Mock()

sys.modules["nalgonda.services.oai_client"] = oai_mock
