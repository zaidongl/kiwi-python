import yaml
import logging
from typing import Any, Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class FixTemplate:
	"""Load and render FIX message templates defined in YAML.

	Template YAML schema (simple, flexible):

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

	The class provides helpers to load templates and build a flattened list of
	(tag, value) tuples suitable for passing to a FIX message builder.
	"""

	def __init__(self):
		self.templates: Dict[str, Dict[str, Any]] = {}

	def load_from_file(self, path: str) -> None:
		with open(path, 'r', encoding='utf-8') as fh:
			data = yaml.load(fh, Loader=yaml.FullLoader)
		self._load_data(data)

	def load_from_string(self, content: str) -> None:
		data = yaml.load(content, Loader=yaml.FullLoader)
		self._load_data(data)

	def _load_data(self, data: Dict[str, Any]) -> None:
		if not data:
			return
		templates = data.get('templates') or data
		for name, tpl in templates.items():
			self.templates[name] = tpl

	def get_template(self, name: str) -> Optional[Dict[str, Any]]:
		return self.templates.get(name)

	def _render_value(self, template_val: Any, context: Dict[str, Any]) -> Optional[str]:
		"""Render a template value. If template_val is a string with {placeholders}
		perform format substitution using context. Otherwise return str(template_val).
		If placeholder not found, returns None.
		"""
		if template_val is None:
			return None
		if not isinstance(template_val, str):
			return str(template_val)
		# simple placeholder rendering using str.format_map with missing keys -> KeyError
		try:
			# allow usage of braces directly; use format_map with a dict-like that returns placeholder when missing
			rendered = template_val.format_map(DefaultDict(context))
			# if there are unresolved placeholders (still contain '{' and '}') treat as missing
			if '{' in rendered and '}' in rendered:
				return None
			return rendered
		except Exception:
			# if formatting fails, return the raw string
			return template_val

	def build_fields(self, template_name: str, values: Dict[str, Any]) -> List[Tuple[int, str]]:
		"""
		Build and return a list of (tag, value) tuples from the named template using provided values.

		Args:
			template_name: name of the template to use
			values: dict of placeholder values; for repeating groups provide a list under the group's name

		Returns:
			list of (tag:int, value:str)
		"""
		tpl = self.get_template(template_name)
		if tpl is None:
			raise KeyError(f"Template '{template_name}' not found")

		context = dict(values or {})
		fields: List[Tuple[int, str]] = []

		# header
		header = tpl.get('header', []) or []
		for entry in header:
			if isinstance(entry, list) and len(entry) >= 2:
				tag = int(entry[0])
				val = str(entry[1])
				fields.append((tag, val))
			elif isinstance(entry, dict):
				tag = int(entry.get('tag'))
				val = entry.get('value')
				val_rendered = self._render_value(val, context)
				if val_rendered is not None:
					fields.append((tag, val_rendered))

		# body
		body = tpl.get('body', []) or []
		for fld in body:
			if isinstance(fld, dict) and fld.get('repeating'):
				# repeating group
				group_tag = int(fld['tag'])
				group_name = fld.get('name') or str(group_tag)
				group_instances = context.get(group_name) or context.get(str(group_tag)) or []
				if not isinstance(group_instances, list):
					raise ValueError(f"Repeating group '{group_name}' requires a list of instances")
				# first add count
				fields.append((group_tag, str(len(group_instances))))
				group_template = fld.get('group') or []
				for instance in group_instances:
					# instance is dict; merge with parent context for rendering
					inst_ctx = dict(context)
					if isinstance(instance, dict):
						inst_ctx.update(instance)
					for gfld in group_template:
						gtag = int(gfld['tag'])
						gval_tpl = gfld.get('value')
						rendered = self._render_value(gval_tpl, inst_ctx)
						if rendered is None:
							rendered = ''
						fields.append((gtag, rendered))
			else:
				# normal field
				tag = int(fld['tag']) if isinstance(fld, dict) else int(fld[0])
				val_tpl = fld.get('value') if isinstance(fld, dict) else (fld[1] if len(fld) > 1 else None)
				name = fld.get('name') if isinstance(fld, dict) else None
				rendered = self._render_value(val_tpl, context)
				# required check
				if fld.get('required') and (rendered is None or rendered == ''):
					raise ValueError(f"Required field {name or tag} missing for template {template_name}")
				if rendered is None:
					rendered = ''
				fields.append((tag, rendered))

		return fields


class DefaultDict(dict):
	"""Helper mapping for format_map that returns the placeholder as-is if key missing."""

	def __missing__(self, key):
		return '{' + key + '}'


