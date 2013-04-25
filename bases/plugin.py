from plugins.bases.registry import PluginRegistry, _PLUGINS, find_plugins
import imp
import os

class PluginBase(object):
	# Secret gem to make everything load properly
	__metaclass__ = PluginRegistry

	# Lets plugins call other plugins
	_PLUGINS = _PLUGINS

	# If true, the plugin won't be added to the plugins lookup table
	plugin_disabled = False

	# The path to the plugins (by default in the directory found here)
	_PLUGIN_PATH = "./plugins"

	# Establishes a reference to the plugin (__init__ should not be overriden)
	def __init__(self, *args, **kwargs):
		pass

	# Called to initialize data (any startup routines should go here)
	def init(self, *args, **kwargs):
		pass

	# Override this to do clean up when a plugin is ended/shut down
	def shutdown(self, *args, **kwargs):
		pass

	# No reason to override this, states the class the plugin is
	@property
	def plugin_type(self):
		return self.plugin_class

	# Don't override.  Returns the name of the plugin (i.e.: class name)
	@property
	def name(self):
		return self.__class__.__name__

	def get_name(self):
		return self.__class__.__name__

	"""
	This reloadsa specified plugin (reason?  I'm sure there'll come a time when this is necessary).

	Does it work?  One can only hope.
	"""
	@classmethod
	def reload_plugin(self, *args, **kwargs):
		# We need a plugin name, or else its pointless
		try:
			pname = kwargs['plugin_name']
		except:
			raise BaseException("Keyword argument 'plugin_name' missing in reload_plugin.  Must be the plugin name (typically self.name)")

		# To help speed things along, plugin_type=... can be passed to this method
		ptype = kwargs['plugin_type'] if "plugin_type" in kwargs else None

		info = None
		data = None

		# If the plugin type was passed, make things easier
		try:
			data = self._PLUGINS[ptype][pname]

			self._PLUGINS[ptype].pop(pname, None)
			info = imp.find_module(data['loader'], [data['dir']])
		except KeyError:
			# Get a list of all the plugins we have so far
			plugins = find_plugins(self._PLUGIN_PATH, load=False)

			# No plugin type given?  Well, lets cycle through everything!
			for type_ in plugins:
				for name,plugin in plugins[type_].items():
					if name == pname:
						data = plugins[type_][name]
						plugins[type_].pop(name, None)

						info = imp.find_module(data['loader'], [data['dir']])
						break

		try:
			if info[0]:
				try:
					imp.load_module(data['loader'], *info)
					return True
				except:
					return False
			else:
				return False
		except IndexError:
			return False

	"""
	Simple method to check if a plugin is actually loaded or not.

	- plugin_name Name of the plugin to check
	- pugin_type  Plugin class the plugin is in
	- load_plugin If plugin isn't loaded (found), load it?  (default: no)
	- force_reload If enabled (by default it isn't), reload the plugin anyways
	- args, kwargs - Arguments to pass to the plugin if a (re)load is to be performed
	"""
	def is_plugin_loaded(self, plugin_type, plugin_name, load_plugin=False, force_reload=False, *args, **kwargs):
		try:
			self._PLUGINS[plugin_type][plugin_name]

			if force_reload:
				data = self._PLUGINS[plugin_type][plugin_name]
				info = imp.find_module(data['loader'], [data['dir']])
				imp.load_module(data['loader'], *info)
			return True
		except KeyError:
			if load_plugin:
				path = os.path.join(self._PLUGIN_PATH, plugin_name)
				
				if os.path.isdir(path):
					info = imp.find_module(plugin_name, [path])
					imp.load_module(plugin_name, *info)
					return True
				else:
					return False
			else:
				return False

	"""
	Easier way of accessing a plugin (instead of calling self._PLUGINS[type][name].init(args,...))

	Simply call:
	self.get_plugin(type, name, args...)

	You're welcome.

	Returns None if the plugin doesn't exist (isn't loaded).
	"""
	def get_plugin(self, plugin_type, plugin_name, *args, **kwargs):
		return self._PLUGINS[plugin_type][plugin_name]['ref'].init(*args, **kwargs) if self.is_plugin_loaded(plugin_type, plugin_name) else None

	def get_plugin_type(self, plugin_name):
		t = None

		for type_, data in self._PLUGINS.iteritems():
			if plugin_name in data:
				t = type_
				break

		return t

	"""
	A property method to be overriden when wanting to specify default settings for the plugins on load.  Typically no need to mess with
	this, but an example as to why can be found in plugins/report/logger/logger.py.

	This acts as default kwargs (dictionary) for the plugin.
	"""
	@property
	def defaults(self):
		return {}