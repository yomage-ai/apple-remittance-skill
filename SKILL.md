---
name: artifact-template-apple-remittance-invoice
description: "为组织开发者准备并核对苹果打款银行材料：访问真实后台新截七张图，生成形式发票和情况说明。Prepare an Apple remittance bank packet with seven fresh browser screenshots and two Word documents using the current user's own account and bank details."
---

# 苹果打款完整材料 / Apple Remittance Packet

为用户指定付款日制作七张本次真实网页截图、形式发票和情况说明，共九份。适合中国大陆组织开发者准备对公收款材料；此组合来自实际办理经验，不能当作所有银行的统一要求。营业执照、协议全文、银行专用表等按用户银行的实际要求另备。回复使用用户当前语言。

Deliver seven fresh screenshots and two Word documents for the requested payment. This workflow targets organization developers preparing bank materials in mainland China; it is not a universal Apple/bank checklist or a guarantee of acceptance.

## 执行 / Workflow

1. **定位这笔款和个人档案。** 用户提供付款日或对应目录即可。保留原件，读取[页面与事实验收标准](references/evidence.md)和[数据与模板约定](references/data.md)。Agent 从本次后台与用户材料建立/更新仓库外的私有 `profile.json` 和 `payment.json`，不是要求用户编辑 JSON。默认查找 `${CODEX_HOME:-~/.codex}/apple-remittance/profiles/default/profile.json`；多个主体时按本次主体匹配，不能猜用默认档案。已有私有模板和样式对照继续使用，历史数据必须重新核对。首次无已接受模板时使用内置匿名版式。禁止把示例资料用作真实材料。
2. **每次访问真实网页。** 使用用户授权的已登录浏览器，七页逐一新截。银行弹窗仅查看、展开账号/主体关联或切换步骤，最后取消，不能保存设置。只有必须本人完成的身份验证才交接；Agent 继续其余独立工作。不要退出用户现有登录。详细页面覆盖及数据来源见证据表。
3. **登录页到密码输入阶段即可。** 在任务自建无痕窗口访问 `https://developer.apple.com/account/`，填已核实的开发者账号，点“继续”，等密码框出现。账号已填、密码框可见，密码留空，不点“登录”；不用密码管理器自动填充或提交。不要为了截图发起完整登录、通行密钥或验证码验证。不是仅有账号框的初始页。关闭浮层、加载和报错后才能截；保留原后台会话。
4. **七图统一边界。** 每张保留真实浏览器地址栏，去掉上方标签栏，画面无鼠标/高亮。截图前将鼠标移到将裁掉的标签栏（可点当前已选标签）。按本次实测边界运行 `scripts/prepare_screenshot.py`。长总览页只能用同页、同时段、同宽度的真实地址栏像素和浏览器原生整页截图作纵向拼接。不得绘制网址栏、改数值、重建网页、抹除鼠标或拿旧图代替。未加载完、账号不全、税表被截掉或业务字段不可读都需重截。
5. **提取和核对事实。** 本次已付款报告决定付款日、报表月、金额/币种、交易号和所选供应商；银行/公司资料取本次相应页面。Apple付款状态不等于银行已入账。只有银行通知或用户材料明确证实收到时，才把 `receipt_confirmed` 设为 true；否则情况说明使用“付款报告列示支付”的措辞。前期结转需真实凭据支持。对方 Apple 法律实体取本用户协议/付款凭证，不猜展开简称，不套他人主体。支持 CNY/USD/EUR/HKD/GBP 两位小数；其他币种先适配校验和文档，不能冒称已支持。不要用舍入汇率重算实际付款额。
6. **生成 Word 并看渲染。** Agent 准备 Python 及 Pillow，使用可用 Documents/Word 工具渲染。调用下列脚本，拒绝覆盖现有文件。内置匿名模板或本用户已接受的私有字段模板控制版式。检查两个文档的每个渲染页，尤其公司长名称、日期、金额大写、币种和一页A4。模板占位符原件不用于打印；实际填好的 Word 才进九份目录。中文字体不全时修复本次渲染字体配置，不能靠改原字体掩盖缺字。
7. **九份一起验收。** Agent 记录本次时间、每图实际来源URL、SHA-256、逐图视觉签核及实时核实字段到打印目录外的 `capture-manifest.json`。检查脚本只验证声明、文件和文字，不能证明网页访问或代替读图。七张图及两份 Word 都需人工视觉检查；缺图、错主体/日期/金额/交易、网址栏缺失、有标签/鼠标、登录页密码框缺失或必要身份验证未完时不得报告完整通过。原材料和当前网页有真实差异时说明差异，不修图迎合旧状态。
8. **本地交付与收尾。** 打印目录只放九份。给出位置、核对结论、与参考差异及需用户处理的事；不自动上传、发给银行、提交、盖章或寄出。关闭任务自建页/无痕窗口，保留用户原标签和会话，删除无用临时截图、渲染和依赖。个人档案、模板、截图、凭据与生成材料永远不加入共享仓库。改公开代码前后做隐私扫描，见 `scripts/check_public.py`。

## Agent helpers

Agent 填参数、准备依赖和运行，不让用户手工执行安装、JSON 编辑或转换步骤。

```bash
python scripts/create_invoice.py --profile /private/profile.json --payment /private/payment.json --output /packet/形式发票.docx
python scripts/create_statement.py --profile /private/profile.json --payment /private/payment.json --output /packet/Apple软件分成款情况说明.docx
python scripts/check_packet.py --folder /packet --profile /private/profile.json --payment /private/payment.json --capture-manifest /private/capture-manifest.json
```

Each invocation must visit the actual authorized website and capture all seven categories anew. Every screenshot includes real browser URL chrome, excludes tabs and contains no pointer. The login screenshot requires the entered account and a visible empty password field after Continue, without submitting Sign In. Keep profiles, accepted personal templates, captures and generated materials outside the shared repository. Resolve facts from current evidence, never from bundled examples. Distinguish Apple payment from bank receipt, and a checked packet from bank acceptance. The Agent handles setup, document rendering, verification and cleanup; only genuinely personal login/permissions need handoff.
