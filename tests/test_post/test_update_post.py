import datetime
import json

from slugify import slugify

from tests.conftest import create_test_auth_headers_for_user


async def test_update_post(client,
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
    post_data_updated = {
        "title": "update_title",
        "text": "update_text",
        "short_description": "update_description"
    }
    await create_user_in_database(**user_data)
    await create_post_in_database(**post_data)
    resp = client.patch(
        f"/posts/?post_id={post_data['id']}",
        content=json.dumps(post_data_updated),
        headers=create_test_auth_headers_for_user(user_data["username"]),
    )
    assert resp.status_code == 200
    data_from_resp = resp.json()
    assert data_from_resp["id"] == post_data["id"]
    posts_from_db = await get_post_from_database(user_data["id"])
    post_from_db = dict(posts_from_db[0])
    assert post_from_db["id"] == post_data["id"]
    assert post_from_db["author_id"] == user_data["id"]
    assert post_from_db["title"] == post_data_updated["title"]
    assert post_from_db["text"] == post_data_updated["text"]
    assert post_from_db["short_description"] == \
           post_data_updated["short_description"]
    assert post_from_db["slug"] == slugify(post_data_updated["title"])


async def test_update_post_not_found_error(client,
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
    post_data_updated = {
        "title": "update_title",
        "text": "update_text",
        "short_description": "update_description"
    }
    await create_user_in_database(**user_data)
    await create_post_in_database(**post_data)
    fake_post_id = 15
    resp = client.patch(
        f"/posts/?post_id={fake_post_id}",
        content=json.dumps(post_data_updated),
        headers=create_test_auth_headers_for_user(user_data["username"]),
    )
    assert resp.status_code == 404
    resp_data = resp.json()
    assert resp_data == {"detail": f"Post with id {fake_post_id} not found."}
