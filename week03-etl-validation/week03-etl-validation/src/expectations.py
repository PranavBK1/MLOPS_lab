from dataclasses import dataclass


@dataclass
class Violation:
    expectation: str      # name of the check, e.g. "expect_column_not_null"
    column: str            # which column it was checking
    row_index: int          # index into the rows list where it failed
    detail: str              # short human-readable reason


def _is_null(value):
    return value is None or (isinstance(value, str) and value.strip() == "")


def expect_column_not_null(rows, column):
    """Return a Violation for every row where rows[i][column] is null/empty."""
    # TODO: implement
    violations = []

    for i, row in enumerate(rows):
        value = row.get(column)

        if _is_null(value):
            violations.append(
                Violation(
                    expectation="expect_column_not_null",
                    column=column,
                    row_index=i,
                    detail=f"{column} is null or empty",
                )
            )

    return violations
    # raise NotImplementedError


def expect_column_positive(rows, column):
    """Return a Violation for every row where rows[i][column], cast to float,
    is not strictly greater than 0. If the value can't be cast to float at
    all, that also counts as a violation (detail should say so).
    """
    # TODO: implement
    violations = []

    for i, row in enumerate(rows):
        value = row.get(column)

        try:
            number = float(value)
        except (TypeError, ValueError):
            violations.append(
                Violation(
                    expectation="expect_column_positive",
                    column=column,
                    row_index=i,
                    detail=f"{column} cannot be cast to float: {value!r}",
                )
            )
            continue

        if number <= 0:
            violations.append(
                Violation(
                    expectation="expect_column_positive",
                    column=column,
                    row_index=i,
                    detail=f"{column} must be greater than 0, got {value!r}",
                )
            )

    return violations

    # raise NotImplementedError


def expect_column_in_set(rows, column, allowed_values):
    """Return a Violation for every row where rows[i][column] is not a member
    of allowed_values (a set or list you're given).
    """
    # TODO: implement
    violations = []

    for i, row in enumerate(rows):
        value = row.get(column)

        if value not in allowed_values:
            violations.append(
                Violation(
                    expectation="expect_column_in_set",
                    column=column,
                    row_index=i,
                    detail=f"{column} has invalid value: {value!r}",
                )
            )

    return violations
    # raise NotImplementedError


def expect_column_unique(rows, column):
    """Return a Violation for every row AFTER THE FIRST that repeats a value
    already seen in `column`. (i.e. if three rows share a value, rows 2 and 3
    are violations; row 1 is not.)
    """
    # TODO: implement
    violations = []
    seen = set()

    for i, row in enumerate(rows):
        value = row.get(column)

        if value in seen:
            violations.append(
                Violation(
                    expectation="expect_column_unique",
                    column=column,
                    row_index=i,
                    detail=f"{column} contains duplicate value: {value!r}",
                )
            )
        else:
            seen.add(value)

    return violations
    # raise NotImplementedError