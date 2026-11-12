import pytest
from api.auth_api import AuthAPI

@pytest.mark.endpoint("POST /auth")
def test_login_success(config, token):
    assert token

@pytest.mark.endpoint("POST /auth")
def test_login_wrong_username(config, logger):
    resp = AuthAPI(config, logger).login("wrong","password123")
    assert resp.status_code == 200
    assert "token" not in resp.json()

@pytest.mark.endpoint("POST /auth")
def test_login_wrong_password(config, logger):
    resp = AuthAPI(config, logger).login("admin", "wrong")
    assert resp.status_code == 200
    assert "token" not in resp.json()

@pytest.mark.endpoint("POST /auth")
def test_login_with_empty(config, logger):
    resp = AuthAPI(config, logger).login("","")
    assert resp.status_code == 200
    assert "token" not in resp.json()

@pytest.mark.endpoint("POST /booking")
def test_login_no_need_auth(config, logger, booking_api,booking_payload):
    resp = booking_api.create(booking_payload)
    assert resp.status_code == 200
    assert "bookingid" in resp.json()