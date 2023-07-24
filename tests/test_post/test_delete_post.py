import datetime

import pytest

from tests.conftest import create_test_auth_headers_for_user


async def test_delete_post(client,
                           create_user_in_database,
                           create_post_in_database,
                           get_post_from_database):
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
    post_data = {
        "id": 1,
        "author_id": user_data["id"],
        "slug": "someslug",
        "title": "sometitle",
        "text": "some_text",
        "short_description": "some_description",
        "published_at": datetime.date(2023, 5, 15),
    }
    await create_user_in_database(**user_data)
    await create_post_in_database(**post_data)
    resp = client.delete(
        f"/posts/?post_id={post_data['id']}",
        headers=create_test_auth_headers_for_user(user_data["username"]),
    )
    assert resp.status_code == 200
    posts_from_db = await get_post_from_database(post_data["id"])
    assert len(posts_from_db) == 0


async def test_delete_post_no_jwt(client,
                                  create_user_in_database,
                                  create_post_in_database,
                                  get_post_from_database):
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
    post_data = {
        "id": 1,
        "author_id": user_data["id"],
        "slug": "someslug",
        "title": "sometitle",
        "text": "some_text",
        "short_description": "some_description",
        "published_at": datetime.date(2023, 5, 15),
    }
    await create_user_in_database(**user_data)
    await create_post_in_database(**post_data)
    resp = client.delete(f"/posts/?post_id={post_data['id']}")
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
async def test_delete_post_by_another_user_error(
        client,
        create_user_in_database,
        user_for_deletion,
        user_who_delete,
        create_post_in_database,
):
    post_data = {
        "id": 1,
        "author_id": user_for_deletion["id"],
        "slug": "someslug",
        "title": "sometitle",
        "text": "some_text",
        "short_description": "some_description",
        "published_at": datetime.date(2023, 5, 15),
    }
    for user_data in [user_for_deletion, user_who_delete]:
        await create_user_in_database(**user_data)
    await create_post_in_database(**post_data)
    resp = client.delete(
        f"/posts/?post_id={post_data['id']}",
        headers=create_test_auth_headers_for_user(user_who_delete["username"]),
    )
    assert resp.status_code == 403
