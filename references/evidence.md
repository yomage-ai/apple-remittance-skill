# Page and fact acceptance / 页面与事实验收

## Starting from no reference materials / 无旧资料开始

The Agent opens `https://appstoreconnect.apple.com/`, checks login and prepares the actual official page for user login only when necessary. Reference files and advance login are not required. Find the latest paid transaction or match the specified payment date, resolve genuine team/payment ambiguity, then read and capture these pages. Existing samples and bank instructions are optional.

Actual backend login is distinct from screenshot 06: complete necessary user login in the working session first, then use a separate private window only for the empty-password login screenshot. Never sign out of a working session to create that image.

## Seven fresh pages / 七页实时截图

| Filename | Live content that must be readable |
|---|---|
| 01 付款和财务报告.png | Correct report month and selected vendor; paid date/status, transaction ID, total payout and currency, account suffix and all final payout rows. Reconcile final payout-currency amounts, not mixed raw proceeds. |
| 02 商务主体.png | Current legal-entity selector; this user's company names, address, vendor and any legacy entity/status actually present. A second or deprecated entity is not required if the user has none. |
| 03 公司商务总览.png | Current company/vendor, agreements and their dates/status, bank row/currencies/status, tax forms/dates/status and compliance sections actually shown. Capture the complete long page, including lower sections. |
| 04 账户持有人详细信息.png | Bank-holder modal; current beneficiary/type, address lines, city/province/postcode/country and controls. If native input clips the full name, inspect its actual value using supported accessibility/DOM and cross-check company evidence; do not alter field widths. |
| 05 银行账户详细信息.png | Current full revealed account, currency, routing/CNAPS if present, nickname, bank address and associated entities. Expand association read-only as needed; never save bank changes. |
| 06 Apple登录页面.png | Real Apple Developer login in a task-owned private window: correct account entered, Continue clicked, password field visible and empty. No Sign In submission, verification, passkey/password-manager flow, error, loading or overlay. The account-only initial stage fails. |
| 07 App列表.png | Actual authorized account's apps and any current payment warnings. Preserve true warnings. A historical returned-transaction reference is not evidence that the selected current payment was returned. |

The seven categories form this workflow's reference packet, not a universal bank requirement. Missing permissions or page availability cannot be disguised as a successful capture. Explain any discrepancy and keep the packet incomplete until resolved. The user may need additional bank-specific documents outside these nine files.

## Required framing / 截图边界

All seven images include the actual browser address toolbar, exclude the tab strip and contain no cursor or pointer highlight. Before capture, move the pointer onto the selected tab that will be cropped away. Do not paint/inpaint it out. Dismiss password-manager suggestions with Escape and blur the login form by clicking a plain non-link heading before clicking the selected tab; tabbing onto a hyperlink can introduce a status-URL overlay.

Inspect the current native screenshot before measuring the crop. Never reuse fixed crop coordinates after a browser, window or DPI change. Save native bytes using their actual format, then losslessly crop to PNG:

```bash
python scripts/prepare_screenshot.py --raw-window /private/raw.jpg --tabs-bottom MEASURED_Y --output /packet/new.png
```

For long pages, add `--content-top MEASURED_Y --full-page /private/same-page-native.png`. This joins the same live page's genuine toolbar pixels and native full-page body at identical width, without resizing, redrawing or substituting another page's bar. Record both raw hashes and geometry. A DOM-only screenshot omitting the real address bar is insufficient. Use only supported browser/native UI capture APIs, never website scripts, replayed API responses or local HTML to fabricate the page.

## Source decisions / 数据来源

- **Payment date:** the paid transaction date, not report update time or printing date. Report month is independent.
- **Amount/currency:** final payout header and displayed final payout rows. Displayed FX rates may be rounded; do not replace Apple's actual payout by multiplying the displayed rate.
- **Transaction/vendor:** the selected payment's actual vendor and transaction, not a legacy vendor or warning's old transaction. A beneficiary can differ from the legal entity; verify both instead of silently forcing equality.
- **Company/bank:** this user's current company, full holder, address, bank, full account, currency and routing information. Reconcile the report's suffix with full bank details. Retain leading zeros and exact spelling.
- **Apple party:** use the user's current signed agreement/remittance evidence. Do not assume every account is paid by the same Apple entity.
- **Receipt wording:** Apple paid status alone does not prove bank receipt. Only use “received” after explicit user/bank evidence; otherwise describe what the payment report says.
- **Template precedence:** this user's accepted template and their bank's instructions control. The shared anonymous layout is a starting point, not an approved document from their bank. No invented stamps or signatures.

## Capture record / 来源记录

See [data.md](data.md) for the schema. The Agent sets visual booleans only after inspecting actual screenshots and live facts, never as defaults copied from an example. Preserve supplied originals; never change a value or erase a live warning to match them. The automated checker checks declared provenance, hashes and document text, not whether an image's visible content is true.

Apple's current payment-report reference: [View payments and proceeds](https://developer.apple.com/help/app-store-connect/getting-paid/view-payments-and-proceeds/). Recheck current UI rather than relying on this page as evidence of a particular user's payment.
