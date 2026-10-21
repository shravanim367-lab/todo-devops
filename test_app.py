import pytest
import app as todo_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(
        todo_app, "DB_PATH", str(tmp_path / "test.db")
    )
    todo_app.init_db()
    todo_app.app.config["TESTING"] = True

    with todo_app.app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"My To-Do List" in response.data


def test_add_task(client):
    client.post("/add", data={"title": "Study DevOps"})
    response = client.get("/")
    assert b"Study DevOps" in response.data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"todo_tasks_added_total" in response.data