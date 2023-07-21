import json
import pytest


async def test_create_user(client, get_user_from_database):
    user_data = {
        "username": "Serega",
        "email": "lol@kek.com",
        "password": "SamplePass1!",
    }
    resp = client.post("/users/", content=json.dumps(user_data))
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["username"] == user_data["username"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True
    assert data_from_resp["is_admin"] is False
    assert data_from_resp["is_superuser"] is False
    users_from_db = await get_user_from_database(data_from_resp["id"])
    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["username"] == user_data["username"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is True
    assert user_from_db["is_admin"] is False
    assert user_from_db["is_superuser"] is False
    assert user_from_db["id"] == data_from_resp["id"]


@pytest.mark.parametrize(
    "user_data, user_data_same, expected_status_code, expected_detail",
    [
        (
                {"username": "Serega", "email": "lol@kek.com", "password": "SamplePass1!"},
                {"username": "Maksim", "email": "lol@kek.com", "password": "SamplePass1!"},
                409,
                {"detail": "This email is already registered"}
        ),
        (
                {"username": "Serega", "email": "lol@kek.com", "password": "SamplePass1!"},
                {"username": "Serega", "email": "lol@kek2.com", "password": "SamplePass1!"},
                409,
                {"detail": "This username is already registered"}
        ),

    ]
)
async def test_create_user_duplicate_data_error(client,
                                                get_user_from_database,
                                                user_data,
                                                user_data_same,
                                                expected_status_code,
                                                expected_detail):
    resp = client.post("/users/", content=json.dumps(user_data))
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["username"] == user_data["username"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True
    assert data_from_resp["is_admin"] is False
    assert data_from_resp["is_superuser"] is False
    users_from_db = await get_user_from_database(data_from_resp["id"])
    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["username"] == user_data["username"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is True
    assert user_from_db["is_admin"] is False
    assert user_from_db["is_superuser"] is False
    assert user_from_db["id"] == data_from_resp["id"]
    resp = client.post("/users/", content=json.dumps(user_data_same))
    assert resp.status_code == expected_status_code
    assert resp.json() == expected_detail


@pytest.mark.parametrize(
    "user_data_for_creation, expected_status_code, expected_detail",
    [
        (
                {"username": 'Serg', "email": "lol@kek.com"},
                422,
                {"detail": "Username must be more than 4 characters"}
        ),
        (
                {},
                422,
                {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": [
                                "body",
                                "username"
                            ],
                            "msg": "Field required",
                            "input": {},
                            "url": "https://errors.pydantic.dev/2.0.3/v/missing"
                        },
                        {
                            "type": "missing",
                            "loc": [
                                "body",
                                "email"
                            ],
                            "msg": "Field required",
                            "input": {},
                            "url": "https://errors.pydantic.dev/2.0.3/v/missing"
                        },
                        {
                            "type": "missing",
                            "loc": [
                                "body",
                                "password"
                            ],
                            "msg": "Field required",
                            "input": {},
                            "url": "https://errors.pydantic.dev/2.0.3/v/missing"
                        }
                    ]
                },
        ),
        (
                {"username": 'Serega', "email": "lol"},
                422,
                {
                    "detail": [
                        {
                            "type": "value_error",
                            "loc": [
                                "body",
                                "email"
                            ],
                            "msg": "value is not a valid email address: The email address is not valid. It must have exactly one @-sign.",
                            "input": "lol",
                            "ctx": {
                                "reason": "The email address is not valid. It must have exactly one @-sign."
                            }
                        },
                        {
                            "type": "missing",
                            "loc": [
                                "body",
                                "password"
                            ],
                            "msg": "Field required",
                            "input": {
                                "username": "Serega",
                                "email": "lol"
                            },
                            "url": "https://errors.pydantic.dev/2.0.3/v/missing"
                        }
                    ]
                },
        ),
    ],
)
async def test_create_user_validation_error(
        client, user_data_for_creation, expected_status_code, expected_detail
):
    resp = client.post("/users/", content=json.dumps(user_data_for_creation))
    data_from_resp = resp.json()
    assert resp.status_code == expected_status_code
    assert data_from_resp == expected_detail
