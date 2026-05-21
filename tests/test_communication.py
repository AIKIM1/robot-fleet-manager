from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.communication.rest_api import router, set_fleet_manager
from src.fleet.manager import FleetManager


def test_list_robots():
    fm = FleetManager(max_robots=2)
    fm.register_robot("Bot1", "models/test.xml", robot_id="bot1")
    set_fleet_manager(fm)
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    res = client.get("/api/robots")
    assert res.status_code == 200
    assert res.json()[0]["id"] == "bot1"
