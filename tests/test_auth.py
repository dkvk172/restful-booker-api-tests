from api.auth_api import AuthAPI

def test_login_success(config, token):
    assert token

def test_login_wrong_username(config, logger):
    resp = AuthAPI(config, logger).login("wrong","password123")
    assert resp.status_code == 200
    assert "token" not in resp.json()

def test_login_wrong_password(config, logger):
    resp = AuthAPI(config, logger).login("admin", "wrong")
    assert resp.status_code == 200
    assert "token" not in resp.json()

def test_login_with_empty(config, logger):
    resp = AuthAPI(config, logger).login("","")
    assert resp.status_code == 200
    assert "token" not in resp.json()

def test_login_no_need_auth(config, logger, booking_api,booking_payload):
    resp = booking_api.create(booking_payload)
    assert resp.status_code == 200
    assert "bookingid" in resp.json()