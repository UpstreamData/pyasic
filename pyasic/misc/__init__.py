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
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from pyasic.API import APIError


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def api_min_version(version: str):
    def decorator(func):
        # handle the inner function that the decorator is wrapping
        async def inner(*args, **kwargs):
            api_ver = args[0].api_ver

            if not api_ver == "0.0.0" and isinstance(api_ver, str):
                api_sub_versions = api_ver.split(".")
                api_major_ver = int(api_sub_versions[0])
                api_minor_ver = int(api_sub_versions[1])
                if len(api_sub_versions) > 2:
                    api_patch_ver = int(api_sub_versions[2])
                else:
                    api_patch_ver = 0

                allowed_sub_versions = version.split(".")
                allowed_major_ver = int(allowed_sub_versions[0])
                allowed_minor_ver = int(allowed_sub_versions[1])
                if len(allowed_sub_versions) > 2:
                    allowed_patch_ver = int(allowed_sub_versions[2])
                else:
                    allowed_patch_ver = 0

                if not api_major_ver >= allowed_major_ver:
                    raise APIError(
                        f"Miner API version v{api_major_ver}.{api_minor_ver}.{api_patch_ver} is too low for {func.__name__}, required version is at least v{version}"
                    )
                if not (
                    api_minor_ver >= allowed_minor_ver
                    and api_major_ver == allowed_major_ver
                ):
                    raise APIError(
                        f"Miner API version v{api_major_ver}.{api_minor_ver}.{api_patch_ver} is too low for {func.__name__}, required version is at least v{version}"
                    )
                if not (
                    api_patch_ver >= allowed_patch_ver
                    and api_minor_ver == allowed_minor_ver
                    and api_major_ver == allowed_major_ver
                ):
                    raise APIError(
                        f"Miner API version v{api_major_ver}.{api_minor_ver}.{api_patch_ver} is too low for {func.__name__}, required version is at least v{version}"
                    )

            return await func(*args, **kwargs)

        return inner

    return decorator
