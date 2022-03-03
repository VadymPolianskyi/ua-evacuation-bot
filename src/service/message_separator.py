from src.config import limits


def separate(txt: str, limit: int = limits.FIND_RESPONSE_LIMIT) -> list:
    splited = txt.split('\n')
    i = 0
    result = [""]
    for s in splited:
        if len(result[i]) >= limit:
            i += 1
            result.append("")
        else:
            result[i] = result[i] + '\n' + s

    return result
