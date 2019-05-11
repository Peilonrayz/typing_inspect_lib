import collections

from .get_args import _get_args
from .get_parameters import _get_parameters
from .get_typing import get_typing
from .helpers.typing_ import ClassVar


class _TypeInfo(
        collections.namedtuple(
            'TypeInfo',
            ['typing', 'class_', 'args', 'parameters']
        )
):
    def __eq__(self, other):
        if not isinstance(other, _TypeInfo):
            return False
        if self.typing is ClassVar:
            if self.typing is not other.typing:
                return False
            if self.class_ is not other.class_:
                return False
        else:
            if self.typing != other.typing:
                return False
            if self.class_ != other.class_:
                return False
        return self.args == other.args and self.parameters == other.parameters


def get_type_info(type_):
    """
    Get all the type information for a type.

    Examples:

        type_ = get_type_info(Mapping[TKey, int])
        type_ == (Mapping, collections.abc.Mapping, (int,), (TKey,))
        type_.typing == Mapping
        type_.class_ == collections.abc.Mapping
        type_.args == (int,)
        type_.parameters == (TKey,)
    """
    t_typing, class_ = get_typing(type_)
    if t_typing is None and class_ is None:
        return None
    args = tuple(a for a in _get_args(type_, t_typing=t_typing))
    parameters = tuple(p for p in _get_parameters(type_, t_typing=t_typing))
    return _TypeInfo(t_typing, class_, args, parameters)
