from sqlalchemy import CheckConstraint


def text_nonempty(column_name: str) -> CheckConstraint:
    return CheckConstraint(f"{column_name} <> ''", name="text_is_not_an_empty_string")


def text_no_null_repr(column_name: str) -> CheckConstraint:
    return CheckConstraint(
        f"lower({column_name}) NOT IN ('null', 'nil', 'nul', 'none')",
        name="text_is_not_a_string_representation_of_null",
    )


def url_is_https(column_name: str) -> CheckConstraint:
    return CheckConstraint(f"substr(lower({column_name}), 1, 8) = 'https://'", name="url_is_https")


def timestamps_consistency() -> CheckConstraint:
    return CheckConstraint("updated_at >= created_at", name="timestamps_consistency")


def integer_range(col_name: str, low: int, high: int) -> CheckConstraint:
    return CheckConstraint(
        f"({col_name} > {low}) AND ({col_name} < {high})", name=f"{col_name}_range"
    )


def relative_time(timestamp1: str, timestamp2: str) -> CheckConstraint:
    return CheckConstraint(
        f"{timestamp1} <= {timestamp2}", name=f"{timestamp1}_{timestamp2}_relative_dates"
    )


def some_non_null(*column_names) -> CheckConstraint:
    clauses = [f"({col_name} IS NOT NULL)" for col_name in column_names]
    return CheckConstraint(" OR ".join(clauses), name="some_non_null")


def enum_member(col_name: str, enum_class) -> CheckConstraint:
    valid_values = ", ".join([f"'{i.value}'" for i in enum_class])
    return CheckConstraint(f"{col_name} IN ({valid_values})", name=f"{col_name}_enum_member")
