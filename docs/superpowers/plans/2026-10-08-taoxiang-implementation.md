# 淘项运营工作区 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task after user review. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 交付可同步的运营工作区和可验证的利润、目标单量测算工具。

**Architecture:** Markdown 保存运营说明，CSV 提供空白数据模板。Python 计算模块与命令行分离，使用标准库 unittest 验证，真实私人数据放在忽略目录。

**Tech Stack:** Python 3.11+、Decimal、argparse、unittest、Git。

**Spec:** `docs/superpowers/specs/2026-10-08-taoxiang-design.md`

## Global Constraints

- 第一个经营目标：北京时间 2026 年 11 月 11 日，单日经营净利润超过 2000 元。
- 启动预算为 5000 元以上，具体上限和品类尚未确定，不构造真实经营数据。
- Python 3.11 及以上，无第三方运行依赖；金额使用 Decimal。
- 贡献利润公式及严格超过目标的单量公式使用设计中的定义；费用非负，费率范围 0 到 1。
- 未录入费用不能声明已经扣除；输出标记为预计，案例标记为假设。
- 使用现有云端检出，不创建 Git worktree；不直接访问或覆盖用户的 F 盘。
- 不提交凭据、客户资料、真实订单、私人供应商报价及私人经营账本；不自动发布、采购或投放。
- 安装与启动配置不得改动源代码或锁文件；Windows 指令只声明为提供，未实际执行不声明验证成功。

## Review Focus

- 单量是负数、非整数或非数字：拒绝并给出非零退出码，Task 2 覆盖。
- NaN、Infinity 及异常大的数：拒绝不支持的输入，不打印堆栈，Task 1、2 覆盖。
- 接近分币的贡献利润：目标单量不能使用展示时的舍入值，Task 1 覆盖。
- 成本缺项：所有成本参数必须显式提供，零费用也显式填写，Task 2 覆盖。
- 既有本地文件和同步冲突：克隆说明不覆盖既有目录，忽略私人目录，Task 3 检查。

## Task 1：独立利润计算模块

**Files:** Create `taoxiang/__init__.py`, `taoxiang/profit.py`; Test `tests/test_profit.py`。

**Interfaces:**
- `parse_amount(value: str, name: str) -> Decimal`：有限非负数，最多 12 位整数和 6 位小数；超出范围报 ValueError，避免 Decimal 精度和资源边界。
- `contribution(price: Decimal, purchase: Decimal, packaging: Decimal, shipping: Decimal, fee_rate: Decimal, advertising: Decimal, aftersales: Decimal) -> Decimal`：按设计计算未舍入利润，验证所有参数。
- `daily_profit(unit_profit: Decimal, orders: int, fixed: Decimal) -> Decimal`：利润可为负，单量为非负整数，固定费用非负。
- `required_orders(unit_profit: Decimal, target: Decimal, fixed: Decimal) -> int | None`：非正贡献利润返回 None；其余使用向下取整加一。

- [ ] 写失败测试：售价 100、采购 30、包装 2、运费 5、费率 0.05、推广 8、售后 3 的贡献利润为 47；50 单、固定费用 100 的日利润为 2250。
- [ ] 写边界测试：贡献利润 20/40/80、目标 2000、固定费用 0，目标单量为 101/51/26；固定费用 100、利润 40 时为 53。
- [ ] 写精度测试：贡献利润 40.000001 时目标单量为 50；利润为 0 或负数返回 None；NaN、Infinity、负费用、费率 1.01 和超过输入范围的数报 ValueError。
- [ ] 执行 `python3 -m unittest discover -s tests -p test_profit.py -v`，确认失败来自缺失模块或行为。
- [ ] 实现模块；使用 Decimal，禁止 float 运算；金额展示留给命令行处理。
- [ ] 重跑 Task 1 测试，全部通过后提交计算模块和测试。

## Task 2：可直接运行的命令行工具

**Files:** Create `taoxiang/__main__.py`; Test `tests/test_cli.py`。

**Interfaces:** `main(argv: list[str] | None = None) -> int`；`python -m taoxiang` 使用 Task 1 模块。

- [ ] 写 subprocess 失败测试：完整参数输入得到预计每单贡献利润 47.00、预计日利润 2250.00、严格超过目标至少 45 单（固定费用 100，目标 2000）。
- [ ] 写 subprocess 失败测试：缺少成本参数、无效数字、非整数或负单量、NaN、超大数字退出非零且输出无 traceback；亏损模型正常输出无法通过增加单量达到目标。
- [ ] 执行 `python3 -m unittest discover -s tests -p test_cli.py -v`，确认目标功能尚未实现。
- [ ] 实现必填参数 `--price --purchase --packaging --shipping --fee-rate --advertising --aftersales --fixed --orders`；可选 `--target` 默认 2000。提供中文帮助、两位小数展示、预计标签和未录入费用说明。
- [ ] 重跑完整测试；执行完整 CLI 正常案例与错误案例，检查退出码后提交。

## Task 3：运营资料和跨电脑同步

**Files:** Create `README.md`, `.gitignore`, `operations/store-profile.md`, `operations/roadmap.md`, `templates/selection.csv`, `templates/product.md`, `templates/sku.csv`, `templates/daily-report.csv`, `docs/windows-sync.md`, `docs/data-policy.md`。

**Interfaces:** 模板仅含表头或填写说明，不提供虚构商品；README 使用 Task 2 的实际参数。

- [ ] 店铺档案写入已知预算范围、未选定品类和目标日期；路线图复制设计的五个检查阶段，并提供进度记录位置。
- [ ] 选品 CSV 表头覆盖候选 ID、商品、供应商、采购、运费、售后、竞争观察、来源、日期；SKU 表头覆盖商品 ID、SKU、规格、成本、售价、库存、依据；日报覆盖日期、订单、收入、退款、成本、推广、其他费用、预计或已结算状态。
- [ ] 商品模板包含标题、卖点证据、详情页结构、图片需求、SKU 引用及草稿状态；数据政策要求实际私人资料放入 `private/`，图片原稿不进入公开仓库。
- [ ] `.gitignore` 忽略 `private/`、`.env`、`.env.*`、虚拟环境和 Python 缓存；同步文档区分可公开资料与私人资料。
- [ ] Windows 文档提供 Git 与 Python 前提、仅在 `F:\淘项` 不存在时克隆、目录存在时先检查 `git status` 与 remote、不覆盖文件、正常 `git pull --ff-only`、提交推送和冲突处理流程；提供同一 CLI 命令的 `py -3` 版本。
- [ ] README 说明数据来源、协作职责、运行和测试命令；只读检查 GitHub 仓库可见性，无法确认时说明未确认，并坚持提交内容可公开。
- [ ] 用 csv.reader 核验三个 CSV 的表头、UTF-8、无假数据；用 `git check-ignore` 核验私人文件路径被忽略；运行 README 的 Linux 命令；检查 git diff 后提交。

## Task 4：验证、推送与云配置

**Files:** 不增加应用代码；保存环境配置 `start_skill`，有实际需要才保存 `install_script`。

**Interfaces:** 消费 README 的目录及已验证命令；使用 cloud-environment-onboarding:setup 配置工具。

- [ ] 执行 Python 版本检查、完整 unittest、正常 CLI、非法输入 CLI、严格目标边界；记录实际测试数量和结果，错误命令退出码单独核验。
- [ ] `git diff --check` 与工作区检查；提交并推送到 main，核验远端 SHA 等于本地 HEAD。失败则报告具体原因，不把提交成功当作推送成功。
- [ ] 保存 start_skill：使用现有 `/workspace/taobao_qianniu`，无需 worktree；Python 3.11+、无第三方依赖、测试与假设测算命令；没有常驻服务；私人数据边界。
- [ ] 无安装需求时不保存空 install_script；确认保存结果，不将保存称为发布或新实例验证。
- [ ] 最终交付说明工具功能、测试、GitHub 提交、云配置字段、用户在环境设置中审阅与发布、Windows 目录需用户实际同步，以及尚缺的真实选品和经营数据。

## 自审与执行方式

四个任务覆盖设计的模板、计算、同步、阶段目标和云配置。计算接口共享 Decimal，CLI 只负责解析与展示；没有引入网页服务、店铺接口或无关依赖。

推荐由当前助手在本会话直接执行：代码量小、计算与命令行接口紧密相关，无需并行代理。用户审阅计划并确认执行方式后开始 Task 1。
