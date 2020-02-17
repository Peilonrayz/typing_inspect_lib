Types
=====

When using Typing Inspect Lib you'll come across three main types.
It's important that you know what the difference between the three of
them are so that you can get the most out Typing Inspect Lib.

When a function says "type" without specifying the subtype, then it
means all subtypes. Unless specified otherwise.

Common Types
------------

.. _Unwrapped:

Unwrapped
^^^^^^^^^

These can be any type that derive from :pep:`484` that doesn't have
their arguments or parameters defined by a user. This means that
:class:`typing.List` is an unwrapped type, but :code:`typing.List[str]` is not.

There are also :ref:`Wrapped` types, which have arguments or parameters
defined by a user.

These normally are the simplest type to work with as they correspond
with the types already being used.

Some examples are:

- :class:`typing.List`.
- :class:`typing.Mapping`.
- :class:`typing.Union`.
- :class:`typing.Generic`.

.. _Wrapped:

Wrapped
^^^^^^^

These are :ref:`Unwrapped` types with the arguments and parameters set.

Some examples are:

- :code:`typing.List[bool]`.
- :code:`typing.Mapping[TKey, TValue]`.
- :code:`typing.Union[str, int]`.

.. _Origin:

Origin
^^^^^^

.. note::

    | From Python 3.7 these are the :code:`__origin__` of the :ref:`Unwrapped` types.
    | However in Python 3.5 and 3.6 these were the :code:`__extra__` of the :ref:`Unwrapped` types.

These are normally provided whenever a :ref:`Unwrapped` type is.
This is to provide an abstraction to the typing internals.

Whilst these seem easy to work with, they can be missing from the
standard library in different Python versions.
For example the Origin type of :class:`typing.Match` doesn't exist in
:mod:`re` in previous versions of Python.

Some examples are:

- :class:`collections.abc.List`.
- :class:`collections.abc.Mapping`.
- :class:`typing.Union`.
- :class:`typing.Generic`.

Uncommon Types
--------------

.. _Literal:

Literal
^^^^^^^

These are commonly builtin types that can be passed to :ref:`Typing` types.

Some examples are:

- :class:`list`.
- :class:`dict`.
- :class:`tuple`.

.. _Typing:

Typing
^^^^^^

These are types that are defined in either :mod:`typing` or `Typing Extensions`_.

.. _Typing Extensions: https://github.com/python/typing/tree/master/typing_extensions

Some examples are:

- :class:`typing.List`.
- :class:`typing.Mapping`.
- :class:`typing.Union`.
- :class:`typing.Generic`.

.. _User Defined:

User Defined
^^^^^^^^^^^^

These are types that are defined by users. These normally inherit
:class:`typing.Generic` or :class:`typing.Protocol`.

.. _Special:

Special
^^^^^^^

These types aren't well defined, sometimes a type is special in one context,
sometimes it's not in another.

This mostly is to show that the handling is special, like an edge case,
to the normal :mod:`typing` and typing_inspect code.

Some special types are, but not limited to:

- :class:`typing.Callable`,
- :class:`typing.ClassVar`,
- :class:`typing.Generic`,
- :class:`typing.NamedTuple`,
- :class:`typing.Optional`,
- :class:`typing.Tuple`,
- :class:`typing.Type`,
- :class:`typing.Union`,
- :code:`typing_extensions.Protocol`,
- :code:`typing_extensions.ClassVar`,
- :code:`typing_extensions.Type`
