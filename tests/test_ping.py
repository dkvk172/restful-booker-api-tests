from api.ping_api import PingAPI

def test_ping(config,logger):
    resp = PingAPI(config,logger).ping()
    assert resp.status_code == 201
