from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_status_endpoint():
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "everything's good YAY"
    assert data["code"] == 200


def test_strikers_endpoint():
    response = client.get("/strikers")
    assert response.status_code == 200
    data = response.json()
    assert "strikers" in data
    assert isinstance(data["strikers"], list)
    assert len(data["strikers"]) > 0
    assert "Lauren James" in data["strikers"]


def test_recommend_endpoint_valid_player():
    response = client.post("/recommend", params={"playername": "Lauren James", "numberofrecs": 3})
    assert response.status_code == 200
    data = response.json()

    # target player stats verification
    assert data["target_player_stats"]["Player"] == "Lauren James"
    assert data["target_player_stats"]["Shots"] >= 15
    assert data["target_player_stats"]["Similarity"] == 100.0

    # recommendations list verification
    assert len(data["recommendations"]) == 3
    for rec in data["recommendations"]:
        assert "Player" in rec
        assert 0.0 <= rec["Similarity"] <= 100.0


def test_recommend_endpoint_invalid_limit():
    # numberofrecs=50 violates the Query(le=10) constraint
    response = client.post("/recommend", params={"playername": "Lauren James", "numberofrecs": 50})
    assert response.status_code == 422


def test_recommend_endpoint_invalid_player():
    # unknown player name rejected by Enum validation
    response = client.post("/recommend", params={"playername": "NonExistentPlayer", "numberofrecs": 3})
    assert response.status_code == 422
