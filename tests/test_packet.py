"""Synthetic fixtures only: these images are never bank evidence."""
import copy
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from zipfile import ZipFile
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from packet_data import ROOT, IMAGES, DOCS, read_json, load_facts, create_document, paragraphs_xml, sha256, rmb_upper
from check_packet import check, expected_facts
from check_public import check as check_public


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.profile = read_json(ROOT / 'examples/profile.example.json')
        self.payment = read_json(ROOT / 'examples/payment.example.json')
        self.profile['company']['english_name'] = 'Second Example & Partners Co., Ltd.'
        self.profile['company']['local_name'] = '另一家示例企业有限公司'
        self.profile['bank']['account'] = 'SECOND-DEMO-ACCOUNT'
        self.profile['bank']['beneficiary'] = self.profile['company']['english_name']
        self.profile['bank']['name'] = 'Second Example Bank'
        self.payment['vendor_name'] = self.profile['company']['english_name']
        self.profile_path, self.payment_path = self.base / 'profile.json', self.base / 'payment.json'
        self.save()

    def save(self):
        self.profile_path.write_text(json.dumps(self.profile, ensure_ascii=False))
        self.payment_path.write_text(json.dumps(self.payment, ensure_ascii=False))

    def generate(self, kind):
        return create_document(kind, self.profile_path, self.payment_path, self.base / DOCS[kind])

    def doc_text(self, path):
        with ZipFile(path) as z:
            return '\n'.join(paragraphs_xml(z.read('word/document.xml')))

    def packet(self):
        folder = self.base / 'packet'
        folder.mkdir()
        for kind, name in DOCS.items():
            create_document(kind, self.profile_path, self.payment_path, folder / name)
        now = datetime.now(timezone.utc).isoformat()
        manifest = {'method': 'live_browser', 'started_at': now, 'verified_facts': expected_facts(self.profile, self.payment), 'captures': {}}
        for name in IMAGES:
            image = Image.new('RGB', (800, 500), 'white')
            ImageDraw.Draw(image).text((30, 30), 'SYNTHETIC TEST FIXTURE - NOT BANK EVIDENCE', fill='black')
            image.save(folder / name)
            item = {'url': 'https://developer.apple.com/account/', 'captured_at': now, 'sha256': sha256(folder / name), 'visual_checked': True, 'address_bar_visible': True, 'tab_strip_absent': True, 'cursor_absent': True}
            if name.startswith('06'):
                item.update(login_stage='password_entry', account_identifier=self.profile['apple']['developer_account'], account_entered=True, password_field_visible=True, password_empty=True, login_not_submitted=True)
            manifest['captures'][name] = item
        path = self.base / 'manifest.json'
        path.write_text(json.dumps(manifest))
        args = SimpleNamespace(folder=folder, profile=self.profile_path, payment=self.payment_path, capture_manifest=path)
        return args, manifest

    def test_second_company_and_bank_replace_examples(self):
        content = self.doc_text(self.generate('invoice'))
        self.assertIn(self.profile['company']['english_name'], content)
        self.assertIn(self.profile['bank']['account'], content)
        self.assertNotIn('Example Technology Co., Ltd.', content)
        self.assertNotIn('{{', content)

    def test_unconfirmed_receipt_does_not_claim_received(self):
        content = self.doc_text(self.generate('statement'))
        self.assertIn('付款报告列示', content)
        self.assertNotIn('收到', content)

    def test_confirmed_receipt(self):
        self.payment['receipt_confirmed'] = True
        self.save()
        self.assertIn('收到', self.doc_text(self.generate('statement')))

    def test_foreign_currency_does_not_use_rmb_words(self):
        self.profile['bank']['currency'] = self.payment['currency'] = 'USD'
        for row in self.payment['payout_rows']:
            row['currency'] = 'USD'
        self.save()
        content = self.doc_text(self.generate('invoice'))
        self.assertIn('USD 123.45', content)
        self.assertNotIn('人民币大写', content)
        self.assertIn('美元123.45元', self.doc_text(self.generate('statement')))

    def test_invalid_payment_facts_rejected(self):
        for key, value in [('amount', '999.99'), ('amount', 'NaN'), ('status', 'pending'), ('agreement_verified', False), ('receipt_confirmed', 'yes'), ('report_month', '2027-01'), ('currency', 'JPY')]:
            with self.subTest(key=key, value=value):
                old = copy.deepcopy(self.payment)
                self.payment[key] = value
                self.save()
                with self.assertRaises(ValueError):
                    load_facts(self.profile_path, self.payment_path)
                self.payment = old

    def test_negative_final_payout_row_reconciles(self):
        self.payment['payout_rows'] = [{'currency': 'CNY', 'amount': '-1.00'}, {'currency': 'CNY', 'amount': '124.45'}]
        self.save()
        self.assertIn('CNY 123.45', self.doc_text(self.generate('invoice')))

    def test_mixed_raw_currencies_and_wrong_bank_rejected(self):
        self.payment['payout_rows'][0]['currency'] = 'USD'
        self.save()
        with self.assertRaises(ValueError):
            load_facts(self.profile_path, self.payment_path)
        self.payment['payout_rows'][0]['currency'] = 'CNY'
        self.profile['bank']['currency'] = 'USD'
        self.save()
        with self.assertRaises(ValueError):
            load_facts(self.profile_path, self.payment_path)

    def test_sources_and_existing_outputs_preserved(self):
        source = ROOT / 'assets/reference.docx'
        before = sha256(source)
        output = self.generate('invoice')
        digest = sha256(output)
        with self.assertRaises(ValueError):
            self.generate('invoice')
        self.assertEqual(sha256(output), digest)
        self.assertEqual(sha256(source), before)
        with ZipFile(source) as a, ZipFile(output) as b:
            self.assertEqual(a.namelist(), b.namelist())
            for name in a.namelist():
                if name != 'word/document.xml':
                    self.assertEqual(a.read(name), b.read(name))

    def test_rmb_boundaries(self):
        for amount, expected in [('0.01', '零元壹分'), ('10.00', '壹拾元整'), ('10001.01', '壹万零壹元零壹分')]:
            self.assertEqual(rmb_upper(Decimal(amount)), expected)

    def test_complete_synthetic_packet_checks_structure_only(self):
        args, _ = self.packet()
        self.assertEqual(check(args)['files'], 9)
        self.assertIn('not image semantics', check(args)['visual_review'])

    def test_missing_file_rejected(self):
        args, _ = self.packet()
        (args.folder / IMAGES[0]).unlink()
        with self.assertRaises(ValueError):
            check(args)

    def test_live_fact_conflict_rejected(self):
        args, manifest = self.packet()
        manifest['verified_facts']['bank_account'] = 'WRONG-DEMO-ACCOUNT'
        args.capture_manifest.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            check(args)

    def test_visual_and_login_signoffs_required(self):
        args, manifest = self.packet()
        for name, flag, value in [(IMAGES[0], flag, False) for flag in ['visual_checked', 'address_bar_visible', 'tab_strip_absent', 'cursor_absent']] + [(IMAGES[5], flag, False) for flag in ['account_entered', 'password_field_visible', 'password_empty', 'login_not_submitted']] + [(IMAGES[5], 'login_stage', 'account_entry'), (IMAGES[5], 'account_identifier', 'wrong@example.invalid')]:
            with self.subTest(flag=flag):
                bad = copy.deepcopy(manifest)
                bad['captures'][name][flag] = value
                args.capture_manifest.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    check(args)

    def test_changed_screenshot_rejected(self):
        args, _ = self.packet()
        with (args.folder / IMAGES[0]).open('ab') as handle:
            handle.write(b'changed')
        with self.assertRaises(ValueError):
            check(args)

    def test_changed_word_fact_rejected(self):
        args, _ = self.packet()
        path = args.folder / DOCS['invoice']
        with ZipFile(path) as z:
            parts = {i.filename: z.read(i.filename) for i in z.infolist()}
        parts['word/document.xml'] = parts['word/document.xml'].replace(b'123.45', b'999.99')
        with ZipFile(path, 'w') as z:
            for name, content in parts.items():
                z.writestr(name, content)
        with self.assertRaises(ValueError):
            check(args)

    def test_public_candidates_are_anonymous(self):
        self.assertEqual(check_public(ROOT)['privacy_check'], 'passed')

    def test_hidden_word_metadata_is_rejected(self):
        # Isolated publication fixture, never a second development checkout.
        root = self.base / 'publication-fixture'
        from check_public import FIXED
        for name in FIXED:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        with ZipFile(root / 'assets/reference.docx', 'a') as z:
            z.writestr('docProps/thumbnail.emf', b'FAKE PRIVATE PREVIEW')
        with self.assertRaisesRegex(ValueError, 'Private/opaque'):
            check_public(root)

    def test_known_private_value_is_rejected_without_printing_it(self):
        with self.assertRaises(ValueError) as result:
            check_public(ROOT, ['Second Example Bank'])
        self.assertNotIn('Second Example Bank', str(result.exception))


if __name__ == '__main__':
    unittest.main()
