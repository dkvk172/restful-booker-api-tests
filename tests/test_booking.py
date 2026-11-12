import pytest

@pytest.mark.endpoint("POST /booking")
def test_create_booking(booking_api,booking_payload):
    resp = booking_api.create(booking_payload)
    assert resp.status_code == 200
    assert resp.json()["booking"]["firstname"] == booking_payload["firstname"]

@pytest.mark.endpoint("GET /booking/{id}")
def test_get_booking(booking_api,booking_payload,create_booking):
    resp = booking_api.get(create_booking)
    assert resp.status_code == 200
    assert resp.json()["lastname"] == booking_payload["lastname"]

@pytest.mark.endpoint("PUT /booking/{id}")
def test_update_booking(booking_api,booking_payload,create_booking,token):
    booking_payload["firstname"] = "Updated"
    resp = booking_api.update(create_booking,booking_payload,token)
    assert resp.status_code == 200
    assert booking_api.get(create_booking).json()["firstname"] == "Updated"

@pytest.mark.endpoint("PUT /booking/{id}")
def test_update_booking_no_auth(booking_api,booking_payload,create_booking):
    booking_payload["firstname"] = "Updated"
    resp = booking_api.update(create_booking,booking_payload)
    assert resp.status_code == 403
    assert booking_api.get(create_booking).json()["firstname"] == "Jim"

@pytest.mark.endpoint("DELETE /booking/{id}")
def test_delete_booking(booking_api,create_booking,token):
    resp = booking_api.delete(create_booking, token)
    assert resp.status_code == 201
    check = booking_api.get(create_booking)
    assert check.status_code == 404

@pytest.mark.endpoint("DELETE /booking/{id}")
def test_delete_booking_no_auth(booking_api,create_booking):
    resp = booking_api.delete(create_booking)
    assert resp.status_code == 403

@pytest.mark.endpoint("POST /booking")
@pytest.mark.xfail(strict=True,reason="非法日期，应返回400，实际返回200")
def test_create_booking_with_invalid_date(booking_api,booking_payload):
    booking_payload["bookingdates"]["checkin"]="2025-13-41"
    resp = booking_api.create(booking_payload)
    assert resp.status_code == 400

@pytest.mark.endpoint("PUT /booking/{id}")
@pytest.mark.xfail(strict=True, reason="checkin晚于checkout，应返回400，实际返回200")
def test_update_booking_with_invalid_checkin(booking_api, booking_payload, create_booking, token):
    booking_payload["bookingdates"]["checkin"]="2026-03-01"
    resp = booking_api.update(create_booking,booking_payload,token)
    assert resp.status_code == 400



