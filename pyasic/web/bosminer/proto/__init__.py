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
from __future__ import annotations

from .bos import version_pb2
from .bos.v1 import (
    actions_pb2,
    authentication_pb2,
    common_pb2,
    configuration_pb2,
    constraints_pb2,
    cooling_pb2,
    license_pb2,
    miner_pb2,
    performance_pb2,
    pool_pb2,
    units_pb2,
    work_pb2,
)


def get_service_descriptors():
    return [
        *version_pb2.DESCRIPTOR.services_by_name.values(),
        *authentication_pb2.DESCRIPTOR.services_by_name.values(),
        *actions_pb2.DESCRIPTOR.services_by_name.values(),
        *common_pb2.DESCRIPTOR.services_by_name.values(),
        *configuration_pb2.DESCRIPTOR.services_by_name.values(),
        *constraints_pb2.DESCRIPTOR.services_by_name.values(),
        *cooling_pb2.DESCRIPTOR.services_by_name.values(),
        *license_pb2.DESCRIPTOR.services_by_name.values(),
        *miner_pb2.DESCRIPTOR.services_by_name.values(),
        *performance_pb2.DESCRIPTOR.services_by_name.values(),
        *pool_pb2.DESCRIPTOR.services_by_name.values(),
        *units_pb2.DESCRIPTOR.services_by_name.values(),
        *work_pb2.DESCRIPTOR.services_by_name.values(),
    ]


def get_auth_service_descriptors():
    return authentication_pb2.DESCRIPTOR.services_by_name.values()
