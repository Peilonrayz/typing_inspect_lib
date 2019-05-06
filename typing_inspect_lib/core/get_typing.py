import typing
import types

from .helpers import safe_dict_get, PY_OLD, LITERAL_TYPES, TYPING_OBJECTS, SPECIAL_OBJECTS_WRAPPED, typing_

from .get_origins import _get_last_origin


if PY_OLD:
    def _get_typing(type_):
        """
        Returns the typing type and class type of a wrapped or unwrapped type.

        This function doesn't work special types, these require another function to extract the information correctly.
        Builtin {literal types, class types, typing types} all are handled before this function runs.

        Example:

            _get_typing(Mapping[str, int]) == (Mapping, collections.abc.Mapping)
            _get_typing(MyClass) == (MyClass, MyClass)
            _get_typing(MyClass[str, int]) == (MyClass, MyClass)
        """
        origin = _get_last_origin(type_)
        if origin is not None:
            return origin, safe_dict_get(TYPING_OBJECTS.typing_to_class, origin) or origin

        if isinstance(type_, typing.GenericMeta):
            return type_, type_
        return None
else:
    def _get_typing(type_):
        origin = getattr(type_, '__origin__', None)
        if origin is not None:
            return safe_dict_get(TYPING_OBJECTS.class_to_typing, origin) or origin, origin

        if hasattr(type_, '__orig_bases__'):
            return type_, type_
        return None


def _get_special_typing_universal(type_):
    """Handles the following types for wrapped types: TypeVar, Protocol, NewType"""
    if isinstance(type_, typing.TypeVar):
        return typing.TypeVar, type_
    if isinstance(type_, typing_.ProtocolMeta):
        return typing_.Protocol, type_
    if isinstance(type_, types.FunctionType) and hasattr(type_, '__supertype__'):
        return typing_.NewType, type_
    return None


if PY_OLD:
    def _get_special_typing(type_):
        """Handles special types that can't be handled through normal means."""
        return safe_dict_get(SPECIAL_OBJECTS_WRAPPED.class_types, type(type_))
else:
    def _get_special_typing(type_):
        return None


def get_typing(type_):
    """
    Gets the typing type and the class type of the type passed to it.

    Examples:

        get_typing(Mapping) == (Mapping, collections.abc.Mapping)
        get_typing(Mapping[str, int]) == (Mapping, collections.abc.Mapping)
        get_typing(Union[str, int]) == (Union, Union)
    """
    ret = (
            _get_special_typing_universal(type_)
            or safe_dict_get(LITERAL_TYPES, type_)
            or safe_dict_get(TYPING_OBJECTS.class_types, type_)
            or safe_dict_get(TYPING_OBJECTS.typing_types, type_)
            or _get_typing(type_)
            or _get_special_typing(type_)
    )
    if ret is None:
        return None, None
    t, c = ret
    if t is typing_.NewType:
        c = type_
    return t, c