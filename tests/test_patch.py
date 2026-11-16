import pytest

from utils.data_loader import get_path, load_cases, parametrize_cases

CASES = load_cases("patch_cases")


@pytest.mark.regression
@pytest.mark.endpoint("PATCH /booking/{id}")
@pytest.mark.parametrize("case", parametrize_cases(CASES))
def test_patch(case, booking_api, booking_payload,create_booking,token):
    payload = case.get("set") or {}
    resp = booking_api.patch(create_booking, payload, token)

    expected_status = case["expected"]["status"]
    assert resp.status_code == expected_status, (
        f"{case['id']} 期望 {expected_status}，实际 {resp.status_code}，"
        f"body={resp.text[:300]}"
    )
    for path, value in (case.get("expected_body") or {}).items():
        assert get_path(resp.json(), path) == value, (
            f"{case['id']} 字段 {path} 期望 {value}，实际 {resp.text[:300]}"
        )

@pytest.mark.contract
@pytest.mark.endpoint("PATCH /booking/{id}")
def test_patch_no_auth(booking_api, create_booking):
    resp = booking_api.patch(create_booking, {"firstname": "Patched"})
    assert resp.status_code == 403

@pytest.mark.negative
@pytest.mark.endpoint("PATCH /booking/{id}")
def test_patch_nonexistent_id(booking_api, token):
    resp = booking_api.patch("999999", {"firstname": "Patched"}, token)
    assert resp.status_code == 405

@pytest.mark.contract
@pytest.mark.endpoint("PATCH /booking/{id}")
@pytest.mark.xfail(strict=True, reason="非法 Accept 实测 500，应然 406；DEF-006")
def test_patch_invalid_accept_returns_406(booking_api, create_booking, token):
    resp = booking_api.patch(
        create_booking, {"firstname": "Patched"}, token, accept="text/plain"
    )
    assert resp.status_code == 406, (
        f"非法 Accept 期望 406，实际 {resp.status_code}，body={resp.text[:200]}"
    )

@pytest.mark.contract
@pytest.mark.endpoint("PATCH /booking/{id}")
@pytest.mark.xfail(strict=True, reason="协商失败仍写库：先 update 后 parse，DEF-013")
def test_patch_invalid_accept_must_not_mutate(booking_api, create_booking, token):
    before = booking_api.get(create_booking).json()["firstname"]
    booking_api.patch(
        create_booking, {"firstname": "ShouldNotPersist"}, token, accept="text/plain"
    )
    after = booking_api.get(create_booking).json()["firstname"]
    assert after == before, (
        f"响应协商失败却已落库：{before} -> {after}"
        f"（routes/index.js:565-571，update 在 parse 之前）"
    )

@pytest.mark.contract
@pytest.mark.endpoint("PATCH /booking/{id}")
@pytest.mark.xfail(strict=True, reason="urlencoded 分支 TypeError 被当响应体返回 200；DEF-014")
def test_patch_accept_urlencoded_returns_form(booking_api, create_booking, token):
    resp = booking_api.patch(
        create_booking, {"firstname": "Patched"}, token,
        accept="application/x-www-form-urlencoded",
    )
    assert resp.status_code == 200
    assert "firstname=Patched" in resp.text, f"实际 body={resp.text[:120]}"

@pytest.mark.contract
@pytest.mark.endpoint("PATCH /booking/{id}")
@pytest.mark.xfail(strict=True, reason="XML 响应 Content-Type 是 text/html，DEF-015")
def test_patch_accept_xml_content_type(booking_api, create_booking, token):
    resp = booking_api.patch(
        create_booking, {"firstname": "Patched"}, token, accept="application/xml"
    )
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("application/xml"), (
        f"实际 Content-Type={resp.headers.get('Content-Type')}"
    )