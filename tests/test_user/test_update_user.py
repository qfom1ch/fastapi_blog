import json

import pytest

from tests.conftest import create_test_auth_headers_for_user


async def test_update_user(client,
                           create_user_in_database,
                           get_user_from_database):
    user_data = {
        "id": 1,
        "username": "Serega",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": False,
        "is_superuser": False,
        "is_verified_email": False,
    }
    user_data_updated = {
        "username": "Maksim",
        "email": "cheburek@kek.com"
    }
    await create_user_in_database(**user_data)
    resp = client.patch(
        f"/users/?user_id={user_data['id']}",
        content=json.dumps(user_data_updated),
        headers=create_test_auth_headers_for_user(user_data["username"]),
    )
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data["id"] == user_data["id"]
    users_from_db = await get_user_from_database(user_data["id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["username"] == user_data_updated["username"]
    assert user_from_db["email"] == user_data_updated["email"]
    assert user_from_db["is_active"] is user_data["is_active"]
    assert user_from_db["is_admin"] is user_data["is_admin"]
    assert user_from_db["is_superuser"] is user_data["is_superuser"]
    assert user_from_db["is_verified_email"] is user_data["is_verified_email"]
    assert user_from_db["id"] == user_data["id"]


async def test_update_user_not_found_error(client, create_user_in_database):
    user_data = {
        "id": 1,
        "username": "Serega",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": False,
        "is_superuser": False,
        "is_verified_email": False,
    }
    user_data_updated = {
        "username": "Maksim",
        "email": "cheburek@kek.com"
    }
    await create_user_in_database(**user_data)
    fake_user_id = 15
    resp = client.patch(
        f"/users/?user_id={fake_user_id}",
        data=json.dumps(user_data_updated),
        headers=create_test_auth_headers_for_user(user_data["username"]),
    )
    assert resp.status_code == 404
    resp_data = resp.json()
    assert resp_data == {"detail": f"User with id {fake_user_id} not found."}


@pytest.mark.parametrize(
    "string_to_update, expected_detail",
    [
        (
                "email",
                {"detail": "This email is already registered"}

        ),
        (
                "username",
                {"detail": "This username is already registered"}

        )
    ]
)
async def test_update_user_duplicate_data_error(client,
                                                create_user_in_database,
                                                string_to_update,
                                                expected_detail):
    user_data1 = {
        "id": 1,
        "username": "Serega",
        "email": "lolol@kekek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": False,
        "is_superuser": False,
        "is_verified_email": False,
    }
    user_data2 = {
        "id": 2,
        "username": "Maksim",
        "email": "kek@lol.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": True,
        "is_superuser": False,
        "is_verified_email": False,
    }
    user_data_updated = {
        string_to_update: user_data2[string_to_update],
    }
    for user_data in [user_data1, user_data2]:
        await create_user_in_database(**user_data)
    resp = client.patch(
        f"/users/?user_id={user_data1['id']}",
        data=json.dumps(user_data_updated),
        headers=create_test_auth_headers_for_user(user_data1["username"]),
    )
    assert resp.status_code == 409
    assert resp.json() == expected_detail
