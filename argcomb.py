"""ArgComb checks that the combination of arguments supplied for a
function is valid. For example, suppose a function has the following
signature::

    def subseq(seq, start, length=None, end=None): ...

This function returns a subsequence of ``seq`` starting at ``start``. The
end can be specified by supplying either ``length`` or ``end``. The
:func:`@argcomb<argcomb>` decorator checks that exactly one of these is supplied::

    from argcomb import argcomb, Xor

    @argcomb(seq=Xor("length", "end"))
    def subseq(seq, start, length=None, end=None): ...
"""

from __future__ import annotations

import abc
import contextlib
import enum
import functools
import warnings
from typing import Any, Callable, Dict, NoReturn, Optional, Tuple, Union

__all__ = [
    "argcomb",
    "Or",
    "And",
    "Xor",
    "Not",
    "Else",
    "InvalidArgumentCombination",
    "Condition",
    "ArgumentSpec",
]


class InvalidArgumentCombination(ValueError):
    """Raised when the caller passes an invalid argument
    combination. """


class ConditionType(enum.Enum):
    """Enumeration of types of condition. """

    NOT = 0
    AND = 1
    OR = 2
    XOR = 3


class DerivedCondition(abc.ABC):
    """A condition that is derived from one or more other
    conditions. """

    type_: ConditionType

    def __init__(self, *args: Condition):
        """Construt a condition.

        :param args: list of conditions nested under this condition
        """

        self.args = args
        with contextlib.suppress(NotImplementedError):
            self._validate()

    def _validate(self) -> None:
        """Perform post initialisation validation if required. """

        raise NotImplementedError

    def __repr__(self) -> str:
        return (
            self.type_.name.capitalize()
            + "("
            + ", ".join(repr(a) for a in self.args)
            + ")"
        )


class Or(DerivedCondition):
    """Logical OR condition.

    An :class:`Or` condition will evaluate to ``True`` if any of
    its child conditions evaluates to ``True``.

    :param args: conditions from which this new condition should be
        constructed.
    """

    type_ = ConditionType.OR


class And(DerivedCondition):
    """Logical AND condition.

    An :class:`And` condition will evaluate to ``True`` only if all
    its child conditions evaluate to ``True``.

    :param args: conditions from which this new condition should be
        constructed.
    """

    type_ = ConditionType.AND


class Xor(DerivedCondition):
    """Logical XOR condition.

    An :class:`Xor` condition will evaluate to ``True`` only if exactly
    1 of its child conditions evaluates to ``True``.

    :param args: conditions from which this new condition should be
        constructed.
    """

    type_ = ConditionType.XOR


class Not(DerivedCondition):
    """Logical NOT condition.

    An :class:`Not` condition will evaluate to ``True`` only if its child
    condition evaluates to ``False``.

    :param arg: the child condition that this new condition is based on
    """

    type_ = ConditionType.NOT

    def _validate(self) -> None:
        """Ensure that only one argument was passed. """

        if len(self.args) != 1:
            raise TypeError(
                f"Not() takes 1 positional argument but {len(self.args)} were given"
            )


#: Type definition for conditions. A condition can take one of two
#: forms:
#:
#: #. A string containing the name of a variable. In this case, the
#:    condition evaluates to ``True`` if the variable named in the
#:    string is passed by the caller, or ``False`` otherwise.
#: #. An instance of :class:`Or`, :class:`And`, :class:`Xor`,
#:    or :class:`Not`. Such conditions are called "derived
#:    conditions", as they are derived from other conditions.
#:
#: Since derived conditions can be constructed from other derived
#: conditions, arbitrarily complex conditions can be created, for
#: example::
#:
#:     my_condition = Or(And("a", "b"), Not(Xor("a", "c", "d")))
Condition = Union[str, DerivedCondition]

#: Type definition for argument specification.
#:
#: Argument specifications determine what validation is done in
#: respect of the caller supplying a certain argument.
#:
#: An argument specification can either be a :data:`Condition` or a
#: dictionary mapping values to :data:`Condition`\ s.
#:
#: If an argument specification is a :data:`Condition` then
#: validation of that argument will succeed if the condition is
#: valid. If the argument specification is a dictionary mapping
#: values to :data:`Condition`\ s then the :data:`Condition` will be
#: chosen based on the value of the argument being validated.
#:
#: If an argument specification is a dictionary, a special key
#: :data:`Else` is available to serve as a catch-all for values
#: not otherwise handled. If no :data:`Else` key is present and the
#: value of the argument is also not present, no validation will take
#: place. For example::
#:
#:     @argcomb(a={1: "b", 2: "c"})
#:     def f(a, b, c): ...
#:
#: In this case, ``f(a=1, b=2)`` is valid but ``f(a=2, b=2)`` is not.
#: ``f(a=3)`` is valid. ::
#:
#:     @argcomb(a={1: "b", Else: "c"})
#:     def f(a, b, c): ...
#:
#: Now ``f(a=3)`` is not valid, but ``f(a=3, c=2)`` is
#: valid.
ArgumentSpec = Union[Dict[Any, Condition], Condition]

#: Special value to indicate validation behaviour when a value-specific
#: condition is not available. See :data:`ArgumentSpec` for more
#: details.
Else = object()


class argcomb:
    """Check that the combination of arguments passed to a function by
    the caller is valid.

    The first argument is a condition which, if supplied, is
    always evaluated. For example::

        @argcomb(Or("a", "b"))
        def f(a=None, b=None): ...

    The :data:`Condition` ``Or("a", "b")`` stipulates that the caller
    must pass at least one of ``a`` or ``b`` as an argument to ``f``
    when calling it, otherwise an :exc:`InvalidArgumentCombination`
    exception will be raised.

    Subsequent arguments determine further validation that should be
    carried out *if* an additional argument is specified. This
    validation can optionally vary depending on the value that the
    caller passes for this argument. ::

        @argcomb(Or("a", "b"), a="c")
        def g(a=None, b=None, c=None): ...

        @argcomb(Or("a", "b"), a={1: "b", 2: "c", Else: Or("b", "c"))
        def h(a=None, b=None, c=None): ...

    For ``g``, at least one of ``a`` or ``b`` must be passed, and if
    ``a`` is passed then ``c`` must be passed too.

    For ``h``, at least one of ``a`` or ``b`` must be passed. If ``a``
    is passed then further validation will take place depending on the
    value of ``a``. If ``a==1`` then ``b`` must also be passed. If
    ``a==2`` then ``c`` must also be passed. If ``a`` takes any value
    except ``1`` or ``2`` then at least one of ``b`` or ``c`` must be
    passed.

    :param default: a :class:`Condition` that must always evaluate to
        ``True`` in order for the call to be considered valid.
    :param kwargs: for each keyword argument, the name is assumed to be
        the name of a variable that the caller may supply, and the
        value determines any valiation actions that should take place
        if that variable is passed by the caller to the decorated
        function.
    """

    _spec: Dict[str, ArgumentSpec]
    _default: Optional[Condition]

    def __init__(self, default: Optional[Condition] = None, /, **kwargs: ArgumentSpec):
        """Specify the conditions.

        :param kwargs: the conditions to validate the arguments against

        There are two forms that a condition can take. If the mere fact
        that an argument is supplied means a condition should be
        validated, the condition can be given directly. For example:
            @argcomb(a=Or("b", "c"))
        This says that if argument `a is supplied then at least one of
        `b` or `c` must also be supplied. Alternatively different
        conditions can be given depending on the value that an argument
        takes:
            @argcomb(a={1: "b", 2: "c"})
        This says if `a` is `1` then `b` must be supplied, and if `a`
        is `2` then `c` must be supplied. In this case, `Else` may be
        used as a catch-all for other cases:
            @argcomb(a={1: "b", 2: "c", Else: Or("b", "c")})
        """

        self._spec = kwargs
        self._default = default

    def __call__(self, func: Callable) -> Callable:
        """Create the decorated function.

        :param func: the original function
        :return: the decorated function
        """

        @functools.wraps(func)
        def ret(*args: Any, **kwargs: Any) -> Any:
            # Although functions and methods both have ``__defaults__` and
            # ``__kwdefaults__`` members, not all callables necessarily have
            # them
            try:
                pos_arg_defaults = func.__defaults__  # type: ignore
            except AttributeError:
                pos_arg_defaults = None
            try:
                kw_arg_defaults = func.__kwdefaults__  # type: ignore
            except AttributeError:
                kw_arg_defaults = None
            arg_dict = self._get_arg_dict(
                pos_arg_values=args,
                kw_args=kwargs,
                all_arg_names=func.__code__.co_varnames,
                pos_arg_defaults=pos_arg_defaults,
                kw_arg_defaults=kw_arg_defaults,
                kw_only_arg_count=func.__code__.co_kwonlyargcount,
            )
            self._check_all(arg_dict)
            return func(*args, **kwargs)

        return ret

    @staticmethod
    def _get_arg_dict(
        *,
        pos_arg_values: Tuple,
        kw_args: Dict[str, Any],
        all_arg_names: Tuple[str, ...],
        pos_arg_defaults: Optional[Tuple],
        kw_arg_defaults: Optional[Dict[str, Any]],
        kw_only_arg_count: int,
    ) -> Dict[str, Any]:
        """Get a dictionary of user supplied arguments and their values.

        If the user supplies an argument with its default value, it is
        treated as if the user did not pass it at all.

        For keyword arguments this is a slightly more simple since both
        the values and the defaults are supplied in a dictionary
        mapping argument names to values, but for positional arguments
        we need to do some work to match up the argument names, values
        and default values.
        """

        defaults: Dict[str, Any] = {}
        if pos_arg_defaults:
            if kw_only_arg_count:
                pos_arg_names = all_arg_names[:-kw_only_arg_count]
            else:
                pos_arg_names = all_arg_names
            defaults.update(zip(reversed(pos_arg_names), reversed(pos_arg_defaults)))
        if kw_arg_defaults:
            defaults.update(kw_arg_defaults)

        arg_dict = {
            arg_name: arg_value
            for arg_name, arg_value in zip(all_arg_names, pos_arg_values)
            if arg_name not in defaults or defaults[arg_name] != arg_value
        }
        for arg_name in kw_args:
            if arg_name in arg_dict:
                # For a function such as:
                #     f(a, /, **kwargs): ...
                # the call ``f(1, a=1)`` is valid, but from
                # ``argcomb``'s point of view there are now two
                # arguments both called ``a``. This is not supported
                # and ``argcomb`` should not be used where there are
                # both positional only arguments and ``**kwargs``. We
                # emit a warning when this situation is detected.
                warnings.warn(
                    f"Argument {arg_name} was supplied as both a"
                    "positional only argument and a keyword argument. This is"
                    "not supported by ArgComb."
                )
        arg_dict.update(
            {
                arg_name: arg_value
                for arg_name, arg_value in kw_args.items()
                if arg_name not in defaults or defaults[arg_name] != arg_value
            }
        )
        return arg_dict

    def _check_all(self, arg_dict: Dict[str, Any]) -> None:
        """Execute all checks as specified in ``self._spec``.

        Also check that ``self._default`` holds.

        :param arg_dict: dictionary of argument names and values
        """

        if self._default and not self._validate(arg_dict, self._default):
            raise InvalidArgumentCombination(
                f"Condition `{self._default}` does not hold"
            )

        for arg_name, arg_spec in self._spec.items():
            self._check(arg_dict, arg_name, arg_spec)

    def _check(
        self,
        arg_dict: Dict[str, Any],
        arg_name: str,
        arg_spec: Union[Dict[Any, Condition], Condition],
    ) -> None:
        """Check an argument.

        If the check fails then an `InvalidArgumentCombination`
        exception is raised.

        :param arg_dict: dictionary of arguments and values
        :param arg_name: name of the argument being checked
        :param arg_spec: specification for this argument
        """

        if arg_name not in arg_dict:
            # This argument wasn't supplied
            return
        if not isinstance(arg_spec, dict):
            if not self._validate(arg_dict, arg_spec):
                self._raise_error(arg_name, arg_spec)
            return
        for arg_val, condition in arg_spec.items():
            if arg_val != arg_dict[arg_name] or arg_name is Else:
                continue
            if not self._validate(arg_dict, condition):
                self._raise_error(arg_name, condition)
        if Else in arg_spec:
            if not self._validate(arg_dict, arg_spec[Else]):
                self._raise_error(arg_name, arg_spec[Else])

    @staticmethod
    def _raise_error(arg_name: str, condition: Condition) -> NoReturn:
        """Raise an exception when validation fails.

        :param arg_name: name of the argument that did not validate
        :param condition: failing condition
        """

        raise InvalidArgumentCombination(
            f"Argument `{arg_name}` is not valid: condition `{condition}` does not hold"
        )

    def _validate(self, arg_dict: Dict[str, Any], condition: Condition) -> bool:
        """Validate a single condition.

        :param arg_dict: dictionary of arguments and values
        :param condition: the condition to evaluate
        :return: `True` if the condition is satisfied or `False` otherwise
        """

        if isinstance(condition, str):
            return condition in arg_dict

        if isinstance(condition, Not):
            return not self._validate(arg_dict, condition.args[0])

        if isinstance(condition, Or):
            for arg in condition.args:
                if self._validate(arg_dict, arg):
                    return True
            return False

        if isinstance(condition, Xor):
            found_true = False
            for arg in condition.args:
                if self._validate(arg_dict, arg):
                    if found_true:
                        return False
                    found_true = True
            return found_true

        if isinstance(condition, And):
            for arg in condition.args:
                if not self._validate(arg_dict, arg):
                    return False
            return True

        raise TypeError(f"Condition type {type(condition)} is not supported")
