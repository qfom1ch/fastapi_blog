import shutup; shutup.please()
import datetime

import pytest

from tests.conftest import create_test_auth_headers_for_user


@pytest.mark.parametrize(
    "type_finding, data_for_finding",
    [
        (
                "user_id",
                "id"
        ),
        (
                "user_email",
                "email"
        ),
        (
                "username",
                "username"
        ),
    ]
)
async def test_get_user(client,
                        create_user_in_database,
                        type_finding,
                        data_for_finding):
    user_data = {
        "id": 1,
        "username": "Serega",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": False,
        "is_superuser": False,
    }
    await create_user_in_database(**user_data)
    resp = client.get(
        f"/users/?{type_finding}={user_data[data_for_finding]}")
    assert resp.status_code == 200
    user_from_response = resp.json()
    assert user_from_response["id"] == user_data["id"]
    assert user_from_response["username"] == user_data["username"]
    assert user_from_response["email"] == user_data["email"]
    assert user_from_response["is_active"] is True
    assert user_from_response["is_admin"] is False
    assert user_from_response["is_superuser"] is False


@pytest.mark.parametrize(
    "type_finding, fake_data_for_finding",
    [
        (
                "user_id",
                15
        ),
        (
                "user_email",
                "fake@mail.com"
        ),
        (
                "username",
                "fakename"
        ),
    ]
)
async def test_get_user_not_found(client,
                                  create_user_in_database,
                                  type_finding,
                                  fake_data_for_finding):
    user_data = {
        "id": 1,
        "username": "Serega",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": False,
        "is_superuser": False,
    }
    await create_user_in_database(**user_data)
    resp = client.get(
        f"/users/?{type_finding}={fake_data_for_finding}")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "User not found."}


async def test_get_all_users_list(client, create_user_in_database):
    user_data1 = {
        "id": 1,
        "username": "Serega",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": False,
        "is_superuser": False,
    }
    user_data2 = {
        "id": 2,
        "username": "Maksim",
        "email": "kek@lol.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": True,
        "is_superuser": False,
    }
    for user_data in [user_data1, user_data2]:
        await create_user_in_database(**user_data)
    resp = client.get("/users/list")
    assert resp.status_code == 200
    assert resp.json() == \
           {
               "items": [
                   {
                       "id": 1,
                       "username": "Serega",
                       "email": "lol@kek.com",
                       "is_active": True,
                       "is_admin": False,
                       "is_superuser": False
                   },
                   {
                       "id": 2,
                       "username": "Maksim",
                       "email": "kek@lol.com",
                       "is_active": True,
                       "is_admin": True,
                       "is_superuser": False
                   }
               ],
               "total": 2,
               "page": 1,
               "size": 50,
               "pages": 1
           }


async def test_get_users_me_posts(client,
                                  create_user_in_database,
                                  create_post_in_database):
    user_data = {
        "id": 1,
        "username": "Serega",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "is_admin": False,
        "is_superuser": False,
    }
    post_data1 = {
        "id": 1,
        "author_id": user_data["id"],
        "slug": "someslug",
        "title": "sometitle",
        "text": "some_text",
        "short_description": "some_description",
        "published_at": datetime.date(2023, 5, 15),
    }
    post_data2 = {
        "id": 2,
        "author_id": user_data["id"],
        "slug": "someslug2",
        "title": "sometitle2",
        "text": "some_text2",
        "short_description": "some_description2",
        "published_at": datetime.date(2022, 5, 15),
    }
    await create_user_in_database(**user_data)
    await create_post_in_database(**post_data1)
    await create_post_in_database(**post_data2)
    resp = client.get("/users/me/posts",
                      headers=create_test_auth_headers_for_user(user_data["username"]))
    assert resp.status_code == 200
    assert resp.json() == {
        "items": [
            {
                "id": 1,
                "author_id": 1,
                "title": "sometitle",
                "text": "some_text",
                "short_description": "some_description",
                "slug": "someslug",
                "published_at": "2023-05-14T21:00:00Z",
            },
            {
                "id": 2,
                "author_id": 1,
                "title": "sometitle2",
                "text": "some_text2",
                "short_description": "some_description2",
                "slug": "someslug2",
                "published_at": "2022-05-14T21:00:00Z",
            }
        ],
        "total": 2,
        "page": 1,
        "size": 50,
        "pages": 1
    }
