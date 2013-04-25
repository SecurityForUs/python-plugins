python-plugins
==============

Modular plugin system that's generic enough for any project, and works for vast majority of projects.

Plugin Architecture
-------------------
This is a plugin system to use in various projects.  The main purpose of this is to fit the needs of our various projects, and as such make it easy for a centralized code base.

How to Store Plugins
---------------------
Below is the structure of the plugin system:

```plugins/<plugin type>/<plugin name>/<plugin name>.py```

When the plugin system is initialized (by calling ```plugins.registry.find_plugins()```), it will search the plugins directory.  It will then store the plugins based on class, then by name.  So if you have a HTML report generator plugin, the structure will look like this:

```
plugins/reports/html/html.py
```

The registry will save the plugin as _PLUGINS["reports"]["html"], and you can use ```get_pugin()``` in BasePlugin (see: plugins/bases/plugin.py) to retrieve the plugin.

When the plugin is stored, three different aspects are saved.

## Reference
The reference (class initialization [```__init__()```]), which should always be empty.  This just makes it so a different instance of the plugin can be initialized without reloading the same plugin over and over.

## Loader
The filename of the plugin, used for reloading the plugin (or enabling it).

## Directory
The directory is saved because the plugin system needs to know where to save it, and it seemed like a good idea to do it this way instead of reading the dictionary values.

How To Use Plugins
-------------------
This system was designed to make it easy to use plugins.  Howeve, first the plugins have to be loaded, which can be done by calling ```find_plugins()``` like this:

```python
from plugins.registry import find_plugins

if __name__ == "__main__":
	plugins = find_plugins()
```

In order to use the logger plugin, for example, you just do this in your ```init()``` method (or elsewhere):

```python
self.log = self.get_plugin("reports", "Logger", name=self.name)
```

Other arguments are possible, but those are the mandatory ones for the logger.  See the plugin for more options.

Please note that plugin system was designed to work within other plugins only, but this will be changed soon.

Writing Plugins
----------------
To create a plugin is as easy as writing Python code.  The only absolute requirement is for your plugin to subclass a base (see: plugins/bases/).  Besides that, you can do as much or as little as you feel like.

The reason to subclass a base (preferably only one) are:

1. This is the only way really to have a plugin registered and loadable
2. Skeleton definitions are always nice for a framework
3. Easier to classify files beyond folder structure
4. Can use multiple bases in one plugin if need-be or desired (i.e.: one class subclasses report, another subclasses a scanner*)

* - This should still be broken up into separate plugins and such, but hey...anything's possible, right?

What Is Mandatory In A Plugin?
-------------------------------
Plugins, by default, should have at least a init() method (**NOT** __init__(), more on this soon).  This will be where you initialize data (i.e.: create a logger, save some data, check if something exists, etc...).  Beyond this, it is more of what the plugin is supposed to do, and what methods are in the base.

For example, if you want to provide default settings when initializing, simply override the defaults property:

```python
class SomeClass(SomeBase):
    @property
    def defaults(self):
        return {'kwarg1' : 'val1', 'kwarg2' : 'val2', etc...}
```

It is highly advisable that plugins accept only ```*arg``` and ```**kwarg``` arguments, however.  Not only does it make it easier for others to use your plugin, but it also requires less backwards compatibility when changing code around as well.

How To Create A Plugin Reference
---------------------------------
Creating a plugin reference is quite easy.  This has to be done in order to use a plugin (i.e.: use the logger plugin in a scan plugin).

```python
class SomeClass(SomeBase):
    def init(self, *args, **kwargs):
        self.logger = self.get_plugin("report", "Logger", arg1, arg2, argn, kwarg1, kwarg2, kwargn)

        # Every init() should return self for sake of issues
        return self
```

In hopes that the plugin is well (or at least semi-well) documented, it should state what needs to be passed as arguments, or at the very least raise exceptions when its missing.

```get_plugin``` is found in plugins/bases/plugin.py and is passed along to every plugin that subclasses it (or the class that subclasses it).  There are also some other helpful functions as well.

Why Not To Use ```__init__()```
-------------------------
Well, the biggest reason of all is that the plugin's ```__init__``` method is called when loading the plugin **ONLY**.  This means if you want to initialize data every time the plugin is used, it will only happen once here.  This is why every plugin has to have a init() method, even if you just have "pass" in it (which the base class does).

This was intentionally designed this way as we wanted a way to make plugins usable across the board, but without having restrictions of what can be initialized.

Bases: How and Why
------------------
Base classes provide a sort of interface with the most basic plugin subclass (plugins/bases/plugin.py), while also providing specifics of a specific plugin type.  For example, you don't necessarily need code to handle creating a report if you're writing a logger, so it wouldn't make sense to pile every possible instance into one class and just subclass that.

If a base class is missing and you feel it should exist, definitely feel free to write it up and create a pull request.  We aren't able to think of every instance possible, or know how to work with one, and this solution is meant to be a community effort.

Tutorial: Logging Plugin
-------------------------
The code base for a simple plugin for logging can be found in plugins/report/logger.  This is a simple plugin that basically wraps the Python logger while also providing a standard/universal interface to it for all needs.  Basically this section will go over the thoughts behind it, etc...

```
from plugins.bases.reports import Report_Base
import logging
import logging.config
import os
```
We want to subclass the logger to reports, so we import the base class.  The rest are either logger-specific or to make filenames easier to manage.

```python
_LOG_LEVELS = {
	'DEBUG' : logging.DEBUG,
	'WARN' : logging.WARNING,
	'INFO' : logging.INFO,
	'ERR' : logging.ERROR,
	'CRIT' : logging.CRITICAL
}
```
Global data to make it easier.  Could be placed inside of the class reference itself, but why make things even more easier to manipulate? ;)

```python
class Logger(Report_Base):
```
Every plugin is a class that subclasses a specific type.  The name of the class, for all intents and purposes, should match the filename (casing not mandatory).  When the plugin is loaded, it's ```__init__()``` method is called (which should be only from the Base).  From there, a new instance can be spawned anywhere by calling its ```init()``` method.

```python
	@property
	def defaults(self):
		return {'name' : "logger.base"}
```
Set some defaults of the plugin.  So when the plugin is first initialized, we can pass plugin.defaults to it (by default, ```defaults``` is ```{}```).

```python
	def init(self, *args, **kwargs):
		# A name must be given to the logger (just pass self.name)
		try:
			name = kwargs['name']
		except KeyError:
			raise BaseException("No logger name passed as keyword argument (name=...)")
```
We need the name of the logger to use (class' name).  If its not found, raise an exception.

```python
		# Initialize (or retrieve) a logger by the name
		log = logging.getLogger(name)

		# Settings for writing to the console
		console_level = _LOG_LEVELS[kwargs['console_level'] if "console_level" in kwargs else "DEBUG"]
		console_fmt = kwargs['console_format'] if "console_format" in kwargs else "DBG: %(module)s: %(lineno)d: %(message)s"
```
Create (or retrieve) a logger by the name given, and set some default values for stdout/stderr.

```python
		# Should we log to a file? (default: False/no)
		do_file_logging = kwargs['log_file'] if "log_file" in kwargs else False

		# Initialize a basic logging structure
		logging.basicConfig()
```
Check if we should do logging to a file too or not, and initialize the logger with some empty configurations.

```python
		# Do file logging
		if do_file_logging:
			# Log stuff to <install path>/logs/<name>.log (makes things easier)
			log_file = os.path.join(os.path.abspath("."), "logs", "%s.log" % (name))

			# File type specifications
			file_fmt = kwargs['file_format'] if "file_format" in kwargs else "%(asctime)s %(module)-20s %(levelname)s %(message)s"
			file_level = _LOG_LEVELS[kwargs['file_level'] if "file_level" in kwargs else "ERR"]

			# Create the handler and make it usable
			file_handler = logging.FileHandler(filename=log_file)
			file_handler.setLevel(file_level)
			fmt = logging.Formatter(file_fmt)
			file_handler.setFormatter(fmt)
			log.addHandler(file_handler)
```
If we are to log to a file, specify the log file, and set some formatting and settings for the file.  By default we only log error messages and higher.

```python
		# Create a stream handler so we can write to the console, and pretty it up with settings
		console = logging.StreamHandler()
		console.setLevel(console_level)
		fmt = logging.Formatter(console_fmt)
		console.setFormatter(fmt)
		log.addHandler(console)
```
Regardless if we log to a file, we still also output it to the console.  Similar code as the file, but for the console.

```python
		# Return the finalized logger
		return log
```
Return a reference of the log handler we set up (plugins should either return a variable [i.e.: ```log```] or ```self```, otherwise they are kind of useless).