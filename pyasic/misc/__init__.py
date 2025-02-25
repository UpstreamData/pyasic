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

from copy import deepcopy

from pyasic.errors import APIError


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
                        f"Miner API version v{api_major_ver}.{api_minor_ver}.{api_patch_ver}"
                        f" is too low for {func.__name__}, required version is at least v{version}"
                    )
                if not (
                    api_minor_ver >= allowed_minor_ver
                    and api_major_ver == allowed_major_ver
                ):
                    raise APIError(
                        f"Miner API version v{api_major_ver}.{api_minor_ver}.{api_patch_ver}"
                        f" is too low for {func.__name__}, required version is at least v{version}"
                    )
                if not (
                    api_patch_ver >= allowed_patch_ver
                    and api_minor_ver == allowed_minor_ver
                    and api_major_ver == allowed_major_ver
                ):
                    raise APIError(
                        f"Miner API version v{api_major_ver}.{api_minor_ver}.{api_patch_ver} "
                        f"is too low for {func.__name__}, required version is at least v{version}"
                    )

            return await func(*args, **kwargs)

        return inner

    return decorator


def merge_dicts(a: dict, b: dict) -> dict:
    result = deepcopy(a)
    for b_key, b_val in b.items():
        a_val = result.get(b_key)
        if isinstance(a_val, dict) and isinstance(b_val, dict):
            result[b_key] = merge_dicts(a_val, b_val)
        else:
            result[b_key] = deepcopy(b_val)
    return result


def validate_command_output(data: dict) -> tuple[bool, str | None]:
    if "STATUS" in data.keys():
        status = data["STATUS"]
        if isinstance(status, str):
            if status in ["RESTART"]:
                return True, None
            status = data
        if isinstance(status, list):
            status = status[0]

        if status.get("STATUS") in ["S", "I"]:
            return True, None
        else:
            return False, status.get("Msg", "Unknown error")
    else:
        for key in data.keys():
            # make sure not to try to turn id into a dict
            if key == "id":
                continue
            if "STATUS" in data[key][0].keys():
                if data[key][0]["STATUS"][0]["STATUS"] not in ["S", "I"]:
                    # this is an error
                    return False, f"{key}: " + data[key][0]["STATUS"][0]["Msg"]
        return True, None
