# Typing Inspect Lib

[![Build Status](https://travis-ci.org/Peilonrayz/typing_inspect_lib.svg?branch=master)](https://travis-ci.org/Peilonrayz/typing_inspect_lib)

Allows type inspections for the `typing` and `typing_extensions` library.

## API

Currently I support the following functions:

- `get_typing`
- `get_args`
- `get_parameters`
- `get_type_info`
- `get_type_var_info`
- `get_bases`
- `get_mro`
- `get_mro_orig`
- (WIP) `build_types`

### `get_typing`

This returns the typing type and the class type of the type passed to it.

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

### `get_args`

This returns the arguments stored in the type provided.

```python
from typing import Mapping, Union
from typing_inspect_lib import get_args

assert get_args(Mapping) == ()
assert get_args(Mapping[str, int]) == (str, int)
assert get_args(Mapping[Union[str, int], int]) == (Union[str, int], int)
```

### `get_parameters`

This returns the parameters stored in the type provided.

```python
from typing import Mapping, TypeVar
from typing_inspect_lib import get_parameters

TKey = TypeVar('TKey')
TValue = TypeVar('TValue')

assert get_parameters(Mapping[str, int]) == ()
assert get_parameters(Mapping[TKey, TValue]) == (TKey, TValue)
```

### `get_type_info`

This returns all the type information for a type.

```python
from typing import Mapping, TypeVar
from typing_inspect_lib import get_type_info
import collections

TKey = TypeVar('TKey')
type_ = get_type_info(Mapping[TKey, int])

assert type_ == (Mapping, collections.abc.Mapping, (int,), (TKey,))
assert type_.typing == Mapping
assert type_.class_ == collections.abc.Mapping
assert type_.args == (int,)
assert type_.parameters == (TKey,)
```

### `get_type_var_info`

This returns the parameters stored in the type provided.

```python
from typing import Mapping, TypeVar
from typing_inspect_lib import get_parameters, get_type_var_info

TExample = TypeVar('TExample', bound=int)
t_example = get_type_var_info(TExample)

assert t_example == ('TExample', int, False, False)
assert t_example.name == 'TExample'
assert t_example.bound == int
assert not t_example.covariant
assert not t_example.contravariant

# Using this with typing objects
assert get_parameters(Mapping) != ()
mapping_parameters = tuple(get_type_var_info(p) for p in get_parameters(Mapping))
assert (('KT', None, False, False), ('VT_co', None, True, False)) == mapping_parameters
```

### `get_bases`

Gets the bases of the type, returns the typing type, class type and orig type.

This returns different values in different versions of Python. The below is Python 3.7.

```python
from typing import Mapping, Collection
from collections import abc

from typing_inspect_lib import get_bases

assert get_bases(Mapping) == ((Collection, abc.Collection, None),)
assert get_bases(abc.Mapping) == ((Collection, abc.Collection, None),)
assert get_bases(Mapping[int, int]) == ((Collection, abc.Collection, typing.Collection[int]),)
```

### `get_mro`

Gets the mro of the type. Returning them as class types.

Builtin types are converted to their class type to get the MRO and so `Generic` may be missing.

This returns different values in different versions of Python. The below is Python 3.7.

```python
from typing import Mapping
from collections import abc

from typing_inspect_lib import get_mro

mro = (
    abc.Mapping,
    abc.Collection,
    abc.Sized,
    abc.Iterable,
    abc.Container,
    object
)
assert get_mro(Mapping) == mro
assert get_mro(abc.Mapping) == mro
assert get_mro(Mapping[int, str]) == mro
```

### (WIP) `build_types`

This builds the type object in, soon to be, easy to use classes.

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

## Incompatibilities between versions

- <3.5.[0-1]> Passing `get_args(typing_extensions.Counter[T])` returns `(T, int)` rather than `(T,)`.
- Some parameters change between versions:
    - <3.5.2> `typing.Type` is `CT`, rather than `CT_co`. (It is still covariant and bound to `type`)  
       FIX: `typing_extensions.Type` works fine.
    - <3.5.[0-1]> `typing.ItemsView` is `T_co, KT, VT_co` rather than `KT, VT_co`.
    - <3.5.[0-1]> `typing_extensions.Coroutine` is `V_co, T_co, T_contra` rather than `T_co, T_contra, T_co`.
- Due to changes in `collections.abc` the following functions return different results in different Python versions:
    - `get_bases`
    - `get_mro`
    - `get_mro_orig`

## Compatibility objects

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

### When should I use these compatibility objects?

This depends on if you have `typing_extensions` installed. For the most part if you have it installed then you shouldn't need to use these. These also only affect older Python versions. Below is the list of when you may need to use these objects.


#### `typing_extensions` is installed:

 - <3.5.0> `Protocol_`

#### `typing_extensions` isn't installed:

 - <2.x & 3.x> `Protocol_`
 - <2.x & 3.x> `NewType_`
 - <3.5.[0-2]> `ClassVar_`
