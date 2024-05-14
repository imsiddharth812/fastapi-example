from app import schemas
import pytest


def test_get_all_posts(authorized_client, test_posts):
    response = authorized_client.get("/posts")

    # print(response.json())
    def validate(post: dict):
        return schemas.PostOut(**post)

    posts_map = map(validate, response.json())
    posts_list = list(posts_map)
    assert len(response.json()) == len(test_posts)
    assert response.status_code == 200
    assert posts_list[1].Post.id == test_posts[1].id
    assert posts_list[2].Post.title == test_posts[2].title


def test_unauthorised_user_get_all_posts(client, test_posts):
    response = client.get("/posts")
    assert response.status_code == 401


def test_unauthorised_user_get_one_post(client, test_posts):
    response = client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401


def test_one_post_not_exist(authorized_client, test_posts):
    response = authorized_client.get("/posts/55")
    assert response.status_code == 404


def test_get_one_post_(authorized_client, test_posts):
    response = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostOut(**response.json())
    assert response.status_code == 200
    assert post.Post.id == test_posts[0].id
    assert post.Post.title == test_posts[0].title
    assert post.Post.content == test_posts[0].content


@pytest.mark.parametrize(
    "title, content, published",
    [
        ("Awesome new title", "Awesome new content", True),
        ("Awesome second title", "Awesome second content", False),
    ],
)
def test_create_post(authorized_client, test_user, title, content, published):
    response = authorized_client.post(
        "/posts",
        json={
            "title": title,
            "content": content,
            "published": published,
        },
    )
    new_post = schemas.Post(**response.json())
    # print(new_post.title)
    # print(new_post.content)
    assert response.status_code == 201
    assert new_post.title == title
    assert new_post.content == content
    assert new_post.published == published
    assert new_post.owner_id == test_user["id"]


def test_create_post_default_published_true(authorized_client):
    response = authorized_client.post(
        "/posts",
        json={
            "title": "published",
            "content": "test default value of published",
        },
    )
    new_post = schemas.Post(**response.json())
    assert response.status_code == 201
    assert new_post.published == True


def test_unauthorised_user_create_post(client):
    response = client.post(
        "/posts",
        json={
            "title": "published",
            "content": "test default value of published",
        },
    )
    assert response.status_code == 401


def test_delete_post_success(authorized_client, test_posts):
    response = authorized_client.delete(f"/posts/{test_posts[1].id}")
    assert response.status_code == 204


def test_unauthorised_user_delete_post(client, test_posts):
    response = client.delete(f"/posts/{test_posts[1].id}")
    assert response.status_code == 401


def test_delete_post_non_exist(authorized_client):
    response = authorized_client.delete("/posts/444")
    assert response.status_code == 404


def test_delete_other_user_post(authorized_client, test_posts, test_user):
    response = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert response.status_code == 403


def test_update_post(authorized_client, test_posts):
    data = {"title": "updated title", "content": "updated content"}
    response = authorized_client.put(f"/posts/{test_posts[1].id}", json=data)
    updated_post = schemas.Post(**response.json())
    assert response.status_code == 200
    assert updated_post.id == test_posts[1].id
    assert updated_post.title == data["title"]
    assert updated_post.content == data["content"]


def test_update_other_user_post(authorized_client, test_posts, test_user):
    data = {"title": "updated title", "content": "updated content"}
    response = authorized_client.put(f"/posts/{test_posts[3].id}", json=data)
    assert response.status_code == 403


def test_unauthorised_user_update_post(client, test_posts):
    response = client.put(f"/posts/{test_posts[1].id}")
    assert response.status_code == 401


def test_update_post_non_exist(authorized_client, test_posts):
    data = {"title": "updated title", "content": "updated content"}
    response = authorized_client.put("/posts/444", json=data)
    assert response.status_code == 404
