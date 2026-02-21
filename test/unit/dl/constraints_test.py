from test import mock_data

import grammdb
import pytest
from grammdb.exceptions import (
    CheckConstraintError,
    NotNullConstraintError,
    UniqueConstraintError,
    constraint_error,
)

from pykc.dl import (
    db,
    tables,
)


def non_empty_text_data():
    return {
        "members": {
            "ApiToken": ["hash", "jwt"],
            "Member": ["moniker", "discord_id"],
        },
        "events": {
            "Event": ["title", "description", "location_details"],
            "Recurring": ["title", "description"],
            "Venue": [
                "address_line1",
                "address_line2",
                "address_line3",
                "city",
                "name",
                "postal_code",
                "state",
            ],
        },
    }


def no_null_repr_text_data():
    data = non_empty_text_data()
    data["members"]["Member"] += ["pronouns", "first_name", "last_name"]
    return data


def url_is_https_data():
    return {
        "events": {
            "Event": ["external_link"],
            "Venue": ["external_link"],
        },
    }


def not_null_data():
    return {
        "members": {
            "ApiToken": ["hash", "jwt"],
            "Member": ["first_name", "last_name", "moniker", "pronouns"],
        },
        "events": {
            "Event": [
                "title",
                "description",
                "start",
                "end",
                "is_cancelled",
                "is_av_capable",
            ],
            "Recurring": [
                "title",
                "description",
                "interval_type",
                "start_time",
                "end_time",
            ],
            "Venue": [
                "address_line1",
                "city",
                "name",
                "postal_code",
                "state",
                "external_link",
            ],
        },
    }


def unique_data():
    return {
        "members": {
            "ApiToken": ["hash", "jwt"],
            "Member": ["moniker", "discord_id"],
        },
        "events": {
            "Event": ["external_link"],
            "Recurring": ["title"],
            "Venue": ["name"],
        },
    }


def _generate_check_test_cases(data_mapping, bad_val, match_str):
    input_data = mock_data.resources()["new"]
    return [
        pytest.param(
            {**input_data[table_name], column_name: bad_val},
            getattr(db, db_name),
            getattr(tables, table_name),
            match_str,
            id=f"{match_str}-{table_name}-{column_name}-{'""' if bad_val == "" else bad_val}",
        )
        for db_name, v in data_mapping.items()
        for table_name, columns in v.items()
        for column_name in columns
    ]


def _generate_not_null_test_cases(data_mapping):
    input_data = mock_data.resources()["new"]
    bad_val = None
    return [
        pytest.param(
            {**input_data[table_name], column_name: bad_val},
            getattr(db, db_name),
            getattr(tables, table_name),
            id=f"{table_name}-{column_name}",
        )
        for db_name, v in data_mapping.items()
        for table_name, columns in v.items()
        for column_name in columns
    ]


def _generate_unique_test_cases(data_mapping):
    input_data = mock_data.resources()["seed"]
    return [
        pytest.param(
            input_data[table_name][0],
            getattr(db, db_name),
            getattr(tables, table_name),
            id=f"{table_name}-{column_name}",
        )
        for db_name, v in data_mapping.items()
        for table_name, columns in v.items()
        for column_name in columns
    ]


def check_constraint_test_cases():
    return [
        *_generate_check_test_cases(non_empty_text_data(), "", "text_is_not_an_empty_string"),
        *_generate_check_test_cases(
            no_null_repr_text_data(), "None", "text_is_not_a_string_representation_of_null"
        ),
        *_generate_check_test_cases(
            no_null_repr_text_data(), "null", "text_is_not_a_string_representation_of_null"
        ),
        *_generate_check_test_cases(
            no_null_repr_text_data(), "NULL", "text_is_not_a_string_representation_of_null"
        ),
        *_generate_check_test_cases(
            no_null_repr_text_data(), "nil", "text_is_not_a_string_representation_of_null"
        ),
        *_generate_check_test_cases(url_is_https_data(), "http://www.example.com", "url_is_https"),
    ]


def not_null_constraint_test_cases():
    return _generate_not_null_test_cases(not_null_data())


def unique_constraint_test_cases():
    return _generate_unique_test_cases(unique_data())


@pytest.mark.parametrize("create_payload,db_factory,table,match_str", check_constraint_test_cases())
async def test_check_constraints(create_payload, db_factory, table, match_str):
    with pytest.raises(CheckConstraintError, match=match_str):
        with constraint_error():
            async with db_factory().new_connection() as conn:
                async with conn.begin():
                    stmt = grammdb.insert(into=table, **create_payload)
                    await conn.execute(stmt)


@pytest.mark.parametrize("create_payload,db_factory,table", not_null_constraint_test_cases())
async def test_not_null_constraints(create_payload, db_factory, table):
    with pytest.raises(NotNullConstraintError):
        with constraint_error():
            async with db_factory().new_connection() as conn:
                async with conn.begin():
                    stmt = grammdb.insert(into=table, **create_payload)
                    await conn.execute(stmt)


async def test_login_method_requirements():
    create_payload = {
        **mock_data.resources()["new"]["Member"],
        "discord_id": 999,
        "password_hash": mock_data.mock_pw_hash(),
    }
    del create_payload["discord_id"]
    del create_payload["password_hash"]
    with pytest.raises(CheckConstraintError, match="login_method_required"):
        with constraint_error():
            async with db.members().new_connection() as conn:
                async with conn.begin():
                    stmt = grammdb.insert(into=tables.Member, **create_payload)
                    await conn.execute(stmt)


@pytest.mark.parametrize("field_name", ["first_name", "last_name"])
async def test_name_required_for_password_login(field_name):
    create_payload = {
        **mock_data.resources()["new"]["Member"],
        "password_hash": mock_data.mock_pw_hash(),
    }
    del create_payload[field_name]
    with pytest.raises(CheckConstraintError, match="name_non_null"):
        with constraint_error():
            async with db.members().new_connection() as conn:
                async with conn.begin():
                    stmt = grammdb.insert(into=tables.Member, **create_payload)
                    await conn.execute(stmt)


@pytest.mark.parametrize("create_payload,db_factory,table", unique_constraint_test_cases())
async def test_unique_constraints(create_payload, db_factory, table):
    with pytest.raises(UniqueConstraintError):
        with constraint_error():
            async with db_factory().new_connection() as conn:
                async with conn.begin():
                    stmt = grammdb.insert(into=table, **create_payload)
                    await conn.execute(stmt)
