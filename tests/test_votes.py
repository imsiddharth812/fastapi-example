import pytest
from app import models


@pytest.fixture
def test_vote(test_posts, session, test_user):
    new_vote = models.Vote(post_id=test_posts[3].id, user_id=test_user["id"])
    session.add(new_vote)
    session.commit()


def test_authorised_user_vote(authorized_client, test_posts):
    data = {"post_id": test_posts[3].id, "dir": 1}
    response = authorized_client.post("/vote", json=data)
    assert response.status_code == 201


def test_unauthorised_user_vote(client, test_posts):
    data = {"post_id": test_posts[3].id, "dir": 1}
    response = client.post("/vote", json=data)
    assert response.status_code == 401


def test_vote_twice_post(authorized_client, test_posts, test_vote, test_user):
    data = {"post_id": test_posts[3].id, "dir": 1}
    response = authorized_client.post("/vote", json=data)
    assert response.status_code == 409


def test_delete_vote(authorized_client, test_posts, test_vote):
    data = {"post_id": test_posts[3].id, "dir": 0}
    response = authorized_client.post("/vote", json=data)
    assert response.status_code == 201


def test_delete_vote_not_exist(authorized_client, test_posts):
    data = {"post_id": test_posts[3].id, "dir": 0}
    response = authorized_client.post("/vote", json=data)
    assert response.status_code == 404


def test_vote_on_post_not_exist(authorized_client, test_posts):
    data = {"post_id": 44, "dir": 1}
    response = authorized_client.post("/vote", json=data)
    assert response.status_code == 404
