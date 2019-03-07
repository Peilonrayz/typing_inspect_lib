import itertools


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def _find_all_combinations(start, stop, amount, fn=lambda i, j: i >= j):
    range_ = [-1] + list(range(start, stop))
    for t in itertools.product(range_, repeat=amount):
        if all(fn(i, j) for i, j in pairwise(t)):
            yield t


def _build_args(placements, t_args, args, start, stop):
    return [
        (t_args if p >= stop else args)[i]
        for i, p in enumerate(placements)
        if p >= start
    ]


def _build_tuples(placements, t_args, args, total):
    sentinel = object()
    values = list(t_args)
    for i in range(total):
        for j, (v, p) in enumerate(zip(values, placements)):
            if p < i:
                value = sentinel
            elif i == p:
                value = args[j]
            else:
                value = v
            values[j] = value
        values = [v for v in values if v is not sentinel]
        if not values:
            break
        yield tuple(values)


def _build_type(type_, tuples, before, after):
    tuples = list(tuples)

    base = obj = type_
    for t in tuples[:before]:
        obj = obj[t]

    if len(tuples) >= before and after:
        class Test(obj):
            pass

        # Name mangle so debugging is easier.
        Test.__module__ = type_.__module__
        Test.__qualname__ = 'BT<{}>'.format(getattr(type_, '__name__', getattr(type_, '_name', '')))

        base = obj = Test
        for t in tuples[before:]:
            obj = obj[t]

    return base, obj, not after or len(tuples) < before, len(tuples) in {0, before}


def _build_tests(type_, t_args, args, start_, stop_, obj, fn):
    if t_args is None and args is None:
        yield None, type_, True, True, ()
        return

    if len(t_args) != len(args):
        raise ValueError('Both arguments have to be the same length.')

    for t in _find_all_combinations(start_, stop_+1, len(t_args), fn=fn):
        tuples = list(_build_tuples(t, t_args, args, stop_))
        start, stop = (obj, stop_) if len(tuples) >= obj and stop_ > obj else (0, min(obj, stop_))
        args_ = _build_args(t, t_args, args, start, stop)
        # ClassVar doesn't work with tuples
        tuples = [t[0] if len(t) == 1 else t for t in tuples]
        yield _build_type(type_, tuples, obj, stop_ > obj) + (args_,)
