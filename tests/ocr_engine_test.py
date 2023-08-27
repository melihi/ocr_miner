import unittest
import asyncio
from ocr_miner.ocr_engine.ocr_engine import (
    clear_data,
    verify_identity,
    verify_credit_card,
    verify_hash,
    verify_domain,
    find_regex,
)


class Testing(unittest.TestCase):
    def test_clear_data(self):
        data = " .-http: //-https: //- .- . "
        clean = clear_data(data)

        self.assertEqual(clean, ".-http://-https://-.-.")

    def test_verify_identity(self):
        tc = verify_identity("79290240496")  # valid
        fake_tc = verify_identity("79290240495")  # not valid
        ssn = verify_identity("213-11-1234")  # valid
        fake_ssn = verify_identity("220213-11-1234")  # not valid
        vat = verify_identity("ATU12143178")  # valid
        fake_vat = verify_identity("XTU12143178")  # not valid

        self.assertEqual(tc, "TURKISH_CITIZEN_NUMBER")
        self.assertEqual(fake_tc, None)
        self.assertEqual(ssn, "USA_SOCIAL_SECURITY_NUMBER")
        self.assertEqual(fake_ssn, None)
        self.assertEqual(vat, "VAT_NUMBER")
        self.assertEqual(fake_vat, None)

    def test_verify_credit_card(self):
        cc = verify_credit_card("378282246310005")  # American Express
        cc2 = verify_credit_card("6011000990139424")  # Discover
        cc3 = verify_credit_card("4012888888881881")  # Visa
        cc4 = verify_credit_card("4222222222222")  # Visa
        cc5 = verify_credit_card("6331101999990016")  # Switch/Solo(Paymentech)
        fake_cc = verify_credit_card("6331101919990015")
        self.assertEqual(cc, True)
        self.assertEqual(cc2, True)
        self.assertEqual(cc3, True)
        self.assertEqual(cc4, True)
        self.assertEqual(cc5, True)
        self.assertEqual(fake_cc, False)

    def test_verify_hash(self):
        hash_md5 = verify_hash("5f4dcc3b5aa765d61d8327deb882cf99")
        hash_sha1 = verify_hash("5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8")
        hash_sha256 = verify_hash(
            "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
        )
        hash_ntlm = verify_hash("8846F7EAEE8FB117AD06BDD830B7586C")
        fake_hash = verify_hash("aaeaeaeaeaeaeaeaeaeaeaaaaaa23333")
        self.assertEqual(hash_md5, True)
        self.assertEqual(hash_sha1, True)
        self.assertEqual(hash_sha256, True)
        self.assertEqual(hash_ntlm, True)
        self.assertEqual(fake_hash, False)

    def test_verify_domain(self):
        domain = verify_domain("google.com")
        domain2 = verify_domain("notdomain.notdo")
        domain3 = verify_domain("x.co.uk")
        self.assertEqual(domain, True)
        self.assertEqual(domain2, False)
        self.assertEqual(domain3, True)

    def test_find_regex(self):
        ocr_text = "deneme.com https://denedik.com  8846F7EAEE8FB117AD06BDD830B7586C 6331101999990016 79290240496 ATU12143178"

        data = asyncio.run(find_regex(ocr_text))
        print(data)
        self.assertEqual(
            str(data["DOMAINS"][0]), "{'value': 'deneme.com', 'type': 'DOMAIN'}"
        )
        self.assertEqual(
            str(data["URLS"][0]), "{'value': 'https://denedik.com', 'type': 'URL'}"
        )

        self.assertEqual(
            str(data["CREDIT_CARD_NUMBERS"][0]),
            "{'value': '6331101999990016', 'TYPE': 'CREDIT_CARD'}",
        )
        self.assertEqual(
            str(data["ID_NUMBER"][1]),
            "{'value': '79290240496', 'TYPE': 'TURKISH_CITIZEN_NUMBER'}",
        )


if __name__ == "__main__":
    unittest.main()
