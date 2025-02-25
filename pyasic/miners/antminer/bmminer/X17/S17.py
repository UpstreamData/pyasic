# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------

from pyasic.miners.backends import AntminerOld
from pyasic.miners.device.models import S17, S17e, S17Plus, S17Pro


class BMMinerS17(AntminerOld, S17):
    pass


class BMMinerS17Plus(AntminerOld, S17Plus):
    pass


class BMMinerS17Pro(AntminerOld, S17Pro):
    pass


class BMMinerS17e(AntminerOld, S17e):
    pass
