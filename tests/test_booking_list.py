import uuid

import pytest

FUTURE_IN = "2027-05-01"    # 未来日期：seed 的 checkin 只到 now，查这个区间不会混入种子数据
FUTURE_OUT = "2027-05-10"


def _ids(resp):
    assert resp.status_code == 200, f"期望 200，实际 {resp.status_code}，body={resp.text[:200]}"
    data = resp.json()
    assert isinstance(data, list), f"列表接口应返回数组，实际 {type(data).__name__}"
    return [item["bookingid"] for item in data]


@pytest.mark.smoke
@pytest.mark.endpoint("GET /booking")
def test_list_returns_id_array(booking_api):
    """无过滤：200 + 数组，每项只有 bookingid；不断言条数（seed 数量是环境配置，不是契约）。"""
    data = booking_api.list().json()
    assert isinstance(data, list)
    assert all(set(item) == {"bookingid"} for item in data)
    ids = [item["bookingid"] for item in data]
    assert len(ids) == len(set(ids)), "bookingid 不应重复"


@pytest.mark.contract
@pytest.mark.endpoint("GET /booking")
def test_list_item_contract(booking_api):
    """列表项结构：bookingid 必须是 int（不是字符串数字，也不是嵌套对象）。"""
    data = booking_api.list().json()
    assert data, "列表为空，无法校验结构；确认 SUT 用 npm start（SEED=true）启动"
    for item in data:
        assert list(item.keys()) == ["bookingid"]
        assert isinstance(item["bookingid"], int)

@pytest.mark.endpoint("GET /booking")
def test_list_filter_by_firstname(booking_api, make_booking):
    a = make_booking()                       # firstname 是随机唯一值
    ids = _ids(booking_api.list(firstname=a["payload"]["firstname"]))
    assert ids == [a["id"]], f"唯一 firstname 应只命中自己，实际 {ids}"


@pytest.mark.endpoint("GET /booking")
def test_list_filter_by_lastname(booking_api, make_booking):
    a = make_booking(lastname=f"L{uuid.uuid4().hex[:8]}")
    ids = _ids(booking_api.list(lastname=a["payload"]["lastname"]))
    assert ids == [a["id"]]


@pytest.mark.endpoint("GET /booking")
def test_list_filter_by_two_fields(booking_api, make_booking):
    a = make_booking(lastname=f"Combo{uuid.uuid4().hex[:8]}")
    ids = _ids(
        booking_api.list(
            firstname=a["payload"]["firstname"],
            lastname=a["payload"]["lastname"],
        )
    )
    assert ids == [a["id"]], "多条件是 AND，应只命中同时满足的那条"


@pytest.mark.endpoint("GET /booking")
def test_list_no_match_returns_empty(booking_api):
    ids = _ids(booking_api.list(firstname=f"nobody-{uuid.uuid4().hex[:8]}"))
    assert ids == [], f"无匹配应返回空数组，实际 {ids}"


@pytest.mark.endpoint("GET /booking")
def test_list_filter_checkin_after(booking_api, make_booking):
    """checkin 过滤语义：返回 checkin > 查询值的记录。"""
    a = make_booking(bookingdates={"checkin": FUTURE_IN, "checkout": FUTURE_OUT})
    ids = _ids(booking_api.list(checkin="2026-12-01"))
    assert a["id"] in ids, f"2027-05-01 的预订应满足 checkin > 2026-12-01，实际 {ids}"


@pytest.mark.endpoint("GET /booking")
def test_list_filter_checkout_before(booking_api, make_booking):
    a = make_booking(bookingdates={"checkin": "2026-01-01", "checkout": "2026-01-05"})
    ids = _ids(booking_api.list(checkout="2026-02-01"))
    assert a["id"] in ids


@pytest.mark.endpoint("GET /booking")
def test_list_filter_date_range(booking_api, make_booking):
    a = make_booking(bookingdates={"checkin": "2026-01-01", "checkout": "2026-01-05"})
    ids = _ids(booking_api.list(checkin="2025-12-01", checkout="2026-02-01"))
    assert a["id"] in ids, "区间内（checkin>12-01 且 checkout<02-01）应命中"


@pytest.mark.xfail(strict=True, reason="checkin 等值被 $gt 排除，应包含（≥ 语义）；DEF-008")
@pytest.mark.endpoint("GET /booking")
def test_list_checkin_equal_boundary(booking_api, make_booking):
    a = make_booking(bookingdates={"checkin": FUTURE_IN, "checkout": FUTURE_OUT})
    ids = _ids(booking_api.list(checkin=FUTURE_IN))
    assert ids == [a["id"]], (
        f"checkin 等于查询值应包含 {a['id']}，实际 {ids}；"
        "根因：查询值转 ISO 字符串与库内 YYYY-MM-DD 做字符串 $gt 比较"
    )


@pytest.mark.endpoint("GET /booking")
def test_list_checkout_equal_boundary(booking_api, make_booking):
    """checkout 等值会被包含——但这是字符串比较的巧合（"07-12" < "07-12T..."），不是 <= 语义。"""
    a = make_booking(bookingdates={"checkin": FUTURE_IN, "checkout": FUTURE_OUT})
    ids = _ids(booking_api.list(checkout=FUTURE_OUT))
    assert a["id"] in ids

@pytest.mark.xfail(strict=True, reason="非法日期实测 500，应然 400；new Date('abc').toISOString() 抛 RangeError 未被捕获，DEF-007")
@pytest.mark.endpoint("GET /booking")
def test_list_invalid_checkin(booking_api):
    resp = booking_api.list(checkin="abc")
    assert resp.status_code == 400, f"实际 {resp.status_code}，body={resp.text[:120]}"


@pytest.mark.endpoint("GET /booking")
def test_list_ignores_unknown_params(booking_api, make_booking):
    """未声明参数应被忽略，不影响结果集。"""
    a = make_booking()
    ids = _ids(booking_api.list(totalprice=100))
    assert a["id"] in ids, "totalprice 不是合法过滤参数，应被忽略而不是过滤掉数据"


@pytest.mark.xfail(strict=True, reason="列表接口忽略 Accept，恒返回 JSON；应如详情接口返回 XML，DEF-009")
@pytest.mark.endpoint("GET /booking")
def test_list_accept_xml(booking_api):
    resp = booking_api.list(accept="application/xml")
    assert resp.headers["Content-Type"].startswith("application/xml"), (
        f"实际 Content-Type={resp.headers.get('Content-Type')}"
    )