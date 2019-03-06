import itertools


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def _find_all_combinations(total, amount):
    for t in itertools.product(range(-1, total+1), repeat=amount):
        if all(i >= j for i, j in pairwise(t)):
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

    if len(tuples) >= before:
        class Test(obj):
            pass

        base = obj = Test
        for t in tuples[before:]:
            obj = obj[t]

    return base, obj, len(tuples) < before, len(tuples) in {0, before}


def _build_tests(type_, t_args, args, before, after):
    if len(t_args) != len(args):
        raise ValueError('Both arguments have to be the same length.')

    total = before + after
    for t in _find_all_combinations(total, len(t_args)):
        tuples = list(_build_tuples(t, t_args, args, total))
        start, stop = (0, before) if len(tuples) < before else (before, total)
        args_ = _build_args(t, t_args, args, start, stop)
        yield _build_type(type_, tuples, before, after) + (args_,)
