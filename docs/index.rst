ArgComb Documentation
=====================

.. toctree::
   :hidden:
   :maxdepth: 1

   api
   faq

.. automodule:: argcomb
   :noindex:

Installation
------------

Install using pip:

.. code-block:: text

    pip install arg-comb


Basic Usage
-----------

At the heart of ArgComb is the :func:`@argcomb<argcomb>` decorator. At its most basic, it
can assure that the caller supplies an argument::

    from argcomb import argcomb

    @argcomb("bar")
    def f(bar): ...

If ``bar`` is not supplied, an
:exc:`InvalidArgumentCombination` exception will be raised.

This doesn't achieve much since in any event ``bar`` is a required argument: even
without ArgComb, not supplying ``bar`` would have led to a ``TypeError``. ArgComb
comes into its own when the check to be carried out is more subtle.

Derived Conditions
------------------

Recall this example from earlier::

    from argcomb import argcomb, Xor

    @argcomb(Xor("length", "end"))
    def subseq(seq, start, length=None, end=None): ...

By passing an :class:`Xor` instance to :func:`@argcomb<argcomb>`, we check that
exactly one of the conditions holds.

A condition specified using :class:`Xor` is called a **derived condition**, since
it is derived from one or more other conditions (in this case, it is derived from
``"length"`` and ``"end"``).

ArgComb provides four types of derived condition:

:class:`And`
    Holds if all the conditions it is derived from hold. Takes any number of
    arguments.
:class:`Or`
    Holds if any of the conditions it is derived from hold. Takes any number
    of arguments.
:class:`Xor`
    Holds if exactly one of the conditions it is derived from holds. Takes any
    number of arguments.
:class:`Not`
    Holds if the condition it is derived from does not hold. Takes exactly one
    argument.

Derived conditions can themselves be derived from other derived conditions::

    from argcomb import argcomb, And, Xor

    @argcomb(Xor(And("a", "b"), And("c", "d"))
    def f(a=None, b=None, c=None, d=None): ...

In this way, arbitrarily complex conditions can be constructed.

Parameter Dependencies
----------------------

It is also possible to specify conditions in terms of how parameters depend on
each other.

The condition passed as the first positional argument to :func:`@argcomb<argcomb>`
(if any) is always evaluated. This is what we have used up
until now. Additional named arguments may be passed to :func:`@argcomb<argcomb>` to specify
conditions that must be met *only if that parameter is supplied by the caller*::

    from argcomb import argcomb, Or

    @argcomb(Or("a", "c"), a=Or("b", "c"), c="d")
    def f(a=None, b=None, c=None, d=None): ...

In this example, we must pass at least one of ``a`` or ``c`` due to the
``Or("a", "c")``. If ``a`` is supplied then either ``b``
or ``c`` must also be supplied, due to the ``a=Or("b", "c")``.
If ``c`` is supplied then ``d`` must also be
supplied, due to the ``c="d"``.

Strictly speaking parameter dependencies are just a more convenient way of
expressing complex derived conditions. For instance, the previous example
is equivalent to::

    from argcomb import argcomb, And, Or

    @argcomb(Or(And("a", Or("b", And("c", "d"))), And("c", "d")))
    def f(a=None, b=None, c=None, d=None): ...

In practice, as in this case, it is much more readable to use parameter
dependencies than to create highly nested derived conditions.

Value Dependent Conditions
--------------------------

Sometimes the value of an argument will dictate which other arguments can be
passed. In the following example, the function ``trim_video`` takes a video
clip and removes some frames from the end. The number of frames can either be
given explicitally, or the caller can specify the number of seconds they want
to be removed. The caller must declare which method they will use with the
``trim_type`` argument::

    from enum import Enum
    from argcomb import argcomb

    class TrimType(Enum):
        FRAMES = 0
        SECONDS = 1

    @argcomb(trim_type={
        TrimType.FRAMES: "frames",
        TrimType.SECONDS: "seconds",
    })
    def trim_video(
        file_name,
        trim_type,
        frames=None,
        seconds=None,
    ): ...

Instead of giving a single condition for ``trim_type``,
we specify different conditions depending on the value that ``trim_type`` takes.
We do this using a dictionary where the keys are the possible values for ``trim_type``
and the values are the respective conditions. If ``trim_type`` is ``TrimType.FRAMES``
then the caller must supply the ``frames`` argument, and if it is ``TrimType.SECONDS``
then the caller must supply the ``seconds`` argument.

.. note::
    While this example ensures that ``frames`` is passed when ``trim_type``
    is ``TrimType.FRAMES``, it does not check that in this case ``seconds``
    *isn't* passed. We could achieve this, and a similar check for
    ``TrimType.SECONDS``,  with::

        @argcomb(trim_type={
            TrimType.FRAMES: And("frames", Not("seconds")),
            TrimType.SECONDS: And("seconds", Not("frames")),
        })


If the value of the parameter does not match any of the dictionary keys, no validation
takes place. This can be overridden using the special value :class:`Else` as a key::

    from argcomb import argcomb, Else

    @argcomb(a={1: "b", Else: "c"})
    def f(a=None, b=None, c=None): ...

In this example, if ``a`` is ``1`` then ``b`` must also be supplied. If ``a``
takes any other value then ``c`` must be supplied. (If ``a`` isn't
passed at all then no validation takes place.)
