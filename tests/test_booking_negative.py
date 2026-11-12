import pytest

from utils.data_loader import build_payload, get_path, load_cases

CASES = load_cases("booking_cases")


def _params():
    params = []
    for case in CASES:
        marks = []
        if case.get("xfail"):
            marks.append(
                pytest.mark.xfail(strict=True, reason=case.get("reason", case["id"]))
            )
        params.append(pytest.param(case, id=case["id"], marks=marks))
    return params


@pytest.mark.endpoint("POST /booking")
@pytest.mark.parametrize("case", _params())
def test_create_booking_negative(case, booking_api, booking_payload):
    payload = build_payload(booking_payload, case)
    resp = booking_api.create(payload)

    expected_status = case["expected"]["status"]
    assert resp.status_code == expected_status, (
        f"{case['id']} 期望 {expected_status}，实际 {resp.status_code}，"
        f"body={resp.text[:300]}"
    )

    for path, value in (case.get("expected_body") or {}).items():
        assert get_path(resp.json(), path) == value, (
            f"{case['id']} 字段 {path} 期望 {value}，实际 {resp.text[:300]}"
        )