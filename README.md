# restful-booker 接口自动化测试框架

[![api-tests](https://github.com/dkvk172/restful-booker-api-tests/actions/workflows/api-tests.yml/badge.svg)](https://github.com/dkvk172/restful-booker-api-tests/actions/workflows/api-tests.yml)

基于 **pytest + requests** 的接口自动化测试框架，对 [restful-booker](https://github.com/mwinteringham/restful-booker) 的 8 个接口做功能、异常、鉴权、内容协商与缺陷验证。当前 **47 条用例 / 8 个端点**，其中 **19 条 `strict xfail`** 用于固化 15 个服务端已知缺陷；GitHub Actions 每次 push 自动拉起被测服务并运行全部用例。

详细的用例设计见 [`docs/test-matrix.md`](docs/test-matrix.md)（78 行用例矩阵、缺陷台账 DEF-001~015）。

## 项目亮点

- **分层设计**：`BaseAPI` 统一 base_url / 超时 / session / token / 日志，业务层只描述接口
- **数据驱动**：`data/*.yaml` 描述用例，`utils/data_loader.py` 负责加载与 payload 变换；参数化 id 直接复用矩阵 ID（如 `TC-BOOK-POST-002`），用例与矩阵双向可追溯
- **夹具治理**：session 级 token 复用；`make_booking` 工厂用 `uuid` 造唯一数据，`yield` 统一清理，跑两遍结果一致
- **缺陷可追踪**：服务端问题用 `xfail(strict=True)` 固化，reason 带 DEF 编号；将来修好会以 `XPASS` 报警
- **CI 可复现**：固定被测版本 SHA + `npm ci` + 启动健康检查（60s 硬失败），失败仍上传 HTML 报告

## 被测对象

| 项 | 值 |
|---|---|
| 服务 | restful-booker（Node + Express + LokiJS 内存库） |
| 版本 | `00461155995c8636866bf51dc444f63033da44fb`（固定 SHA） |
| 地址 | `http://localhost:3001` |
| 数据 | 重启即清空；`npm start` 会 seed 10 条随机数据 |

固定 SHA 的原因：上游 `main` 会变，锁定版本才能保证「本地绿 = CI 绿」。升级顺序：改 SHA → 本地跑绿 → 再提 PR。

## 技术栈

Python 3.12+ · pytest · requests · PyYAML · pytest-html · GitHub Actions · Node 22（被测服务）

> `requirements.txt` 里的 `jsonschema` / `allure-pytest` / `pytest-xdist` / `faker` 已安装，供 W3 的 schema、报告、并行、数据工厂使用（见 Roadmap），当前版本尚未接入。

## 目录结构

```text
.
├── api/                    # 接口对象层（base / auth / booking / ping）
├── config/                 # settings.yaml（base_url、账号、超时）
├── data/                   # 测试数据：booking.yaml + booking_cases.yaml + patch_cases.yaml
├── docs/                   # test-matrix.md（用例矩阵 + 缺陷台账）
├── scripts/                # stats.py（按端点/marker 统计用例）
├── tests/                  # 用例 + conftest.py（token / make_booking / 清理）
├── utils/                  # 配置加载、日志、数据加载与参数化
├── .github/workflows/      # api-tests.yml（CI）
├── pytest.ini              # 用例路径、marker、HTML 报告
└── requirements.txt
```

## 快速开始

### 1. 启动被测服务

```bash
git clone https://github.com/mwinteringham/restful-booker.git
cd restful-booker
git checkout 00461155995c8636866bf51dc444f63033da44fb
npm ci
npm start            # http://localhost:3001
```

### 2. 安装依赖并运行测试

```powershell
git clone https://github.com/dkvk172/restful-booker-api-tests.git
cd restful-booker-api-tests
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
```

预期结果：`28 passed, 19 xfailed`；HTML 报告生成在 `reports/report.html`。

常用命令：

```powershell
pytest -m smoke                          # 冒烟（8 条）
pytest -m contract                       # 契约类
pytest -k "TC-BOOK-LIST-008"             # 按矩阵 ID 单跑
python scripts/stats.py --total-endpoints 8   # 生成 reports/stats.md
```

## 用例覆盖

| 模块 | 端点 | 覆盖场景 | 用例数 | 其中 xfail |
|---|---|---|---|---|
| 健康检查 | `GET /ping` | 服务存活（201） | 1 | 0 |
| 认证 | `POST /auth` | 正确凭据、错误用户名、错误密码、空值 | 4 | 0 |
| 预订列表 | `GET /booking` | 无过滤、firstname/lastname/日期过滤、组合、边界、非法参数、Accept | 14 | 3 |
| 预订详情 | `GET /booking/:id` | 正确获取 | 1 | 0 |
| 创建 | `POST /booking` | 最小必填、6 个必填字段缺失、类型/日期/字符串边界、trim | 12 | 9 |
| 更新 | `PUT /booking/:id` | 全量更新、无 token 403、checkin 晚于 checkout | 3 | 1 |
| 部分更新 | `PATCH /booking/:id` | 多字段/单字段、类型错误、无 token、不存在 id、Accept 四态、落库校验 | 10 | 6 |
| 删除 | `DELETE /booking/:id` | 删除成功、无 token 403 | 2 | 0 |
| **合计** | 8 个端点 | 正向 / 逆向 / 边界 / 权限 / 契约 | **47** | **19** |

> `pytest -q` 的 `28 passed` 来自正向与已确认行为；19 条 xfailed 全部对应真实缺陷，不是“跑不过就 xfail”。

## 已知缺陷（节选）

| 缺陷 | 用例 | 期望 | 实际 |
|---|---|---|---|
| DEF-001 | POST-002~007 | 400 | **500**（缺必填） |
| DEF-002 | POST-008 / PUT-008 | 400 | 200，checkin 变 `0NaN-aN-aN` |
| DEF-008 | LIST-011 | 等值 checkin 应包含 | 不包含（`$gt` + 字符串比较） |
| DEF-010 | POST-017 / 021 | 400 | 200，`parseInt` 静默转换 |
| DEF-013 | PATCH-011 | 406 且不落库 | **500 但数据已修改** |
| DEF-014 | PATCH-010 | 200 + 表单串 | 200 + `formurlencoded is not a function` |

完整 15 条见 [`docs/test-matrix.md`](docs/test-matrix.md) §5；每条均有 `strict xfail` 用例作为证据。

## CI 说明

- 触发：`push` / `pull_request`
- 步骤：checkout → Python 3.12 / Node 22 → 拉取固定版本服务 → `npm ci` → 健康检查 → 安装依赖 → `pytest` → 上传报告
- 证据：Actions 日志出现 `restful-booker up @ 0046115…`；Artifacts 下载 `report`（`report.html`）
- 失败排查：先在本地用同样的 SHA 起服务复跑，再看 run 里哪个 step 变红

> xfail 不影响退出码，因此 19 条已知缺陷用例不会让 CI 变红；缺陷修复后 strict 模式会转为 XPASS 并让 CI 失败，提醒更新用例。

## 设计说明

- **为什么分层**：接口路径、请求参数、断言的变化频率不同；`BaseAPI` 改一处，业务层不用动。
- **为什么数据驱动**：用例输入与断言分离，新增一条只需改 YAML；`pytest.param(id=矩阵 ID)` 让报告、`-k` 过滤、矩阵回填共用同一标识。
- **为什么 session 级 token**：restful-booker 的 token 不随请求失效，每个用例重复登录纯属浪费。
- **为什么 xfail 而不是 skip**：skip 只是不跑；`strict=True` 是「已知缺陷」契约，服务端修好后会 XPASS 变红，提醒你更新用例。
- **为什么固定 SHA**：可复现是自动化的底线；否则上游一次提交就能让你的 CI 无故变红。

## Roadmap

- [x] 用例矩阵 + 参数化数据层（78 行 / 47 条）
- [x] 缺陷 strict xfail 固化（15 个缺陷 / 19 条用例）
- [x] 统计脚本 `scripts/stats.py`（按端点 / marker）
- [ ] 用例矩阵 60+（当前 47，差 13：详情 6、POST 8、PUT 6、DELETE 2、auth 2）
- [ ] JSON Schema 响应结构校验（T12）
- [ ] 统一断言 helper `expect_status / expect_keys / expect_schema`（T13）
- [ ] 数据工厂（faker）与清理注册表（T20/T21）
- [ ] 多环境切换（`--env`）与敏感信息环境变量化（T22）
- [ ] Allure 报告 + `pytest-xdist` 并行（T24/T25）
- [ ] GitHub Issues 缺陷单与矩阵 Issue 列（T19）

## 已知限制

- 契约测试目前只覆盖状态码 / Content-Type / 列表项结构，未做响应体 JSON Schema 校验
- 详情端点（`GET /booking/:id`）与 PUT/DELETE 的权限矩阵尚未补齐，端点覆盖 8/8 但深度不均
- 尚未接入 Allure 与并行执行
- 被测服务为第三方练习项目，缺陷只能以 xfail 固化，不能直接修复

## 致谢

被测服务 [restful-booker](https://github.com/mwinteringham/restful-booker)（Mark Winteringham）；本仓库仅用于学习与工程实践。
