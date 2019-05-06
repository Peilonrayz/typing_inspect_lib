import collections
import typing


_TypeVarInfo = collections.namedtuple('TypeVarInfo', ['name', 'bound', 'covariant', 'contravariant'])


def get_type_var_info(type_var):
    """
    Get information in a TypeVar

    Example:

        TExample = TypeVar('TExample', bound=int)

        t_example = get_type_var_info(TExample)
        t_example == ('TExample', int, False, False)
        t_example.name == 'TExample'
        t_example.bound == int
        t_example.covariant is False
        t_example.contravariant is False
    """
    if not isinstance(type_var, typing.TypeVar):
        raise TypeError('get_type_var_info must be passed a TypeVar')
    return _TypeVarInfo(
        getattr(type_var, '__name__', None),
        getattr(type_var, '__bound__', None),
        getattr(type_var, '__covariant__', None),
        getattr(type_var, '__contravariant__', None),
    )
