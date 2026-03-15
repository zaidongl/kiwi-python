import unittest

from kiwi.agents.protocol.fix.fix_agent import FixAgent


class TestFixAgent(unittest.TestCase):
    def setUp(self):
        self.agent = FixAgent(sender='S', target='T', version='FIX.4.4')

    def test_build_and_validate_simple_message(self):
        body = [(55, 'AAPL'), (44, '100')]
        msg = self.agent.build_message('D', body_fields=body, seq_num=7, sending_time='20260314-12:00:00')
        # Should validate
        valid, err = self.agent.validate_message(msg)
        self.assertTrue(valid, msg=f"Expected valid message, got error: {err}")

    def test_checksum_and_body_length_values(self):
        body = [(11, '12345')]
        msg = self.agent.build_message('F', body_fields=body, seq_num=2)
        # Extract BodyLength
        nine_idx = msg.find('9=')
        nine_end = msg.find('\x01', nine_idx)
        supplied_len = int(msg[nine_idx+2:nine_end])
        # compute actual length per spec
        pos_after_9 = nine_end + 1
        ten_idx = msg.rfind('10=')
        actual_len = len(msg[pos_after_9:ten_idx].encode('utf-8'))
        self.assertEqual(supplied_len, actual_len)
        # Checksum
        ten_idx = msg.rfind('10=')
        supplied_sum = msg[ten_idx+3: msg.find('\x01', ten_idx)]
        calc = sum(msg[:ten_idx].encode('utf-8')) % 256
        self.assertEqual(supplied_sum, f"{calc:03d}")


if __name__ == '__main__':
    unittest.main()

