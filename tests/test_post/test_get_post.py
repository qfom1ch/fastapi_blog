import datetime

import pytest


@pytest.mark.parametrize(
    "type_finding, data_for_finding",
    [
        (
                "post_id",
                "id"
        ),
        (
                "post_title",
                "title"
        ),
        (
                "post_slug",
                "slug"
        ),
    ]
)
async def test_get_post(client,
                        create_user_in_database,
                        create_post_in_database,
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
    resp = client.get(f"/posts/?{type_finding}={post_data[data_for_finding]}")
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["id"] == post_data["id"]
    assert data_from_resp["author_id"] == user_data["id"]
    assert data_from_resp["title"] == post_data["title"]
    assert data_from_resp["text"] == post_data["text"]
    assert data_from_resp["short_description"] == \
           post_data["short_description"]
    assert data_from_resp["slug"] == post_data["slug"]


@pytest.mark.parametrize(
    "type_finding, fake_data_for_finding",
    [
        (
                "post_id",
                15
        ),
        (
                "post_title",
                "faketitle"
        ),
        (
                "post_slug",
                "fakeslug"
        ),
    ]
)
async def test_get_post_not_found(client,
                                  create_user_in_database,
                                  create_post_in_database,
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
    resp = client.get(f"/posts/?{type_finding}={fake_data_for_finding}")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Post not found."}


async def test_get_all_posts_list(client,
                                  create_user_in_database,
                                  create_post_in_database):
    user_data1 = {
        "id": 1,
        "username": "Serega",
        "email": "lol@kek.com",
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
        "is_admin": False,
        "is_superuser": False,
        "is_verified_email": False,
    }
    post_data1 = {
        "id": 1,
        "author_id": user_data1["id"],
        "slug": "someslug",
        "title": "sometitle",
        "text": "some_text",
        "short_description": "some_description",
        "published_at": datetime.date(2023, 5, 15),
    }
    post_data2 = {
        "id": 2,
        "author_id": user_data2["id"],
        "slug": "someslug2",
        "title": "sometitle2",
        "text": "some_text2",
        "short_description": "some_description2",
        "published_at": datetime.date(2022, 5, 15),
    }
    for user_data in [user_data1, user_data2]:
        await create_user_in_database(**user_data)
    for post_data in [post_data1, post_data2]:
        await create_post_in_database(**post_data)
    resp = client.get("/posts/list")
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
                "published_at": "2023-05-14T21:00:00Z"
            },
            {
                "id": 2,
                "author_id": 2,
                "title": "sometitle2",
                "text": "some_text2",
                "short_description": "some_description2",
                "slug": "someslug2",
                "published_at": "2022-05-14T21:00:00Z"
            }
        ],
        "total": 2,
        "page": 1,
        "size": 50,
        "pages": 1
    }


async def test_get_posts_by_user_id(client,
                                    create_user_in_database,
                                    create_post_in_database):
    user_data1 = {
        "id": 1,
        "username": "Serega",
        "email": "lol@kek.com",
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
        "is_admin": False,
        "is_superuser": False,
        "is_verified_email": False,
    }
    post_data1 = {
        "id": 1,
        "author_id": user_data1["id"],
        "slug": "someslug",
        "title": "sometitle",
        "text": "some_text",
        "short_description": "some_description",
        "published_at": datetime.date(2023, 5, 15),
    }
    post_data2 = {
        "id": 2,
        "author_id": user_data2["id"],
        "slug": "someslug2",
        "title": "sometitle2",
        "text": "some_text2",
        "short_description": "some_description2",
        "published_at": datetime.date(2022, 5, 15),
    }
    for user_data in [user_data1, user_data2]:
        await create_user_in_database(**user_data)
    for post_data in [post_data1, post_data2]:
        await create_post_in_database(**post_data)
    resp = client.get(f"/posts/user_id?user_id={user_data1['id']}")
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
                "published_at": "2023-05-14T21:00:00Z"
            }
        ],
        "total": 1,
        "page": 1,
        "size": 50,
        "pages": 1
    }
