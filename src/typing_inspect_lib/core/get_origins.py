def _get_origins(type_):
    """Gets all origins. Includes passed type."""
    origins = [type_]
    if hasattr(type_, '__origin__'):
        while getattr(type_, '__origin__', None) is not None:
            type_ = type_.__origin__
            origins.append(type_)
    return origins


def _get_last_origin(type_):
    """Gets the last origin. Same as `__origin__` in Python 3.7"""
    if hasattr(type_, '_gorg'):
        return type_._gorg

    origins = _get_origins(type_)
    if len(origins) > 1:
        return origins[-1]
    return None
