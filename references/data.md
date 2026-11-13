# Local data and templates / 私有数据与模板

Agent creates these files outside the shared repository from the current user's live account data; they are internal working files, not user-supplied prerequisites. `examples/*.example.json` are fictitious schema illustrations, never defaults for a real packet. Do not ask users to edit JSON; ask only for genuinely missing business facts or authorization.

## First use without files / 没有资料的首次使用

Open App Store Connect and inspect the current session. If login is needed, keep the official page ready for the user to complete login/verification; do not ask them to sign in beforehand or send credentials in chat. Verify the actual account and company afterward. Find the latest paid transaction unless the user specified a date, and ask only when team/payment selection remains ambiguous.

Read company, full bank-account/holder and payment facts from their live pages; inspect existing signed agreements for the Apple legal party. Create the local profile/payment JSON and dated output folder yourself. A missing local profile is normal on first use. Start from the bundled anonymous templates when no personal template exists. Never demand a previous invoice, screenshots, reference folder or bank checklist as a prerequisite. If an essential fact cannot be read after the relevant source has been inspected, ask only for that missing fact. Without bank-receipt evidence use `receipt_confirmed: false` and payment-report wording. Optional accepted materials may refine the layout later.

## Profile and payment

- Profile: `schema_version: 1`; `company` has `english_name`, `local_name`, `address`; `apple` has `developer_account`, `recipient_name`, `payer_statement_name`, `contract_party`; `bank` has `beneficiary`, `name`, `account`, `currency` and optional `cnaps`. `invoice_prefix` defaults to `INV-APPLE`, an internal reference rather than an Apple invoice number. Verify every party name from actual evidence.
- Optional `templates.invoice` / `templates.statement`: absolute paths or paths relative to the local profile. These must be tokenized versions of that user's accepted Word documents. Optional `visual_baseline` points to the user's private accepted screenshot reference, not a file to upload. Read it for layout and still capture fresh screenshots.
- Payment: `schema_version: 1`, `payment_date: YYYY-MM-DD`, `report_month: YYYY-MM`, `currency`, `amount` as a two-decimal string, `transaction_id`, `vendor_id`, `vendor_name`, `status: paid`, `agreement_verified: true`, `receipt_confirmed` boolean, optional `carried_forward` boolean, and `payout_rows` containing every displayed final payout-currency `amount`/`currency` pair. Raw USD proceeds do not belong in a CNY payout sum.
- Currently supported payout currencies: CNY, USD, EUR, HKD and GBP, with positive totals below 100 million. Payout and this receiving account's currency must agree; an unexplained mismatch blocks generation. This is deliberately narrower than all Apple currencies.
- `receipt_confirmed` is true only with the user's bank notice or explicit existing materials confirming receipt. False uses payment-report wording. `agreement_verified` requires inspecting the agreement state; it is not permission to accept an agreement.
- Do not automatically overwrite a profile when switching legal entities. Match the requested account, company, vendor and currency first. Do not store passwords, cookies or authentication tokens.

## Capture manifest

Root fields: `method: live_browser`, `started_at` (timezone-aware ISO-8601), `verified_facts`, `captures`.

`verified_facts` must exactly match `check_packet.expected_facts(profile, payment)`: payment date/report month/currency/amount/transaction/vendor ID/vendor name; company English/local name/address; bank name/beneficiary/full account/currency (and CNAPS if present); developer account; Apple recipient and payer spelling. Agent must independently verify these from the live pages and authorized user evidence, not manufacture a signoff by copying profile values.

`captures` contains exactly the seven stable filenames. Each has actual `url`, `captured_at`, final `sha256`, and four true visual signoffs: `visual_checked`, `address_bar_visible`, `tab_strip_absent`, `cursor_absent`. Retain raw source hashes/crop boundaries when processing a screenshot.

Login capture additionally requires `login_stage: password_entry`, `account_identifier` equal to the verified account, and `account_entered`, `password_field_visible`, `password_empty`, `login_not_submitted` all true. Never record a password. A populated account field without a visible password field fails.

The manifest and private facts remain outside the nine-file printing folder. Timestamps/hashes and declared signoffs do not prove page truth: Agent must inspect the actual pages and images. Do not label recycled evidence as a fresh run.

## Word token contract

All dynamic text in each template is inside a single Word text node per token, written `{{field_name}}`. `packet_data.REQUIRED` lists the mandatory tokens for each document and `packet_data.fields` computes values. Full dates, company, Apple party, description, total, beneficiary, bank and account are variable. The built-in templates preserve the reference's A4 layout but contain no personal data or cached preview.

When adapting a user's existing Word, map its fields to these tokens in place, including split date/description runs. Preserve non-text XML and other required package parts; retain the source unchanged outside the repository. Unknown/missing/split tokens block generation. Scripts never overwrite existing outputs. Render and inspect every resulting page; fit is not guaranteed for a new long company/address.

For CNY, generate RMB uppercase. For supported foreign currencies, display the currency/code and numeric amount rather than fabricate RMB words. The invoice and statement are for bank explanation of an existing payment, not a request for another payment, an Apple-issued invoice or a tax invoice.

## Publishing

Only code, anonymous tokenized templates, fictitious schema examples, tests and instructions belong in the repository. Real screenshots, previews, old Word ZIP parts, personal paths, profiles and generated packets do not. `.gitignore` is a backstop, not the privacy check.

Before publishing run `python scripts/check_public.py --root .`; for a personal migration additionally pass `--deny-values /private/sensitive-values.json`. This reads every tracked candidate, decompresses Word packages, rejects cached previews/custom metadata/embedded media and reports filenames only. Inspect the final candidate list and diff. Never add a private file temporarily and delete it in a later commit: its history would still disclose it. Tests use synthetic evidence images only and must never be presented as real bank evidence.
