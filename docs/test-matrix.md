# restful-booker 接口测试用例矩阵

> 版本：v0.2 ｜ 更新：2026-11-10 ｜
> 被测服务：restful-booker @ `00461155995c8636866bf51dc444f63033da44fb`（localhost:3001）
> 需求来源：官方 API 文档 + SUT 源码（`routes/index.js`）+ 实测回填

## 0. 图例与规则

- **类型**：正向 P ｜ 逆向 N ｜ 边界 B ｜ 权限 A ｜ 契约 C
- **优先级**：P0 冒烟/主链路 ｜ P1 核心分支 ｜ P2 边缘
- **状态**：✅ 已自动化 ｜ ⬜ 待补 ｜ 🐞 已知缺陷(xfail) ｜ 🔍 待实测（预期未确认） ｜ ⛔ 不适用（附原因）
- **ID 规则**：`TC-<资源>-<方法>-<三位序号>`，如 `TC-BOOK-POST-001`
  - ID 一旦分配**不再修改**；用例函数重命名不影响追溯
- **预期原则**：填「契约应然」（REST 语义 / 官方文档）；实测 ≠ 应然 → 状态 🐞，备注写实测值 + 缺陷单链接
- **证据**：契约类行附 SUT 源码行号；缺陷行附复现命令

## 1. 端点清单（8 个）

| # | 方法   | 路径           | 是否鉴权         | 关键契约                                                  | 证据                      |
|---|--------|----------------|------------------|-----------------------------------------------------------|---------------------------|
| 1 | GET    | `/ping`        | 否               | 返回 201                                                  | routes                    |
| 2 | POST   | `/auth`        | 否               | 错误凭据仍 200 + `{"reason":"Bad credentials"}`           | `routes/index.js:659-671` |
| 3 | GET    | `/booking`     | 否               | 200 + 数组；支持 firstname/lastname/checkin/checkout 过滤 |                           |
| 4 | GET    | `/booking/:id` | 否               | 200 详情；Accept 决定格式；非法 Accept 418                |                           |
| 5 | POST   | `/booking`     | 否（可带 token） | 200 + `bookingid`；校验失败**实测 500**                   | `routes/index.js:319`     |
| 6 | PUT    | `/booking/:id` | 是               | 无 token 403；不存在的 id 405                             |                           |
| 7 | PATCH  | `/booking/:id` | 是               | 部分更新 200；无 token 403                                |                           |
| 8 | DELETE | `/booking/:id` | 是               | 成功 201；无 token 403                                    |                           |

## 2. 设计方法（这些行是怎么推导出来的）

- 正向P：正常 CRUD、最小必填、最大合法、幂等重放
- 逆向N：缺字段、空值、null、类型错误、非法 JSON、非法 Content-Type、不存在的资源
- 边界B：0 / 负数 / 最大整数 / 超长串 / Unicode / 日期边界（闰年、月末、跨年）
- 权限A：无 token / 错 token / Cookie / Basic / 大小写 header
- 契约C：状态码 + Content-Type + JSON Schema + 错误体结构 + 多余字段

## 3. 主矩阵

| ID                 | 端点                | 类型 | 测试点                                 | 输入/数据                                                  | 预期                                | 优先级 | 状态     | 代码位置                                                        | 备注                                                 |
|--------------------|---------------------|------|----------------------------------------|------------------------------------------------------------|-------------------------------------|--------|----------|-----------------------------------------------------------------|------------------------------------------------------|
| TC-PING-001        | GET /ping           | 正向 | 服务存活                               | 无                                                         | 201                                 | P0     | ✅       | tests/test_ping.py::test_ping                                   |                                                      |
| TC-AUTH-001        | POST /auth          | 正向 | 正确凭据换 token                       | admin/password123                                          | 200 + token                         | P0     | ✅       | tests/test_auth.py::test_login_success                          |                                                      |
| TC-AUTH-002        | POST /auth          | 逆向 | 错误用户名                             | wrong/password123                                          | 200 + reason=Bad credentials        | P1     | ✅       | tests/test_auth.py::test_login_wrong_username                   |                                                      |
| TC-AUTH-003        | POST /auth          | 逆向 | 错误密码                               | admin/wrong                                                | 200 + reason=Bad credentials        | P1     | ✅       | tests/test_auth.py::test_login_wrong_password                   |                                                      |
| TC-AUTH-004        | POST /auth          | 逆向 | 用户名密码为空值                       | ""/""                                                      | 200 + reason=Bad credentials        | P1     | ✅       | tests/test_auth.py::test_login_with_empty                       |                                                      |
| TC-AUTH-005        | POST /auth          | 契约 | 多余字段被忽略、仍发 token             | 正确凭据+extra=x                                           | 200 + token                         | P2     | ⬜       |                                                                 |                                                      |
| TC-AUTH-006        | POST /auth          | 契约 | 非法 JSON                              | Content-Type:application/json + body{bad json              | 400                                 | P2     | ⬜       |                                                                 |                                                      |
| TC-BOOK-LIST-001   | GET /booking        | 正向 | 无过滤列表                             | 无                                                         | 200 + 数组（不断言条数，seed 随机） | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-LIST-002   | GET /booking        | 正向 | 过滤条件为firstname                    | 先POST造一条唯一数据，再用该数据过滤。                     | 200                                 | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-LIST-003   | GET /booking        | 正向 | 过滤条件为lastname                     | 自造数据                                                   | 200                                 | P2     | ⬜       |                                                                 |                                                      |
| TC-BOOK-LIST-004   | GET /booking        | 正向 | 过滤条件为checkin                      | 造 checkin=2026-07-10，查 checkin=2026-07-01               | 200                                 | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-LIST-005   | GET /booking        | 正向 | 过滤条件为checkout                     | 自造数据                                                   | 200                                 | P2     | ⬜       |                                                                 |                                                      |
| TC-BOOK-LIST-006   | GET /booking        | 正向 | 多参数过滤                             | 先POST造一条唯一数据，再用该数据过滤。                     | 200                                 | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-LIST-007   | GET /booking        | 逆向 | 无匹配信息                             | /booking?checkin=2099-01-01                                | 200 + []                            | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-LIST-008   | GET /booking        | 逆向 | 非法日期                               | /booking?checkin=abc                                       | 500（应然 400 → 🐞 DEF）            | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-LIST-009   | GET /booking        | 契约 | 未声明参数被忽略                       | /booking?totalprice=100                                    | 200 + 全量数组                      | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-LIST-010   | GET /booking        | 契约 | Accept 忽略                            | 输入Accept:application/xml                                 | 200 + JSON 数组                     | P2     | ⬜       |                                                                 |                                                      |
| TC-BOOK-LIST-011   | GET /booking        | 边界 | 过滤日期相等                           | 造 checkin=2026-07-01 的预订，查同值                       | 200 且包含                          | P1     | 🔍       |                                                                 | $gt 预计不含 → DEF                                   |
| TC-BOOK-LIST-012   | GET /booking        | 边界 | checkout 相等日期                      | 造 checkout=2026-07-01，查同值                             | 200 且包含                          | P2     | ⬜       |                                                                 |                                                      |
| TC-BOOK-LIST-013   | GET /booking        | 正向 | 日期范围组合过滤                       | 造07-01~07-10，查checkin=2026-06-01&checkout=2026-07-20    | 200 且包含                          | P2     | ⬜       |                                                                 |                                                      |
| TC-BOOK-LIST-014   | GET /booking        | 契约 | 列表项结构                             | 无                                                         | 每项仅 bookingid（int）             | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-GET-001    | GET /booking/:id    | 正向 | 正确获得信息                           | /booking/{id}                                              | 200                                 | P0     | ✅       | tests/test_booking.py::test_get_booking                         |                                                      |
| TC-BOOK-GET-002    | GET /booking/:id    | 逆向 | 不存在的id                             | /booking/999999                                            | 404                                 | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-GET-003    | GET /booking/:id    | 逆向 | 非法id                                 | /booking/abc                                               | 404                                 | P1     | ⬜       |                                                                 | parseInt('abc')=NaN，证据 models:19                  |
| TC-BOOK-GET-004    | GET /booking/:id    | 边界 | 非法组合id                             | /booking/1abc                                              | 200 (需booking 1存在）              | P2     | 🔍       |                                                                 | parseInt('1abc')=1，命中 booking 1                   |
| TC-BOOK-GET-005    | GET /booking/:id    | 契约 | Accept: application/xml 返回XML        | application/xml                                            | 200 + xml body                      | P1     | ⬜       |                                                                 | res.send(string)的Content-Type可能是text/html        |
| TC-BOOK-GET-006    | GET /booking/:id    | 契约 | 非法 Accept                            | Accept: text/plain                                         | 418（契约现状）                     | P1     | ⬜       |                                                                 | 应然406 → DEF                                        |
| TC-BOOK-GET-007    | GET /booking/:id    | 契约 | Accept: urlencoded                     | application/x-www-form-urlencoded                          | 200 + 表单串                        | P2     | ⬜       |                                                                 | 响应Content-Type可能是 text/html（res.send(string)） |
| TC-BOOK-GET-008    | GET /booking/:id    | 边界 | id=0 / 负数                            | /booking/0 + /booking/-1                                   | 404                                 | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-POST-001   | POST /booking       | 正向 | 最小必填创建                           | data/booking.yaml                                          | 200 + bookingid                     | P0     | ✅       | tests/test_booking.py::test_create_booking                      |                                                      |
| TC-BOOK-POST-002   | POST /booking       | 逆向 | 缺firstname                            | 删字段后 POST  参数化一组（6 组）                          | 400                                 | P0     | ✅       | tests/test_booking_negative.py                                  | 实测 500 → DEF-001                                   |
| TC-BOOK-POST-003   | POST /booking       | 逆向 | 缺lastname                             | 删字段后 POST  参数化一组（6 组）                          | 400                                 | P1     | ✅       | tests/test_booking_negative.py                                  | 实测 500 → DEF-001                                   |
| TC-BOOK-POST-004   | POST /booking       | 逆向 | 缺totalprice                           | 删字段后 POST  参数化一组（6 组）                          | 400                                 | P1     | ✅       | tests/test_booking_negative.py                                  | 实测 500 → DEF-001                                   |
| TC-BOOK-POST-005   | POST /booking       | 逆向 | 缺depositpaid                          | 删字段后 POST  参数化一组（6 组）                          | 400                                 | P1     | ✅       | tests/test_booking_negative.py                                  | 实测 500 → DEF-001                                   |
| TC-BOOK-POST-006   | POST /booking       | 逆向 | 缺checkin                              | 删字段后 POST  参数化一组（6 组）                          | 400                                 | P1     | ✅       | tests/test_booking_negative.py                                  | 实测 500 → DEF-001                                   |
| TC-BOOK-POST-007   | POST /booking       | 逆向 | 缺checkout                             | 删字段后 POST  参数化一组（6 组）                          | 400                                 | P1     | ✅       | tests/test_booking_negative.py                                  | 实测 500 → DEF-001                                   |
| TC-BOOK-POST-008   | POST /booking       | 边界 | 非法日期                               | checkin=2025-13-41                                         | 400（实测 200 且 0NaN-aN-aN）       | P1     | 🐞 xfail | tests/test_booking.py::test_create_booking_with_invalid_date    |                                                      |
| TC-BOOK-POST-009   | POST /booking       | 边界 | checkin 晚于 checkout                  | checkin=2026-11-11 checkout=2026-03-01                     | 400                                 | P1     | 🔍       |                                                                 | 预计实测200 → DEF                                    |
| TC-BOOK-POST-010   | POST /booking       | 契约 | 额外字段                               | 合法 body + extra=x                                        | 200 + 响应体不含 extra 字段         | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-POST-011   | POST /booking       | 权限 | 无token创建预定                        | data/booking.yaml                                          | 200 + bookingid                     | P1     | ✅       | tests/test_auth.py::test_login_no_need_auth                     |                                                      |
| TC-BOOK-POST-012   | POST /booking       | 正向 | 正常创建text/xml                       | 表单body，Content-Type: text/xml                           | 200 + bookingid                     | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-POST-013   | POST /booking       | 边界 | application/xml 不拆包                 | Content-Type: application/xml                              | 待实测（预计 500，未走拆包分支）    | P2     | 🔍       |                                                                 |                                                      |
| TC-BOOK-POST-014   | POST /booking       | 逆向 | 非法JSONbody                           | Content-Type: application/json + body {bad                 | 400                                 | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-POST-015   | POST /booking       | 契约 | Accept                                 | Accept: application/xml                                    | 200 + created-booking XML           | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-POST-016   | POST /booking       | 契约 | 非法Accept                             | Accept: text/plain                                         | 418                                 | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-POST-017   | POST /booking       | 边界 | totalprice 字符串被静默转换            | totalprice: "111abc"                                       | 400                                 | P1     | ✅       |                                                                 | 实测 200 + 111 → DEF                                 |
| TC-BOOK-POST-018   | POST /booking       | 边界 | depositpaid 字符串转布尔               | depositpaid: "false"                                       | 400                                 | P1     | ⬜       |                                                                 | 实测200 + true → DEF                                 |
| TC-BOOK-POST-019   | POST /booking       | 正向 | application/x-www-form-urlencoded 创建 | 表单 body                                                  | 200 + bookingid                     | P2     | ⬜       |                                                                 |                                                      |
| TC-BOOK-POST-020   | POST /booking       | 边界 | firstname 前后空格被 trim              | " Jim "                                                    | 200 + 响应 "Jim"                    | P2     | ✅       | tests/test_booking_negative.py                                  |                                                      |
| TC-BOOK-POST-021   | POST /booking       | 边界 | totalprice 非数字 "abc"                | "abc"                                                      | 200 + 响应 null                     | P1     | ✅       | tests/test_booking_negative.py                                  |                                                      |
| TC-BOOK-POST-022   | POST /booking       | 逆向 | firstname 空串                         | ""                                                         | 500（应然 400）                     | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-PUT-001    | PUT /booking/:id    | 正向 | 更新信息                               | data/booking.yaml + 改firstname=Updated                    | 200 + firstname                     | P0     | ✅       | tests/test_booking.py::test_update_booking                      |                                                      |
| TC-BOOK-PUT-002    | PUT /booking/:id    | 逆向 | 缺字段                                 | 只传 firstname（缺其余 5 个必填）                          | 400                                 | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-PUT-003    | PUT /booking/:id    | 权限 | 无 token 更新                          | 无 Cookie                                                  | 403                                 | P0     | ✅       | tests/test_booking.py::test_update_booking_no_auth              |                                                      |
| TC-BOOK-PUT-004    | PUT /booking/:id    | 权限 | 错误token                              | Cookie: token=错误值                                       | 403                                 | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-PUT-005    | PUT /booking/:id    | 权限 | Cookie 有效 token                      | 先登录拿到的 完整 booking body + Cookie/Basic              | 200                                 | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-PUT-006    | PUT /booking/:id    | 权限 | Basic 有效                             | Authorization: Basic <base64>                              | 200                                 | P2     | ⬜       |                                                                 |                                                      |
| TC-BOOK-PUT-007    | PUT /booking/:id    | 逆向 | 更新不存在的 id                        | /booking/999999                                            | 404                                 | P1     | ⬜       |                                                                 | 实测 405 → DEF                                       |
| TC-BOOK-PUT-008    | PUT /booking/:id    | 边界 | 非法日期                               | checkin晚于checkout checkin=2026-03-01 checkout=2026-01-01 | 400（实测200）                      | P1     | 🐞 xfail | tests/test_booking.py::test_update_booking_with_invalid_checkin |                                                      |
| TC-BOOK-PUT-009    | PUT /booking/:id    | 正向 | Content-Type: text/xml 更新            | XML body + Basic                                           | 200                                 | P2     | ⬜       |                                                                 |                                                      |
| TC-BOOK-PUT-010    | PUT /booking/:id    | 权限 | Basic 错误（大小写/错值）              | Authorization: basic ...                                   | 403                                 | P2     | ⬜       |                                                                 |                                                      |
| TC-BOOK-PUT-011    | PUT /booking/:id    | 契约 | 不传additionalneeds更新                |                                                            | 200，但旧 additionalneeds 仍在      | P2     | ⬜       |                                                                 |                                                      |
| TC-BOOK-PATCH-001  | PATCH /booking/:id  | 正向 | 更新多个字段                           | {"firstname":"Patched","totalprice":"100"}                 | 200                                 | P0     | ⬜       |                                                                 |                                                      |
| TC-BOOK-PATCH-002  | PATCH /booking/:id  | 逆向 | 更新类型错误                           | {"totalprice":"abc"}                                       | 400                                 | P1     | 🔍       |                                                                 | 实测 200 → DEF                                       |
| TC-BOOK-PATCH-003  | PATCH /booking/:id  | 逆向 | 更新不存在的 id                        | /booking/999999                                            | 404                                 | P1     | ⬜       |                                                                 | 实测405 → DEF                                        |
| TC-BOOK-PATCH-004  | PATCH /booking/:id  | 权限 | 无token部分更新                        | 完整合法 body，不带任何认证头                              | 403                                 | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-PATCH-005  | PATCH /booking/:id  | 契约 | Accept: application/xml 返回 XML       | Accept: application/xml                                    | 200 + XML                           | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-PATCH-006  | PATCH /booking/:id  | 正向 | 只改firstname                          | {"firstname":"x"}                                          | 200 + 其余字段保持不变              | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-PATCH-007  | PATCH /booking/:id  | 契约 | 非法 Accept                            | Accept: text/plain                                         | 500；应然 406/418 → 🐞              | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-PATCH-008  | PATCH /booking/:id  | 边界 | 只传 bookingdates.checkin              | {"bookingdates":{"checkin":"2026-08-01"}}                  | 200 + checkout保留原值              | P1     | ⬜       |                                                                 | 预计checkout 丢失/变 0NaN                            |
| TC-BOOK-PATCH-009  | PATCH /booking/:id  | 边界 | 空body{}                               | {}                                                         | 200 no-op                           |        |          |                                                                 |                                                      |
| TC-BOOK-DELETE-001 | DELETE /booking/:id | 正向 | 删除预订                               | 已创建 id                                                  | 201，随后 GET 404                   | P0     | ✅       | tests/test_booking.py::test_delete_booking                      |                                                      |
| TC-BOOK-DELETE-002 | DELETE /booking/:id | 逆向 | 删除不存在的                           | /booking/999999                                            | 405（应然 404 → 🐞）                | P1     | ⬜       |                                                                 |                                                      |
| TC-BOOK-DELETE-003 | DELETE /booking/:id | 权限 | 无token删除                            | /booking/{id}                                              | 403                                 | P0     | ✅       | tests/test_booking.py::test_delete_booking_no_auth              |                                                      |
| TC-BOOK-DELETE-004 | DELETE /booking/:id | 边界 | 非法 id                                | /booking/abc                                               | 405（应然 404）                     | P1     | ⬜       |                                                                 |                                                      |
| TC-E2E-001         | 全链路              | 正向 | POST→GET→PUT→GET→DELETE→GET            |                                                            | 各步200/201/404一致                 |        |          |                                                                 |                                                      |

## 4. 覆盖统计

| 端点                | P  | N  | B  | A | C  | 合计  | 已自动化  |
|---------------------|----|----|----|---|----|-------|-----------|
| GET /ping           | 1  | 0  | 0  | 0 | 0  | 1     | 1         |
| POST /auth          | 1  | 3  | 0  | 0 | 2  | 6     | 4         |
| GET /booking        | 7  | 2  | 2  | 0 | 3  | 14    | 0         |
| GET /booking/:id    | 1  | 2  | 2  | 0 | 3  | 8     | 1         |
| POST /booking       | 3  | 8  | 7  | 1 | 3  | 22    | 3         |
| PUT /booking/:id    | 2  | 2  | 1  | 5 | 0  | 10    | 3         |
| PATCH /booking/:id  | 2  | 2  | 1  | 1 | 2  | 8     | 0         |
| DELETE /booking/:id | 1  | 1  | 1  | 1 | 0  | 4     | 2         |
| 合计                | 18 | 20 | 14 | 8 | 13 | 73    | 14        |

## 5. 缺陷台账

| 缺陷    | 对应用例                                      | 现象                              | 期望         | 实际           | 定性 | 状态 |
|---------|-----------------------------------------------|-----------------------------------|--------------|----------------|------|------|
| DEF-001 | POST-002~007                                  | POST 缺必填返回 500               | 400          | 500            |      |      |
| DEF-002 | POST-008 / POST-022 / PUT-008                 | 非法日期、空串被接受或 500	        | 400          | 200 / 500      |      |      |
| DEF-003 | POST-009 / PUT-008                            | checkin 晚于 checkout 被接受      | 400          | 200            |      |      |
| DEF-004 | PUT-007 / PATCH-003 / DELETE-002 / DELETE-004 | 不存在资源返回 405                | 404          | 405            |      |      |
| DEF-005 | PATCH-002                                     | PATCH 无校验，类型错误仍写入      | 400          | 200            |      |      |
| DEF-006 | PATCH-007                                     | 非法 Accept 返回 500              | 406/418      | 500            |      |      |
| DEF-007 | LIST-008                                      | 过滤非法日期返回 500              | 400          | 500            |      |      |
| DEF-008 | LIST-011                                      | checkin 相等日期不返回（文档 >=） | 包含         | 不包含         |      |      |
| DEF-009 | LIST-010                                      | 列表忽略 Accept（详情支持 XML）   | 一致         | JSON           |      |      |
| DEF-010 | POST-017 / POST-018 / POST-021                | 字符串被静默转换                  | 400          | 200            |      |      |
| DEF-011 | PATCH-008                                     | 嵌套部分更新丢 checkout           | 保留         | 丢失/0NaN      |      |      |
| DEF-012 | 全局                                          | 错误体只有纯文本状态消息          | 结构化错误码 | Bad Request 等 |      |      |

## 6. 缺口清单（⬜ 行 → 次日任务）

- [ ] `TC-BOOK-LIST-*`：列表 + 4 个过滤参数全部未写
- [ ] ...

## 7. 变更记录

| 日期 | 版本 | 变更 |
|---|---|---|