import unittest

from kiwi.agents.protocol.fix.fix_template import FixTemplate


class TestFixTemplate(unittest.TestCase):
    def setUp(self):
        self.tpl = FixTemplate()
        self.yaml_content = """
templates:
  NewOrderSingle:
    header:
      - [35, D]
    body:
      - tag: 11
        name: ClOrdID
        required: true
        value: "{clordid}"
      - tag: 55
        name: Symbol
        value: "{symbol}"
      - tag: 453
        name: NoPartyIDs
        repeating: true
        group:
          - tag: 448
            name: PartyID
            value: "{party_id}"
"""
        self.tpl.load_from_string(self.yaml_content)

    def test_build_fields_with_repeating_group(self):
        values = {
            'clordid': 'C1',
            'symbol': 'AAPL',
            'NoPartyIDs': [
                {'party_id': 'P1'},
                {'party_id': 'P2'},
            ]
        }
        fields = self.tpl.build_fields('NewOrderSingle', values)
        # expected flattened sequence: header 35, body 11,55, group count 453, then two 448 entries
        expected = [(35, 'D'), (11, 'C1'), (55, 'AAPL'), (453, '2'), (448, 'P1'), (448, 'P2')]
        self.assertEqual(fields, expected)

    def test_required_field_missing_raises(self):
        values = {
            'symbol': 'AAPL',
            'NoPartyIDs': []
        }
        with self.assertRaises(ValueError):
            self.tpl.build_fields('NewOrderSingle', values)


if __name__ == '__main__':
    unittest.main()

