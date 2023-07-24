import pytest

from tests.conftest import create_test_auth_headers_for_user


async def test_delete_user(client,
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
    await create_user_in_database(**user_data)
    resp = client.delete(
        f"/users/?user_id={user_data['id']}",
        headers=create_test_auth_headers_for_user(user_data["username"]),
    )
    assert resp.status_code == 200
    assert resp.json() == {"deleted_user_id": user_data["id"]}
    users_from_db = await get_user_from_database(user_data["id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["username"] == user_data["username"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is False
    assert user_from_db["is_admin"] is False
    assert user_from_db["is_superuser"] is False
    assert user_from_db["is_verified_email"] is False
    assert user_from_db["id"] == user_data["id"]


async def test_delete_user_no_jwt(client, create_user_in_database):
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
    await create_user_in_database(**user_data)
    resp = client.delete(
        f"/users/?user_id={user_data['id']}",
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated"}


@pytest.mark.parametrize(
    "user_for_deletion, user_who_delete",
    [
        (
                {
                    "id": 1,
                    "username": "Serega",
                    "email": "lol@kek.com",
                    "is_active": True,
                    "hashed_password": "SampleHashedPass",
                    "is_admin": False,
                    "is_superuser": False,
                    "is_verified_email": False,
                },
                {
                    "id": 2,
                    "username": "Maksim",
                    "email": "kek@lol.com",
                    "is_active": True,
                    "hashed_password": "SampleHashedPass",
                    "is_admin": False,
                    "is_superuser": False,
                    "is_verified_email": False,
                },
        ),
        (
                {
                    "id": 1,
                    "username": "Serega",
                    "email": "lol@kek.com",
                    "is_active": True,
                    "hashed_password": "SampleHashedPass",
                    "is_admin": False,
                    "is_superuser": True,
                    "is_verified_email": True,
                },
                {
                    "id": 2,
                    "username": "Maksim",
                    "email": "kek@lol.com",
                    "is_active": True,
                    "hashed_password": "SampleHashedPass",
                    "is_admin": True,
                    "is_superuser": False,
                    "is_verified_email": False,
                },
        ),
        (
                {
                    "id": 1,
                    "username": "Serega",
                    "email": "lol@kek.com",
                    "is_active": True,
                    "hashed_password": "SampleHashedPass",
                    "is_admin": True,
                    "is_superuser": False,
                    "is_verified_email": False,
                },
                {
                    "id": 2,
                    "username": "Maksim",
                    "email": "kek@lol.com",
                    "is_active": True,
                    "hashed_password": "SampleHashedPass",
                    "is_admin": True,
                    "is_superuser": False,
                    "is_verified_email": False,
                },
        ),
    ],
)
async def test_delete_another_user_error(
        client,
        create_user_in_database,
        user_for_deletion,
        user_who_delete,
):
    await create_user_in_database(**user_for_deletion)
    await create_user_in_database(**user_who_delete)
    resp = client.delete(
        f"/users/?user_id={user_for_deletion['id']}",
        headers=create_test_auth_headers_for_user(user_who_delete["username"]),
    )
    assert resp.status_code == 403


async def test_reject_delete_superadmin(
        client,
        create_user_in_database,
        get_user_from_database,
):
    user_for_deletion = {
        "id": 1,
        "username": "Serega",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": False,
        "is_superuser": True,
        "is_verified_email": False,
    }
    await create_user_in_database(**user_for_deletion)
    resp = client.delete(
        f"/users/?user_id={user_for_deletion['id']}",
        headers=create_test_auth_headers_for_user(
            user_for_deletion["username"]),
    )
    assert resp.status_code == 406
    assert resp.json() == {"detail": "Superadmin cannot be deleted via API."}
    user_from_database = await get_user_from_database(user_for_deletion["id"])
    assert dict(user_from_database[0])["is_superuser"] is True
