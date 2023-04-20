import collections
import inspect
import logging
import statistics


def _count_deviation(value, lower_boundary, upper_boundary):
    if lower_boundary <= value <= upper_boundary:
        return None
    else:
        dist = min(abs(lower_boundary - value), abs(value - upper_boundary))
        try:
            frac = dist / abs(upper_boundary - lower_boundary)
        except ZeroDivisionError:
            frac = 1
        logging.debug(
            f"_count_deviation({value}, {lower_boundary}, {upper_boundary}): dist={dist} frac={frac}"
        )
        return frac


def _check_by_min_max(data, value):
    logging.debug(f"data={data} and value={value}")
    mean = statistics.mean(data)
    lower_boundary = float(mean - (mean - min(data)))
    upper_boundary = float(mean + (max(data) - mean))
    logging.info(
        f"value={value}, data len={len(data)} mean={mean:.03f}, i.e. boundaries={lower_boundary:.03f}--{upper_boundary:.03f}"
    )
    info = collections.OrderedDict(
        [
            ("method", inspect.stack()[1][3]),
            ("value", value),
            ("data len", len(data)),
            ("data mean", mean),
            ("data min", float(min(data))),
            ("data max", float(max(data))),
            ("lower_boundary", lower_boundary),
            ("upper_boundary", upper_boundary),
        ]
    )
    return lower_boundary <= value <= upper_boundary, info


def check_by_min_max_0_1(data, value):
    return _check_by_min_max(data, value)


def check(methods, data, value, description="N/A", verbose=True):
    assert value is not None, "Value to check should not be None"

    if methods == []:
        methods = ["check_by_min_max_0_1"]
    for method in methods:
        assert method in globals(), f"Check method '{method}' not defined"

    results = []
    info_all = []
    for method in methods:
        result, info = globals()[method](data, value)
        results.append(result)
        logging.info(f"{method} value {value} returned {'PASS' if result else 'FAIL'}")

        info_full = collections.OrderedDict()
        info_full["description"] = description
        info_full["result"] = "PASS" if result else "FAIL"
        info_full.update(info)
        info_full["deviation"] = _count_deviation(
            value, info["lower_boundary"], info["upper_boundary"]
        )
        info_all.append(info_full)
    return results, info_all
