import json

from slugify import slugify

from tests.conftest import create_test_auth_headers_for_user


async def test_create_post(client,
                           create_user_in_database,
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
        "title": "sometitle",
        "text": "some_text",
        "short_description": "some_description",
    }
    await create_user_in_database(**user_data)
    resp = client.post("/posts/", content=json.dumps(post_data),
                       headers=create_test_auth_headers_for_user(
                           user_data["username"]))
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["title"] == post_data["title"]
    assert data_from_resp["text"] == post_data["text"]
    assert data_from_resp["short_description"] == \
           post_data["short_description"]
    assert data_from_resp["author_id"] == user_data["id"]
    assert data_from_resp["slug"] == slugify(post_data["title"])
    post_from_db = await get_post_from_database(data_from_resp["id"])
    assert len(post_from_db) == 1
    user_from_db = dict(post_from_db[0])
    assert user_from_db["title"] == post_data["title"]
    assert user_from_db["text"] == post_data["text"]
    assert user_from_db["short_description"] == post_data["short_description"]
    assert user_from_db["author_id"] == user_data["id"]
    assert user_from_db["slug"] == slugify(post_data["title"])
    assert user_from_db["id"] == data_from_resp["id"]
