# Various path operations
import os

# Used to import the plugins so they can be used
import imp

# To aide in plugin management, we use inspect.getfile(class) to get class path & filename
import inspect

"""
Holds all the enabled plugins (look up by type and name).

To use plugin "SendEmail", which is a task, do this inside of your plugin class:
self.email = self._PLUGINS["tasks"]["SendEmail"]
"""
_PLUGINS = {
}

# Reserved ames we skip over when checking for a valid plugin
_RESERVED = {
	"files" : ["__init__", "base", "register"]
}

class PluginRegistry(type):
	plugins = []
	def __init__(cls, name, bases, attrs):
		# We only allow classes who's name doesn't end in "Base" ("Base" is assumed to be like bases/db_base.py)
		if not name.endswith("Base"):
			try:
				# Attempt to add plugin only if its not marked as disabled (default: False).  'AttributeError' is raised if this is not set
				if not cls.plugin_disabled:
					dir_,file_ = os.path.split(os.path.abspath(inspect.getfile(cls)[:-1]))

					# We do this to get rid of having to specify _PLUGIN_CLASS in files, since things are structured
					# (_PLUGIN_CLASS was mandatory in v0.00000001 of this code)
					_,plugin_class = os.path.split(os.path.split(dir_)[0])

					# Try to register it in both the registry class and _PLUGINS lookup
					if not plugin_class in _PLUGINS:
						_PLUGINS[plugin_class] = {}

					# Plugin hasn't been loaded into the class, so we initialize the data and store things
					if not name in _PLUGINS[plugin_class]:
						print "> Discovered new",plugin_class,"plugin:",name
						
						fn,_ = os.path.splitext(file_)
						ref = cls()
						_PLUGINS[plugin_class][name] = {'ref' : ref, 'loader' : fn, 'dir' : dir_ }
					else:
						# This should never really be reached, but if so, it happens
						raise BaseException("Plugin \"%s\" was already found in class \"%s\"" % (name, cls.plugin_class))
			except AttributeError:
				raise BaseException("Plugin \"%s\" is missing attribute: plugin_disabled" % (name))

def get_plugins():
	return _PLUGINS

"""
Originally, this method only walked through the main directory.

However, as its very likely there will be many, many plugins, a more structured approach easier to maintain.

dir_ = Path of plugins to search, typically just leave it as ./plugins.
load = Whether to load or just see if a plugin exists in the directory.  Have it load them by default.
"""
def find_plugins(dir_="./plugins", load=True):
	plugin_info = {}
	path = ""
	plugin = ""
	base = ""

	for plugin_class in os.listdir(dir_):
		base = os.path.join(dir_, plugin_class)

		if os.path.isdir(base):
			for plugin_name in os.listdir(base):
				path = os.path.join(base, plugin_name)

				plugin = os.path.join(path, "%s.py" % (plugin_name))

				if os.path.isfile(plugin):
					fn, _ = os.path.splitext(plugin_name)

					if fn not in _RESERVED["files"]:
						info = imp.find_module(fn, [path])

						if info[0] and load:
							imp.load_module(fn, *info)

	return _PLUGINS