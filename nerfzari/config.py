"""
"""

import abc
import json
import jsonschema


class Configurable(metaclass=abc.ABCMeta):
	"""An abstract class that lets people know your class can read a config"""
	@abc.abstractclassmethod
	def from_cfg(cls):
		pass


class ConfigStore(object):
	"""One stop shop for managing the various config files modules will need."""
	_configs = {}
	
	@staticmethod
	def _validate_with_defaults(instance, schema, cls=None, *args, **kwargs):
		"""Taken from the jsonschema docs FAQ, fills in defaults then validates"""
		def extend_with_default(validator_class):
			validate_properties = validator_class.VALIDATORS["properties"]
			def set_defaults(validator, properties, instance, schema):
				for property, subschema in properties.items():
					if "default" in subschema:
						instance.setdefault(property, subschema["default"])
				for error in validate_properties(
					validator, properties, instance, schema,
				):
					yield error
			return jsonschema.validators.extend(
				validator_class, {"properties" : set_defaults},
			)
		if cls is None:
			cls = jsonschema.validators.validator_for(schema)
		dcls = extend_with_default(cls)
		# NOTE: using the base class here is a workaround to avoid a bug in this example
		cls.check_schema(schema)
		dcls(schema, *args, **kwargs).validate(instance)

	@staticmethod
	def register(path, schema):
		ConfigStore._configs[path] = {
			'schema': schema
		}

	@staticmethod
	def set(path, cfg):
		meta = ConfigStore._configs[path]
		jsonschema.validate(cfg, meta['schema'])
		if 'cfg' not in meta:
			meta['cfg'] = {}
		meta['cfg'].update(cfg)

	@staticmethod
	def get(path):
		meta = ConfigStore._configs[path]
		if 'cfg' not in meta:
			ConfigStore.load(path)
			meta = ConfigStore._configs[path]
		return meta['cfg']

	@staticmethod
	def load(path):
		meta = ConfigStore._configs[path]
		with open(path, 'r') as f:
			cfg = json.load(f)
		ConfigStore._validate_with_defaults(cfg, meta['schema'])
		ConfigStore._configs[path]['cfg'] = cfg

	@staticmethod
	def load_all():
		for key in ConfigStore._configs.keys():
			ConfigStore.load(key)

	@staticmethod
	def save(path):
		meta = ConfigStore._configs[path]
		jsonschema.validate(meta['cfg'], meta['schema'])
		if 'cfg' in meta:
			with open(path, 'w') as f:
				json.dump(meta['cfg'], f)

	@staticmethod
	def save_all():
		for path in ConfigStore._configs.keys():
			ConfigStore.save(path)
