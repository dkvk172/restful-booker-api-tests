import pytest
from api.ping_api import PingAPI

@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.endpoint("GET /ping")
def test_ping(config,logger):
    resp = PingAPI(config,logger).ping()
    assert resp.status_code == 201
