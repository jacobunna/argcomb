FAQ
===

Doesn't this add unnecessary overhead?
--------------------------------------

Doing additional runtime checks is slower than not doing them.
Whether this overhead is unnecessary is up to the developer. To add
checks to functions which aren't part of a public API would typically
be poor practice since in a stable release the checks would execute but
never fail. Yet adding checks to a public API may be helpful for your
users.

How does ArgComb deal with default values?
------------------------------------------

If a parameter *is* passed by the caller, but it is passed with its
default value, then ArgComb considers that the variable was not passed::

    from argcomb import argcomb

    @argcomb("a")
    def f(a=1): ...

In this case, ``f(a=2)`` is valid, but ``f(a=1)`` will raise an
:exc:`InvalidArgumentCombination` exception.

Why is there no ``Nand`` derived condition?
-------------------------------------------

It is considered that :class:`Or`, :class:`And`, :class:`Xor` and :class:`Not`
will be the most useful derived conditions. Other conditions can be derived
from these. If you feel strongly that another derived condition would
add value, please `open an issue`_.

Does ArgComb correctly handle positional-only and keyword-only parameters?
--------------------------------------------------------------------------

Yes. ArgComb supports all function signatures and calling patterns.

The only exception is when two parameters have the same name::

    from argcomb import argcomb

    @argcomb(a={1: "b", 2: "c"})
    def f(a=None, /, **kwargs): ...

The caller could conceivably call ``f(1, a=2)``, giving two possible values
for ``a``. In this case a warning is emitted. Validation will continue and
``2`` will be taken as the value of ``a``, but it is not recommended to use
ArgComb in this situation.


Why do you only support Python 3.8+?
------------------------------------

Since Python 3.8 introduced positional only arguments, the code for prior
versions would require some simple yet non-trivial changes. As a first
release of this module it only supports Python 3.8+, but if you would like
it to support an earlier version please feel free to `open an issue`_.

How does ArgComb handle ``*args`` and ``**kwargs``?
---------------------------------------------------

ArgComb requires arguments to have names in order to create conditions
for them. Since ``*args`` only captures arguments by position, it is
ignored by ArgComb.

It does not matter whether an argument explicitly appears in the
function signature or is implicitly accepted using ``**kwargs``.
In both cases, ArgComb can be used. For example::

    from argcomb import argcomb

    @argcomb(a="b")
    def f(**kwargs): ...

Neither ``a`` nor ``b`` are explicitly accepted as arguments by ``f``,
but if the caller supplies an argument called ``a`` then ArgComb will
check that they also pass an argument ``b``.

How can I create a value dependent condition for an unhashable value?
---------------------------------------------------------------------

Value dependent conditions are created using a dictionary where the
keys are parameter values and the values are their respective
conditions. Since dictionary keys must be hashable, this prevents
value dependent validation from being carried out based on a
unhashable type such as a ``list``.

This is by design. It is intended that value dependent conditions will
depend on simple indicator variables such as integers, booleans and
``enum.Enum`` instances. Triggering conditions based on comparisons
between complex, mutable objects risks creating behaviour which is
confusing to the caller.

Nevertheless, if you have a compelling use case, feel free to `open an issue`_..

Can't I achieve similar results using ``@typing.overload``?
-----------------------------------------------------------

The biggest difference is that static type checking is static whereas
ArgComb does validation at runtime. This means that whereas ArgComb
should only be used for public APIs where runtime checking is
desirable, ``typing`` can and should be applied to all parts of a
codebase.

In terms of functionality, there is overlap. For example, take the
following::

    from typing import Optional
    from argcomb import argcomb

    @argcomb(a={1: "b", 2: "c"})
    def f(
        a: Optional[int] = None,
        b: Optional[int] = None,
        c: Optional[int] = None
    ): ...

This is conceptually similar to::

    from typing import overload, Literal, Optional

    @overload
    def f(a: Literal(1), b: int, c: None): ...

    @overload
    def f(a: Literal(2), b: None, c: int): ...

    def f(
        a: Optional[int] = None,
        b: Optional[int] = None,
        c: Optional[int] = None
    ): ...

It is usually possible to achieve similar behaviour to ArgComb using
typing. However:

* ArgComb is more compact—in the example above it is slightly more compact,
  but for more complex conditions is can be vastly more compact, to the
  point that using ``typing`` is impractical
* ArgComb can be used even when the signature is generic i.e. uses
  ``*args`` and/or ``**kwargs``
* The behaviour of :class:`Else` cannot be achieved using ``typing``

Can I validate the *type* of one parameter based on the value of another parameter?
-----------------------------------------------------------------------------------

This is not possible.

Instead of the :class:`Else` condition, can I raise an exception?
-----------------------------------------------------------------

This is not possible. Such validation is beyond the scope of ArgComb,
which is focussed just on whether an argument is passed or not.

.. _`open an issue`: https://github.com/jacobunna/argcomb/issues/new
