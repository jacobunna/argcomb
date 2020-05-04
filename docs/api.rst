API Reference
=============

This page documents the public API exposed by ArgComb.

.. autodecorator:: argcomb.argcomb(default: typing.Optional[argcomb.Condition], /, **kwargs: argcomb.ArgumentSpec)

.. autoexception:: argcomb.InvalidArgumentCombination

.. autoclass:: argcomb.Or(*args: argcomb.Condition)

.. autoclass:: argcomb.And(*args: argcomb.Condition)

.. autoclass:: argcomb.Xor(*args: argcomb.Condition)

.. autoclass:: argcomb.Not(arg: argcomb.Condition)

.. autodata:: argcomb.Condition

.. autodata:: argcomb.ArgumentSpec
   :annotation: = typing.Union[typing.Dict[typing.Any, argcomb.Condition], argcomb.Condition]

.. autodata:: argcomb.Else
   :annotation:
