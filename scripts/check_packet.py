#!/usr/bin/env python3
"""Check nine deliverables against local facts and the Agent's capture signoffs."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
from zipfile import ZipFile
from PIL import Image
from packet_data import IMAGES, DOCS, load_facts, fields, filled_xml, template_path, paragraphs_xml, read_json, sha256


def expected_facts(profile, payment):
    facts = {key: payment[key] for key in ['payment_date', 'report_month', 'currency', 'amount', 'transaction_id', 'vendor_id', 'vendor_name']}
    facts.update(company_english_name=profile['company']['english_name'], company_local_name=profile['company']['local_name'],
                 company_address=profile['company']['address'], bank_name=profile['bank']['name'], bank_beneficiary=profile['bank']['beneficiary'],
                 bank_account=profile['bank']['account'], bank_currency=profile['bank']['currency'], developer_account=profile['apple']['developer_account'],
                 recipient_name=profile['apple']['recipient_name'], payer_statement_name=profile['apple']['payer_statement_name'])
    if profile['bank'].get('cnaps'):
        facts['bank_cnaps'] = profile['bank']['cnaps']
    return facts


def check(args):
    profile, payment = load_facts(args.profile, args.payment)
    folder = Path(args.folder).resolve()
    expected = set(IMAGES + list(DOCS.values()))
    actual = {p.name for p in folder.iterdir() if not p.name.startswith('.')}
    if actual != expected:
        raise ValueError(f'Missing: {sorted(expected-actual)}; unexpected: {sorted(actual-expected)}')
    manifest = read_json(args.capture_manifest)
    started = datetime.fromisoformat(manifest['started_at'])
    if started.tzinfo is None or manifest.get('method') != 'live_browser':
        raise ValueError('A timestamped live-browser capture record is required')
    if manifest.get('verified_facts') != expected_facts(profile, payment):
        raise ValueError('Live-reviewed facts do not match profile/payment; resolve the discrepancy')
    captures = manifest['captures']
    if set(captures) != set(IMAGES):
        raise ValueError('Capture record must cover all seven named screenshots')
    checks = []
    for name in IMAGES:
        path = folder / name
        item = captures[name]
        captured = datetime.fromisoformat(item['captured_at'])
        if captured.tzinfo is None or not started <= captured <= datetime.now(timezone.utc):
            raise ValueError('Invalid capture timestamp: ' + name)
        url = urlparse(item['url'])
        if url.scheme != 'https' or url.hostname not in ['appstoreconnect.apple.com', 'idmsa.apple.com', 'account.apple.com', 'developer.apple.com']:
            raise ValueError('Not a verified Apple page: ' + name)
        for flag in ['visual_checked', 'address_bar_visible', 'tab_strip_absent', 'cursor_absent']:
            if item.get(flag) is not True:
                raise ValueError('Missing screenshot visual signoff ' + flag + ': ' + name)
        if name == '06 Apple登录页面.png':
            if item.get('login_stage') != 'password_entry' or item.get('account_identifier') != profile['apple']['developer_account']:
                raise ValueError('Login screenshot must show the verified account at the password-entry stage')
            for flag in ['account_entered', 'password_field_visible', 'password_empty', 'login_not_submitted']:
                if item.get(flag) is not True:
                    raise ValueError('Missing login-stage visual signoff ' + flag)
        if sha256(path) != item['sha256']:
            raise ValueError('Screenshot changed since source review: ' + name)
        with Image.open(path) as im:
            if im.format != 'PNG' or im.width < 600 or im.height < 400:
                raise ValueError('Invalid, mislabeled or undersized screenshot: ' + name)
            dimensions = im.size
            im.verify()
        checks.append({'file': name, 'dimensions': dimensions, 'sha256': item['sha256']})
    for kind, name in DOCS.items():
        with ZipFile(folder / name) as archive:
            actual_text = paragraphs_xml(archive.read('word/document.xml'))
        expected_text = paragraphs_xml(filled_xml(template_path(profile, kind, args.profile), fields(profile, payment), kind))
        if actual_text != expected_text:
            raise ValueError('Document does not agree with verified facts/template: ' + name)
    return {'structural_check': 'passed', 'files': 9, 'screenshots': checks, 'word_facts': 'matched',
            'visual_review': 'Agent must inspect all seven live pages/screenshots and both rendered Word documents. This checks declared evidence and values, not image semantics or actual browser access.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['folder', 'capture-manifest', 'profile', 'payment']:
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(check(args), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError, ET.ParseError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
