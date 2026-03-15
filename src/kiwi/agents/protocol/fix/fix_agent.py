from typing import Dict, List, Tuple, Optional

from kiwi.agents.agent import Agent


class FixAgent(Agent):
	"""Simple FIX message builder and validator.

	This class can construct a FIX message given message fields and compute the
	BodyLength(9) and CheckSum(10) fields. It also validates an existing FIX
	message by recomputing these values.
	"""

	SOH = '\x01'

	def __init__(self, name: str = 'FixAgent', sender: str = 'SENDER', target: str = 'TARGET', version: str = 'FIX.4.4'):
		super().__init__(name)
		self.sender = sender
		self.target = target
		self.version = version

	def _encode_field(self, tag: int, value: str) -> str:
		return f"{tag}={value}{self.SOH}"

	def build_message(self, msg_type: str, body_fields: Optional[List[Tuple[int, str]]] = None, seq_num: Optional[int] = None, sending_time: Optional[str] = None) -> str:
		"""
		Build a FIX message string including standard header and trailer.

		Args:
			msg_type: value for tag 35 (MsgType)
			body_fields: list of (tag, value) tuples to include in the message body (order preserved)
			seq_num: optional MsgSeqNum (tag 34); if omitted, 1 is used
			sending_time: optional SendingTime (tag 52), if omitted the caller can set it externally

		Returns:
			The raw FIX message string with SOH separators.
		"""
		if body_fields is None:
			body_fields = []
		if seq_num is None:
			seq_num = 1

		# Start with BeginString and placeholder for BodyLength
		header = []
		header.append(self._encode_field(8, self.version))
		# BodyLength(9) placeholder; will be replaced later
		header.append('9=000' + self.SOH)

		# Standard header fields
		header.append(self._encode_field(35, msg_type))
		header.append(self._encode_field(49, self.sender))
		header.append(self._encode_field(56, self.target))
		header.append(self._encode_field(34, str(seq_num)))
		if sending_time is not None:
			header.append(self._encode_field(52, sending_time))

		# Body fields
		body = []
		for tag, val in body_fields:
			# prevent duplicate header/trailer tags
			if tag in (8, 9, 10):
				continue
			body.append(self._encode_field(tag, str(val)))

		# Compose message without checksum
		msg_without_checksum = ''.join(header) + ''.join(body)

		# Compute BodyLength: number of bytes after "9=...SOH" up to before checksum
		# Per FIX spec BodyLength is the length in bytes of the message following tag 9 up to and including the delimiter before tag 10
		# So we compute the byte length of everything after the first occurrence of '9=...\x01'
		try:
			# find the position after the BodyLength placeholder
			idx = msg_without_checksum.index(self.SOH) + 1  # after first SOH (end of BeginString)
			# but we need to locate the SOH after the 9= tag; locate '9=' occurrence
			nine_pos = msg_without_checksum.find('9=')
			if nine_pos == -1:
				raise ValueError('BodyLength tag not present')
			# position right after the SOH following the 9 tag value
			pos_after_9 = msg_without_checksum.find(self.SOH, nine_pos) + 1
			body_bytes = msg_without_checksum[pos_after_9:].encode('utf-8')
			body_length = len(body_bytes)
		except Exception:
			# fallback: compute length of body+header without BeginString and placeholder
			body_length = len((''.join(header[2:]) + ''.join(body)).encode('utf-8'))

		# replace BodyLength placeholder with actual value
		body_length_tag = self._encode_field(9, str(body_length))

		# rebuild full msg: BeginString + BodyLength + rest
		full_msg_no_checksum = header[0] + body_length_tag + ''.join(header[2:]) + ''.join(body)

		# Compute checksum: sum of all bytes modulo 256, formatted as 3-digit padded with zeros
		chksum_val = sum(full_msg_no_checksum.encode('utf-8')) % 256
		checksum_field = self._encode_field(10, f"{chksum_val:03d}")

		raw_msg = full_msg_no_checksum + checksum_field
		return raw_msg

	def validate_message(self, raw_message: str) -> Tuple[bool, str]:
		"""
		Validate a raw FIX message for correct BodyLength and CheckSum.

		Returns (is_valid, error_message). If valid, error_message is empty.
		"""
		if raw_message is None:
			return False, 'No message provided'
		try:
			# Ensure message uses SOH
			soh = self.SOH
			# Extract checksum field (10=nnn<SOH>) from the end
			if '10=' not in raw_message:
				return False, 'Missing checksum field'
			# split at last occurrence of SOH before checksum tag
			# find last occurrence of '%s10=' % SOH or just find '10=' from end
			ten_idx = raw_message.rfind('10=')
			if ten_idx == -1:
				return False, 'Checksum tag not found'
			# checksum field goes until the next SOH
			chksum_field = raw_message[ten_idx:]
			# separate supplied checksum
			supplied = None
			if chksum_field.startswith('10='):
				# value between '10=' and next SOH
				end_pos = chksum_field.find(soh)
				if end_pos != -1:
					supplied = chksum_field[3:end_pos]
				else:
					supplied = chksum_field[3:]
			else:
				return False, 'Malformed checksum field'

			# Compute expected checksum
			# expected checksum is sum of all bytes before the checksum field
			prefix = raw_message[:ten_idx]
			chksum_calc = sum(prefix.encode('utf-8')) % 256
			expected = f"{chksum_calc:03d}"
			if supplied != expected:
				return False, f'Checksum mismatch: expected {expected} got {supplied}'

			# Validate BodyLength
			# find tag 9 and its value
			nine_idx = raw_message.find('9=')
			if nine_idx == -1:
				return False, 'Missing BodyLength tag'
			nine_end = raw_message.find(soh, nine_idx)
			if nine_end == -1:
				return False, 'Malformed BodyLength field'
			supplied_len_str = raw_message[nine_idx + 2:nine_end]
			try:
				supplied_len = int(supplied_len_str)
			except Exception:
				return False, 'Invalid BodyLength value'

			# compute actual length: bytes after the SOH following the 9=... value up to before checksum tag
			pos_after_9 = nine_end + 1
			actual_bytes = raw_message[pos_after_9:ten_idx].encode('utf-8')
			actual_len = len(actual_bytes)
			if actual_len != supplied_len:
				return False, f'BodyLength mismatch: expected {supplied_len} actual {actual_len}'

			return True, ''
		except Exception as e:
			return False, f'Exception during validation: {e}'


