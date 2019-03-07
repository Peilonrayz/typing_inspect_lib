# Typing Inspect Lib

[![Build Status](https://travis-ci.org/Peilonrayz/typing_inspect_lib.svg)](https://travis-ci.org/Peilonrayz/typing_inspect_lib)

Allows type inspections for the `typing` and `typing_extensions` library.

Exposes four public functions:

1. `get_special_type` which returns the 'special type' of the type passed to it:

    - `typing.Callable`
    - `typing.ClassVar`
    - `typing.Generic`
    - `typing.NamedTuple`
    - `typing.NewType`
    - `typing.Optional`
    - `typing.Tuple`
    - `typing.Type`
    - `typing.TypeVar`
    - `typing.Union`
    - `typing_extensions.Protocol`
    - `None`
    
    Allowing for the following usage:
    
    ```python
    from typing import Generic, Union
    from typing_inspect_lib import get_special_type
    
    assert get_special_type(Generic) is Generic
    assert get_special_type(Union[Generic, str]) is Union
    ```
    
2. `get_typing` which returns the typing and the class instance of the type passed to it. Not just for special types.

    ```python
    from typing import Mapping, Union
    import collections.abc
    
    from typing_inspect_lib import get_typing
    
    typing_, class_ = get_typing(Mapping[str, int])
    assert typing_ is Mapping
    assert class_ is collections.abc.Mapping
    
    # Not all types have custom classes
    typing_, class_ = get_typing(Union[str, int])
    assert typing_ is Union
    assert class_ is Union
    ```

3. `get_args` which returns the arguments stored in the type provided.

    ```python
    from typing import Mapping
    from typing_inspect_lib import get_args
    
    assert get_args(Mapping) == ()
    assert get_args(Mapping[str, int]) == (str, int)
     ```

4. (WIP) `build_types` which builds the type object in, soon to be, easy to use classes.

    ```python
    from typing import Mapping, Union
    import collections.abc
    
    from typing_inspect_lib import build_types
    
    type_ = build_types(Mapping[Union[str, int], int])
    assert type_.typing is Mapping
    assert type_.class_ is collections.abc.Mapping
    assert type_.args[0].typing is Union
    assert type_.args[0].args[0].typing is str
     ```

# Python compatibility

Help! I'm using Python 3.5.1 and 3.6 and don't have access to `typing.ClassVar` in 3.5.1. What do I do?  
There are two ways to fix this:

1. Install `typing_extensions` and use `typing_extensions.ClassVar`.

    This is the preferred method, as this allows you to use `ClassVar` just the same way you would with `typing`.

    ```python
    from typing import Union
    from typing_extensions import ClassVar
    
    from typing_inspect_lib import get_special_type
    
    assert get_special_type(Union) is not ClassVar
    assert get_special_type(ClassVar) is ClassVar
    assert get_special_type(ClassVar[int]) is ClassVar
    ```
        
2. You can use `ClassVar_` exported by `typing_inspect_lib`.

    This defaults to just an `object()`, and so _should only be used to on the right hand side of `get_special_object` checks_:
    
    ```python
    from typing import Union
    
    from typing_inspect_lib import get_special_type, ClassVar_
    
    assert get_special_type(Union) is not ClassVar_
    assert get_special_type(ClassVar_) is ClassVar_
    assert get_special_type(ClassVar_[int]) is ClassVar_ # Error in 3.5.1
    ```

## When should I use these compatibility objects?

This depends on if you have `typing_extensions` installed. For the most part if you have it installed then you shouldn't need to use these. These also only affect older Python versions. Below is the list of when you may need to use these objects.


### `typing_extensions` is installed:

#### Python 3.5.0

 - `Protocol_`

### `typing_extensions` isn't installed:

#### Python 2.x or 3.x

 - `Protocol_`
 - `NewType_`

#### Python 3.5.0 - 3.5.2:

 - `ClassVar_`
 - `Type_`
