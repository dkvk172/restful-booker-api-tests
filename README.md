# restful-booker 接口自动化测试框架

[![api-tests](https://github.com/dkvk172/restful-booker-api-tests/actions/workflows/api-tests.yml/badge.svg)](https://github.com/dkvk172/restful-booker-api-tests/actions/workflows/api-tests.yml)

基于 **pytest + requests** 的接口自动化测试框架，对 [restful-booker](https://github.com/mwinteringham/restful-booker) 的 8 个接口做功能、异常、鉴权与缺陷验证。当前 **14 条用例 / 8 个端点**，其中 2 条 `strict xfail` 用于固化服务端已知缺陷；GitHub Actions 每次 push 自动拉起被测服务并运行全部用例。

## 项目亮点

- **分层设计**：`BaseAPI` 统一 base_url / 超时 / session / token / 日志，业务层只描述接口
- **夹具治理**：session 级 token 复用；`create_booking` 用 `yield` 做「造数 → 执行 → 清理」
- **缺陷可追踪**：服务端问题用 `xfail(strict=True)` 固化，将来修好会以 `XPASS` 报警
- **CI 可复现**：固定被测版本 SHA + `npm ci` + 启动健康检查（60s 硬失败），失败仍上传 HTML 报告
- **14 条用例全部接入 CI**，push / PR 自动执行

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

## 目录结构

```text
.
├── api/                    # 接口对象层（base / auth / booking / ping）
├── config/                 # settings.yaml（base_url、账号、超时）
├── data/                   # 测试数据（booking.yaml）
├── tests/                  # 用例 + conftest.py（token / 造数 / 清理）
├── utils/                  # 配置加载、日志
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

预期结果：`12 passed, 2 xfailed`；HTML 报告生成在 `reports/report.html`。

## 用例覆盖

| 模块 | 端点 | 覆盖场景 | 用例数 |
|---|---|---|---|
| 认证 | `POST /auth` | 正确凭据、错误用户名、错误密码、空值、免鉴权创建 | 5 |
| 预订 | `POST /booking`、`GET /booking/:id`、`PUT`、`DELETE` | CRUD、未授权 403、不存在 404/405、非法日期 | 8 |
| 健康检查 | `GET /ping` | 服务存活（返回 201） | 1 |

## 已知缺陷（strict xfail）

| 用例 | 期望 | 实际 | 影响 |
|---|---|---|---|
| 非法日期创建预订 | 400 | 200，且 checkin 被写成 `0NaN-aN-aN` | 脏数据入库 |
| checkin 晚于 checkout | 400 | 200 | 日期逻辑失效 |

> 根因：服务端只校验字段是否存在（`validationrules.js`），未校验日期格式与先后关系。缺陷单待补。

## CI 说明

- 触发：`push` / `pull_request`
- 步骤：checkout → Python 3.12 / Node 22 → 拉取固定版本服务 → `npm ci` → 健康检查 → 安装依赖 → `pytest` → 上传报告
- 证据：Actions 日志出现 `restful-booker up @ 0046115…`；Artifacts 下载 `report`（`report.html`）
- 失败排查：先在本地用同样的 SHA 起服务复跑，再看 run 里哪个 step 变红

## 设计说明

- **为什么分层**：接口路径、请求参数、断言的变化频率不同；`BaseAPI` 改一处，业务层不用动。
- **为什么 session 级 token**：restful-booker 的 token 不随请求失效，每个用例重复登录纯属浪费。
- **为什么 xfail 而不是 skip**：skip 只是不跑；`strict=True` 是「已知缺陷」契约，服务端修好后会 XPASS 变红，提醒你更新用例。
- **为什么固定 SHA**：可复现是自动化的底线；否则上游一次提交就能让你的 CI 无故变红。

## Roadmap

- [ ] 用例矩阵 60+：参数化、边界值、鉴权矩阵、契约校验
- [ ] JSON Schema 响应结构校验
- [ ] 数据工厂（唯一数据）与清理注册表
- [ ] 多环境切换（`--env`）与敏感信息环境变量化
- [ ] Allure 报告 + `pytest-xdist` 并行
- [ ] 缺陷单与用例矩阵文档

## 已知限制

- 部分用例造数后未清理，数据隔离尚未完成
- 断言以状态码与关键字段为主，未做 schema 校验
- 尚未接入 Allure 与并行执行

## 致谢

被测服务 [restful-booker](https://github.com/mwinteringham/restful-booker)（Mark Winteringham）；本仓库仅用于学习与工程实践。