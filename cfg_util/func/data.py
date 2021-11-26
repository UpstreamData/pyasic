from API import APIError


async def safe_parse_api_data(data: dict or list, *path: str or int, idx: int = 0):
    path = [*path]
    if len(path) == idx+1:
        if isinstance(path[idx], str):
            if isinstance(data, dict):
                if path[idx] in data.keys():
                    return data[path[idx]]
        elif isinstance(path[idx], int):
            if isinstance(data, list):
                if len(data) > path[idx]:
                    return data[path[idx]]
    else:
        if isinstance(path[idx], str):
            if isinstance(data, dict):
                if path[idx] in data.keys():
                    parsed_data = await safe_parse_api_data(data[path[idx]], idx=idx+1, *path)
                    if not parsed_data:
                        raise APIError(f"Data parsing failed on path index {idx} - \nKey: {path[idx]} \nData: {data}")
                    return parsed_data
                else:
                    if idx == 0:
                        raise APIError(f"Data parsing failed on path index {idx} - \nKey: {path[idx]} \nData: {data}")
                    return False
            else:
                if idx == 0:
                    raise APIError(f"Data parsing failed on path index {idx} - \nKey: {path[idx]} \nData: {data}")
                return False
        elif isinstance(path[idx], int):
            if isinstance(data, list):
                if len(data) > path[idx]:
                    parsed_data = await safe_parse_api_data(data[path[idx]], idx=idx+1, *path)
                    if not parsed_data:
                        raise APIError(f"Data parsing failed on path index {idx} - \nKey: {path[idx]} \nData: {data}")
                    return parsed_data
                else:
                    if idx == 0:
                        raise APIError(f"Data parsing failed on path index {idx} - \nKey: {path[idx]} \nData: {data}")
                    return False
            else:
                if idx == 0:
                    raise APIError(f"Data parsing failed on path index {idx} - \nKey: {path[idx]} \nData: {data}")
                return False
