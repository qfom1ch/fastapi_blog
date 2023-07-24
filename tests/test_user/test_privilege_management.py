import pytest

from tests.conftest import create_test_auth_headers_for_user


async def test_add_admin_privilege_to_user_by_superuser(
        client, create_user_in_database, get_user_from_database
):
    user_data_for_promotion = {
        "id": 1,
        "username": "Serega",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": False,
        "is_superuser": False,
        "is_verified_email": False,
    }
    user_data_who_promoted = {
        "id": 2,
        "username": "Maksim",
        "email": "kek@lol.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": False,
        "is_superuser": True,
        "is_verified_email": True,
    }
    for user_data in [user_data_for_promotion, user_data_who_promoted]:
        await create_user_in_database(**user_data)
    resp = client.patch(
        f"/users/give_admin_privileges?user_id="
        f"{user_data_for_promotion['id']}",
        headers=create_test_auth_headers_for_user(
            user_data_who_promoted["username"]),
    )
    data_from_resp = resp.json()
    assert resp.status_code == 200
    updated_user_from_db = await get_user_from_database(data_from_resp["id"])
    assert len(updated_user_from_db) == 1
    updated_user_from_db = dict(updated_user_from_db[0])
    assert updated_user_from_db["id"] == user_data_for_promotion["id"]
    assert updated_user_from_db["is_admin"] is True


async def test_revoke_admin_privilege_from_user_by_superuser(
        client, create_user_in_database, get_user_from_database
):
    user_data_for_revoke = {
        "id": 1,
        "username": "Serega",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": True,
        "is_superuser": False,
        "is_verified_email": False,
    }
    user_data_who_revoke = {
        "id": 2,
        "username": "Maksim",
        "email": "kek@lol.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": False,
        "is_superuser": True,
        "is_verified_email": True,
    }
    for user_data in [user_data_for_revoke, user_data_who_revoke]:
        await create_user_in_database(**user_data)
    resp = client.delete(
        f"/users/remove_admin_privileges?user_id={user_data_for_revoke['id']}",
        headers=create_test_auth_headers_for_user(
            user_data_who_revoke["username"]),
    )
    data_from_resp = resp.json()
    assert resp.status_code == 200
    revoked_user_from_db = await get_user_from_database(data_from_resp["id"])
    assert len(revoked_user_from_db) == 1
    revoked_user_from_db = dict(revoked_user_from_db[0])
    assert revoked_user_from_db["id"] == user_data_for_revoke["id"]
    assert revoked_user_from_db["is_admin"] is False


@pytest.mark.parametrize(
    "privilege_of_who_revoke",
    [
        (
                False
        ),
        (
                True
        ),
    ],
)
async def test_revoke_admin_privilege_from_user_by_wrong_type_of_user(
        client, create_user_in_database, get_user_from_database,
        privilege_of_who_revoke
):
    user_data_for_revoke = {
        "id": 1,
        "username": "Serega",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": True,
        "is_superuser": False,
        "is_verified_email": False,
    }
    user_data_who_revoke = {
        "id": 2,
        "username": "Maksim",
        "email": "kek@lol.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": privilege_of_who_revoke,
        "is_superuser": False,
        "is_verified_email": False,
    }
    for user_data in [user_data_for_revoke, user_data_who_revoke]:
        await create_user_in_database(**user_data)
    resp = client.delete(
        f"/users/remove_admin_privileges?user_id={user_data_for_revoke['id']}",
        headers=create_test_auth_headers_for_user(
            user_data_who_revoke["username"]),
    )
    data_from_resp = resp.json()
    assert resp.status_code == 403
    assert data_from_resp == {"detail": "Forbidden."}
    not_revoked_user_from_db = await get_user_from_database(
        user_data_for_revoke["id"])
    assert len(not_revoked_user_from_db) == 1
    not_revoked_user_from_db = dict(not_revoked_user_from_db[0])
    assert not_revoked_user_from_db["id"] == user_data_for_revoke["id"]
    assert not_revoked_user_from_db["is_admin"] is True
