#!/usr/bin/env python3
"""Validate local facts and fill Word text slots without rewriting layout."""
from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape, unescape
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
MONTHS = 'January February March April May June July August September October November December'.split()
CURRENCIES = {'CNY': '人民币', 'USD': '美元', 'EUR': '欧元', 'HKD': '港币', 'GBP': '英镑'}
TOKEN = re.compile(r'\{\{([a-z_]+)\}\}')
TEXT = re.compile(r'(<w:t\b[^>]*>)(.*?)(</w:t>)', re.S)
IMAGES = ['01 付款和财务报告.png', '02 商务主体.png', '03 公司商务总览.png', '04 账户持有人详细信息.png', '05 银行账户详细信息.png', '06 Apple登录页面.png', '07 App列表.png']
DOCS = {'invoice': '形式发票.docx', 'statement': 'Apple软件分成款情况说明.docx'}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def text(value, label):
    if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 for c in value):
        raise ValueError('Missing or invalid text field: ' + label)
    if '{{' in value or '}}' in value:
        raise ValueError('Unfilled field: ' + label)
    return value


def money(value, allow_negative=False):
    if not isinstance(value, str) or not re.fullmatch(r'-?\d+\.\d{2}' if allow_negative else r'\d+\.\d{2}', value):
        raise ValueError('Amounts must be strings with exactly two decimal places')
    result = Decimal(value)
    if not (Decimal('-100000000') < result < 100000000 and (allow_negative or result >= 0)):
        raise ValueError('Amount outside supported range')
    return result


def party_facts(profile):
    """An unknown legal party stays unknown; a platform label is not a remitter."""
    apple = profile['apple']
    result = {}
    for key in ['recipient_name', 'payer_statement_name', 'contract_party']:
        value = apple.get(key)
        result[key] = None if value is None or value == '' else text(value, 'apple.' + key)
    result['invoice_party_kind'] = 'legal_entity' if result['recipient_name'] else 'platform'
    return result


def rmb_upper(amount):
    digits = '零壹贰叁肆伍陆柒捌玖'
    def group(n):
        out, zero = '', False
        for power, unit in [(1000, '仟'), (100, '佰'), (10, '拾'), (1, '')]:
            digit, n = divmod(n, power)
            if digit:
                out += ('零' if zero and out else '') + digits[digit] + unit
                zero = False
            elif out:
                zero = True
        return out
    whole, fraction = divmod(int(amount * 100), 100)
    high, low = divmod(whole, 10000)
    result = group(high) + '万' if high else ''
    if high and 0 < low < 1000:
        result += '零'
    result += group(low) if low else ('' if high else '零')
    result += '元'
    jiao, fen = divmod(fraction, 10)
    if not fraction:
        return result + '整'
    if jiao:
        result += digits[jiao] + '角'
    elif whole:
        result += '零'
    return result + (digits[fen] + '分' if fen else '')


def load_facts(profile_path, payment_path):
    profile, payment = read_json(profile_path), read_json(payment_path)
    if profile.get('schema_version') != 1 or payment.get('schema_version') != 1:
        raise ValueError('Unsupported profile/payment schema; originals are not modified')
    for section, keys in {'company': ['english_name', 'local_name', 'address'], 'apple': ['developer_account'], 'bank': ['beneficiary', 'name', 'account', 'currency']}.items():
        for key in keys:
            text(profile[section][key], section + '.' + key)
    parties = party_facts(profile)
    requirements = profile.get('bank_requirements', {})
    if not isinstance(requirements, dict):
        raise ValueError('bank_requirements must be an object')
    for requirement, key in [('remitter_name', 'payer_statement_name'), ('legal_recipient_name', 'recipient_name')]:
        required = requirements.get(requirement, False)
        if not isinstance(required, bool):
            raise ValueError('Bank requirement must be boolean: ' + requirement)
        if required and not parties[key]:
            raise ValueError('Bank explicitly requires a verified ' + requirement)
    for key in ['transaction_id', 'vendor_id', 'vendor_name', 'currency', 'payment_date', 'report_month']:
        text(payment[key], key)
    paid = date.fromisoformat(payment['payment_date'])
    if not re.fullmatch(r'\d{4}-\d{2}', payment['report_month']):
        raise ValueError('Report month must be YYYY-MM')
    year, month = map(int, payment['report_month'].split('-'))
    if date(year, month, 1) > paid:
        raise ValueError('Report month cannot follow payment date')
    if payment.get('status') != 'paid' or payment.get('agreement_verified') is not True:
        raise ValueError('A paid transaction and verified agreement are required')
    if not isinstance(payment.get('receipt_confirmed'), bool):
        raise ValueError('Specify whether receipt was confirmed by the bank/user')
    if 'carried_forward' in payment and not isinstance(payment['carried_forward'], bool):
        raise ValueError('carried_forward must be boolean')
    currency = payment['currency']
    if currency not in CURRENCIES or profile['bank']['currency'] != currency:
        raise ValueError('Unsupported currency or payout/bank currency mismatch')
    amount = money(payment['amount'])
    if not amount:
        raise ValueError('Payout must be positive')
    rows = payment.get('payout_rows')
    if not isinstance(rows, list) or not rows:
        raise ValueError('Record every displayed final payout-currency row')
    if any(row['currency'] != currency for row in rows):
        raise ValueError('Do not mix raw proceeds currencies with final payout rows')
    if sum((money(row['amount'], allow_negative=True) for row in rows), Decimal('0')) != amount:
        raise ValueError('Displayed payout rows do not reconcile to final payout')
    return profile, payment


def template_path(profile, kind, profile_path):
    bundled = ROOT / 'assets' / ('reference.docx' if kind == 'invoice' else 'statement-reference.docx')
    custom = profile.get('templates', {}).get(kind)
    if custom:
        path = Path(custom).expanduser()
        path = path if path.is_absolute() else Path(profile_path).resolve().parent / path
        parties = party_facts(profile)
        needed = 'recipient_heading'
        unknown = kind == 'invoice' and not parties['recipient_name']
        if unknown:
            with ZipFile(path) as archive:
                tokens = set(TOKEN.findall(archive.read('word/document.xml').decode('utf-8')))
            if needed not in tokens:
                return bundled  # Legacy custom template must not mislabel a platform as a legal entity.
        return path
    return bundled


def fields(profile, payment):
    day = date.fromisoformat(payment['payment_date'])
    year, month = map(int, payment['report_month'].split('-'))
    company, apple, bank = (profile[key] for key in ['company', 'apple', 'bank'])
    parties = party_facts(profile)
    currency, amount = payment['currency'], payment['amount']
    full_date = f'{day.day} {MONTHS[day.month-1]} {day.year}'
    carried = payment.get('carried_forward', False)
    english = f'App Store software revenue share - {"carried-forward " if carried else ""}proceeds shown in the {MONTHS[month-1]} {year} payment report.'
    local = f'软件分成费：{year}年{month}月付款报表列示的{"前期结转" if carried else "软件分成"}收入。'
    prefix = text(profile.get('invoice_prefix', 'INV-APPLE'), 'invoice_prefix')
    invoice_id = f'{prefix}-{day:%Y%m%d}-{payment["transaction_id"]}'
    date_local = f'{day.year}年{day.month}月{day.day}日'
    # Keep the accepted statement verbatim apart from its factual slots.
    # APPLE公司 is a general brand reference, not an invented legal remitter name.
    receipt_start = f'本公司于{date_local}收到{parties["payer_statement_name"] or "APPLE公司"}'
    receipt_end = f'支付的{year}年{month}月的软件分成，{CURRENCIES[currency]}{amount}元。'
    return {
        'invoice_id': invoice_id, 'issue_day': str(day.day), 'issue_month_year': f' {MONTHS[day.month-1]} {day.year}',
        'company_english_name': company['english_name'], 'company_local_name': company['local_name'], 'company_address': company['address'],
        'recipient_heading': 'To / 对方主体' if parties['recipient_name'] else 'Payment platform / 付款平台',
        'recipient_name': parties['recipient_name'] or 'Apple App Store',
        'description_english': english, 'description_local': local, 'amount_line': currency + ' ' + amount,
        'amount_words_line': ('人民币大写：' + rmb_upper(Decimal(amount))) if currency == 'CNY' else f'付款币种及金额：{currency} {amount}',
        'payment_date_line': 'Apple payment date: ' + full_date, 'transaction_line': 'Transaction ID: ' + payment['transaction_id'],
        'vendor_line': f'Payment vendor: {payment["vendor_id"]} ({payment["vendor_name"]})',
        'beneficiary_line': 'Beneficiary: ' + bank['beneficiary'], 'bank_line': 'Bank: ' + bank['name'], 'account_line': f'Account: {bank["account"]} | Currency: {bank["currency"]}',
        'statement_company_start': '本公司' + company['local_name'],
        'statement_relation': '与',
        'statement_contract_tail': 'APPLE公司签订协议，根据每月结算单收取软件分成费。',
        'statement_receipt_start': receipt_start, 'statement_receipt_end': receipt_end,
    }


REQUIRED = {
    'invoice': {'invoice_id', 'issue_day', 'issue_month_year', 'company_english_name', 'company_local_name', 'company_address', 'recipient_name', 'description_english', 'description_local', 'amount_line', 'amount_words_line', 'payment_date_line', 'transaction_line', 'vendor_line', 'beneficiary_line', 'bank_line', 'account_line'},
    'statement': {'statement_company_start', 'statement_contract_tail', 'statement_receipt_start', 'statement_receipt_end'},
}


def filled_xml(source, values, kind):
    with ZipFile(source) as archive:
        xml = archive.read('word/document.xml').decode('utf-8')
    tokens = set(TOKEN.findall(xml))
    if not REQUIRED[kind] <= tokens or tokens - values.keys():
        raise ValueError('Template has missing/unknown fields; Agent must map and verify it first')
    def replace(match):
        result = TOKEN.sub(lambda token: values[token[1]], unescape(match[2]))
        return match[1] + escape(result) + match[3]
    result = TEXT.sub(replace, xml)
    if '{{' in result or '}}' in result:
        raise ValueError('Unresolved template token')
    ET.fromstring(result)
    mask = lambda content: TEXT.sub(lambda m: m[1] + m[3], content)
    if mask(result) != mask(xml):
        raise ValueError('Unexpected non-text XML change')
    return result.encode('utf-8')


def create_document(kind, profile_path, payment_path, output):
    profile, payment = load_facts(profile_path, payment_path)
    if kind == 'statement' and not payment['receipt_confirmed']:
        raise ValueError('The accepted statement says received; confirm receipt before generating it. Do not rewrite the reference wording.')
    source = template_path(profile, kind, profile_path)
    output = Path(output).resolve()
    if output.exists() or output.suffix.lower() != '.docx' or output == source.resolve():
        raise ValueError('Output must be a new .docx path; existing files are never overwritten')
    xml = filled_xml(source, fields(profile, payment), kind)
    with ZipFile(source) as original, output.open('xb') as handle, ZipFile(handle, 'w') as final:
        for item in original.infolist():
            final.writestr(item, xml if item.filename == 'word/document.xml' else original.read(item.filename))
    return output


def paragraphs_xml(xml):
    root = ET.fromstring(xml)
    return [''.join(t.text or '' for t in p.findall('.//{*}t')) for p in root.findall('.//{*}p')]


def document_main(kind):
    import argparse
    parser = argparse.ArgumentParser(description='Generate from verified local profile and payment JSON')
    for name in ['profile', 'payment', 'output']:
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    try:
        print(create_document(kind, args.profile, args.payment, args.output))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, str(error) + '\n')
