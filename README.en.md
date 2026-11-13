Copy this request to Codex to install:

> Install the Apple Remittance Packet skill from https://github.com/yomage-ai/apple-remittance-skill.

[简体中文](README.md)

# Apple Remittance Packet

Prepare bank materials for Apple App revenue. Tell the skill which payment to prepare. It opens the Apple website, guides you through login when needed, reads the account data, captures screenshots, generates a pro forma invoice and a situation statement, and checks the complete packet.

Intended for organization developers preparing company bank-receipt materials in mainland China.

## Get started

After installation, start a new task:

> Use the Apple remittance skill to prepare bank-receipt materials for my most recent Apple payment.

1. The skill opens App Store Connect. If you are not signed in, complete login and verification on the Apple page it opens.
2. The Agent finds the most recent paid transaction or the date you requested. It asks you to choose only when several teams or payments make the target ambiguous.
3. The Agent reads company, agreement, bank and payment data from the website, generates documents using the included templates, creates the output folder and verifies the packet.

Previously accepted samples and bank-specific requirements are optional references. The Agent handles environment checks, dependencies, screenshots and documents, and asks for additional facts only when essential information cannot actually be obtained from the account.

## What you receive

- Seven real screenshots: payment report, business entities, company overview, account holder, bank account, login page and app list.
- One editable Word pro forma invoice and one editable Word situation statement.
- A packet verification result, including anything missing or still needing confirmation.

Every screenshot retains the browser address bar, excludes tabs and contains no mouse pointer. The login page shows the entered account and a visible empty password field. Each payment is checked anew; previous amounts or accounts are not reused as facts.

## License

Free to prepare receipts for yourself or your own company. Resale, paid preparation services and commercial product integration require separate written permission. These distribution restrictions do not apply to the bank materials you generate. [Full license](LICENSE) · [Licensing contact](https://github.com/yomage-ai/apple-remittance-skill/issues)
