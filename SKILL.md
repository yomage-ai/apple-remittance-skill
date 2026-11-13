---
name: artifact-template-apple-remittance-invoice
description: "为组织开发者准备并核对苹果打款银行材料：访问真实后台新截七张图，生成形式发票和情况说明。Prepare an Apple remittance bank packet with seven fresh browser screenshots and two Word documents using the current user's own account and bank details."
---

# 苹果打款完整材料 / Apple Remittance Packet

为用户最近一笔或指定付款日的苹果来款制作七张本次真实网页截图、形式发票和情况说明，共九份。首次使用不要求用户有文件夹、旧材料、模板或已登录的浏览器。适合中国大陆组织开发者准备对公收款材料；此组合来自实际办理经验，不能当作所有银行的统一要求。营业执照、协议全文、银行专用表等按用户银行的实际要求另备。回复使用用户当前语言。

Deliver seven fresh screenshots and two Word documents for the latest or requested payment. No reference folder, old packet, template or advance login is required. This workflow targets organization developers preparing bank materials in mainland China; it is not a universal Apple/bank checklist or a guarantee of acceptance.

## 执行 / Workflow

1. **Agent 主动打开后台并处理登录。** 先检查可用浏览器/电脑操作工具，复用合适的 Apple 后台标签；没有时主动打开 `https://appstoreconnect.apple.com/`。检查实际登录状态，不能要求用户先准备已登录浏览器。未登录时把真实 Apple 页面留给用户，明确提示“请在我打开的 Apple 官方页面完成登录和验证，完成后告诉我”，再核实后台身份并继续；不让用户在聊天里发密码或验证码。已有正常会话直接使用，不要求重复登录。只有实际遇到本人验证/必要权限才交接。若工具缺失，Agent 先检查可用替代能力，再说明具体限制；不能拿用户手工截图代替本流程的七张实时截图。
2. **Agent 确定来款并首次建档。** 读取[页面与事实验收标准](references/evidence.md)和[数据与模板约定](references/data.md)。用户指定付款日时匹配该日已付款交易；未指定时在目标团队中查找最近一笔已付款交易。不要把报表月当付款日。只有团队/主体或目标款项仍不唯一时，才展示已经查到的团队、日期、金额、币种等让用户选；用户已明确时不再重复确认。没有已付款记录、实际为不支持的主体，或缺少必要后台权限时说明真实阻碍，不编造材料。Agent 直接读取付款、商务主体、银行弹窗及已经签署的协议详情，获取公司、完整账号、Apple签约/付款方和费用数据。后台能读到的资料不能交给用户手填；公司、收款账号、金额、付款记录等必要事实确实取不到时，核查后集中补问。银行汇款人及具体Apple法人未知时记录未知，不作为所有用户的默认阻塞项；按下述固定原文模板继续。Agent 自行在仓库外建立私有 `profile.json`、`payment.json` 和按付款日命名的输出目录，不让用户先建文件夹、写JSON或交旧发票。默认查找 `${CODEX_HOME:-~/.codex}/apple-remittance/profiles/default/profile.json`，但必须与本次后台主体匹配；已有资料每次回源核实，不默认套用。无个人模板时直接使用内置匿名模板；旧材料、成功样本、截图和银行特别清单仅为可选参考，用户没有这些也继续执行。用户原有文件保留，不覆盖。七页均在本次真实后台新截；银行弹窗仅查看、展开账号/主体关联或切换步骤，最后取消，不能保存设置。
3. **登录页到密码输入阶段即可。** 在任务自建无痕窗口访问 `https://developer.apple.com/account/`，填已核实的开发者账号，点“继续”，等密码框出现。账号已填、密码框可见，密码留空，不点“登录”；不用密码管理器自动填充或提交。不要为了截图发起完整登录、通行密钥或验证码验证。不是仅有账号框的初始页。关闭浮层、加载和报错后才能截；保留原后台会话。
4. **七图统一边界。** 每张保留真实浏览器地址栏，去掉上方标签栏，画面无鼠标/高亮。截图前将鼠标移到将裁掉的标签栏（可点当前已选标签）。按本次实测边界运行 `scripts/prepare_screenshot.py`。长总览页只能用同页、同时段、同宽度的真实地址栏像素和浏览器原生整页截图作纵向拼接。不得绘制网址栏、改数值、重建网页、抹除鼠标或拿旧图代替。未加载完、账号不全、税表被截掉或业务字段不可读都需重截。
5. **提取和核对事实。** 本次已付款报告决定付款日、报表月、金额/币种、交易号和所选供应商；银行/公司资料取本次相应页面。Apple付款状态不等于银行已入账。只有银行通知或用户明确证实收到时，才把 `receipt_confirmed` 设为 true；未提供入账证据时设为 false，情况说明必须保留已接受原文，不能擅自改成“付款报告列示”等另一种文案。用户给出的已收款原件可作为事实依据；确无收到款依据时先确认这一事实，不生成断言已收到的最终说明。前期结转需真实凭据支持。对方Apple法律实体、实际银行汇款人和合同方分别核实，不能混为一谈。已核实名称照实填写；无法唯一确定时保留为空，发票改标“付款平台：Apple App Store”，情况说明固定为已接受的“本公司{公司}与APPLE公司签订协议，根据每月结算单收取软件分成费。”以及“本公司于{付款日}收到{付款方} 支付的{结算月}的软件分成，{币种名称}{金额}元。”两段，只换字段，不改句式、叙述角度或添加段落。付款方沿用本用户已接受原件的准确写法；首次无原件且不知道具体法人时可用品牌通称“APPLE公司”，不冒称某个已核实法人，也不把不知道具体名称作为普遍门槛。只有本用户的银行明确要求该具体名称时，才提示补核实；若银行明确必填而用户暂不知，保留已完成材料并说明该银行要求未满足；没有这种明确要求时，具体名称未知不单独阻塞；但原文“收到”的事实仍须有依据，不以改写文案绕开。支持 CNY/USD/EUR/HKD/GBP 两位小数；其他币种先适配校验和文档，不能冒称已支持。不要用舍入汇率重算实际付款额。
6. **生成 Word 并看渲染。** Agent 准备 Python 及 Pillow，使用可用 Documents/Word 工具渲染。调用下列脚本，拒绝覆盖现有文件。内置匿名模板或本用户已接受的私有字段模板控制版式。检查两个文档的每个渲染页，尤其公司长名称、日期、金额大写、币种和一页A4。模板占位符原件不用于打印；实际填好的 Word 才进九份目录。中文字体不全时修复本次渲染字体配置，不能靠改原字体掩盖缺字。
7. **九份一起验收。** Agent 记录本次时间、每图实际来源URL、SHA-256、逐图视觉签核及实时核实字段到打印目录外的 `capture-manifest.json`。检查脚本只验证声明、文件和文字，不能证明网页访问或代替读图。保留party_scope中的未知值和付款平台/法律实体区别；九份文件齐备不等于未知汇款方已核实或银行特定要求已满足。七张图及两份 Word 都需人工视觉检查；缺图、错主体/日期/金额/交易、网址栏缺失、有标签/鼠标、登录页密码框缺失或必要身份验证未完时不得报告完整通过。原材料和当前网页有真实差异时说明差异，不修图迎合旧状态。
8. **本地交付与收尾。** 打印目录只放九份。给出位置、核对结论、与参考差异及需用户处理的事；不自动上传、发给银行、提交、盖章或寄出。关闭任务自建页/无痕窗口，保留用户原标签和会话，删除无用临时截图、渲染和依赖。个人档案、模板、截图、凭据与生成材料永远不加入共享仓库。改公开代码前后做隐私扫描，见 `scripts/check_public.py`。

## Agent helpers

Agent 填参数、准备依赖和运行，不让用户手工执行安装、JSON 编辑或转换步骤。

```bash
python scripts/create_invoice.py --profile /private/profile.json --payment /private/payment.json --output /packet/形式发票.docx
python scripts/create_statement.py --profile /private/profile.json --payment /private/payment.json --output /packet/Apple软件分成款情况说明.docx
python scripts/check_packet.py --folder /packet --profile /private/profile.json --payment /private/payment.json --capture-manifest /private/capture-manifest.json
```

The Agent opens App Store Connect, checks the actual session and hands the official login page to the user only when needed. Do not require advance login, a reference folder, an old invoice or a prior profile. Select the latest paid transaction unless a date was specified; ask only when the team or target is ambiguous. Read accessible account/agreement/bank facts, bootstrap private data and an output directory, and use bundled templates on first use. Existing bank packets and special bank instructions are optional. Each invocation must visit the actual authorized website and capture all seven categories anew. Every screenshot includes real browser URL chrome, excludes tabs and contains no pointer. The login screenshot requires the entered account and a visible empty password field after Continue, without submitting Sign In. Keep profiles, accepted personal templates, captures and generated materials outside the shared repository. Resolve facts from current evidence, never from bundled examples. Distinguish Apple payment from bank receipt, and a checked packet from bank acceptance. The Agent handles setup, document rendering, verification and cleanup; only genuinely personal login/permissions need handoff.

Unknown exact entity names stay null; do not invent a legal remitter. The situation statement follows the accepted reference verbatim: retain the two original Chinese sentences about the agreement and receipt of monthly software proceeds. Replace only company, payment date, period, currency/amount and the reference's supported payer spelling. Do not substitute platform-business or payment-report narrative. Where no exact remitter is known, APPLE公司 is a general brand reference, not a verified legal entity. The reference says received, so generation and a complete packet require confirmed receipt; user-provided accepted receipt materials may establish it. Confirm a truly missing receipt fact instead of rewriting the statement.
