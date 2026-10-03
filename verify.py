"""
task-manager.verify
~~~~~~~~~~~~~~~~~~~

This module contains test to verify functionality of the app.
"""

from app import create_app


C = create_app().test_client()
"""Creates a testing instance of the application."""


def test_create_signup_user():
    """Tests signup.""" 
    resp = C.post("/signup", json={"email": "jdlservs@gmail.com", "password": "Josiah1940"})
    assert resp.status_code == 201


def test_login_user():
    """Tests login."""
    resp = C.post("/login", json={"email": "a@b.com", "password": "hunter2"})
    assert resp.status_code == 200


def test_add_user_task():
    """Tests add task functionality."""
    resp = C.post("/login", json={"email": "a@b.com", "password": "hunter2"})
    assert resp.status_code == 200, resp.json
    assert resp.json is not None, "login returned no body"
    token = resp.json.get("access_token")

    r1 = C.post("/tasks", json={"title": "test"}, headers={"Authorization": f"Bearer {token}"})
    assert r1.status_code == 201, r1.json

    r2 = C.post("/tasks", json={"title": "   "}, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 400, r2.json


def test_update_tasks():
    """Tests update task functionality."""
    resp = C.post("/login", json={"email": "a@b.com", "password": "hunter2"})
    assert resp.status_code == 200, resp.json
    assert resp.json is not None, "login returned no body"

    token = resp.json.get("access_token")

    r1 = C.put("/tasks/1", json={"completed": True}, headers={"Authorization": f"Bearer {token}"})
    assert r1.status_code == 200, r1.json
    
    r2 = C.put("/tasks/1", json={"completed": "ee"}, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 400, r2.json
    
    r3 = C.put("/tasks/1", json={"completed": ""}, headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 400, r3.json

test_login_user()
