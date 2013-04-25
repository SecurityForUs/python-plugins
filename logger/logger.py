"""
This is the default logger plugin.  Using it is pretty easy.

In your plugin, just load a reference to the plugin:
self.log = self.get_plugin("tasks", "Logger", args)

Where args are keyword arguments of the following:
console_level  - Lowest logging level required for the message to be sent to the terminal/console (see: _LOG_LEVELS)
console_format - How to present the data (use Python's logging tutorial for message formatting)
log_file       - True if using a log file as well, False if only logging to console (default)
file_format    - Same as console_format, but for the log file
file_level     - Same as console_level, but for the log file
name           - The name of the logger (advisable to just pass self.name to not cause conflicts)

Defaults are specified in the init() method for ideas on how to configure this.

Each plugin will have a reference to their own logger, meaning each plugin can configure the logger the way they want it to be done.
"""
from plugins.bases.tasks import Task_Base
import logging
import logging.config
import os

_LOG_LEVELS = {
	'DEBUG' : logging.DEBUG,
	'WARN' : logging.WARNING,
	'INFO' : logging.INFO,
	'ERR' : logging.ERROR,
	'CRIT' : logging.CRITICAL
}

class Logger(Task_Base):
	@property
	def defaults(self):
		return {'name' : "logger.base"}

	def init(self, *args, **kwargs):
		# A name must be given to the logger (just pass self.name)
		try:
			name = kwargs['name']
		except KeyError:
			raise BaseException("No logger name passed as keyword argument (name=...)")

		# Initialize (or retrieve) a logger by the name
		log = logging.getLogger(name)

		# Settings for writing to the console
		console_level = _LOG_LEVELS[kwargs['console_level'] if "console_level" in kwargs else "DEBUG"]
		console_fmt = kwargs['console_format'] if "console_format" in kwargs else "DBG: %(module)s: %(lineno)d: %(message)s"

		# Should we log to a file? (default: False/no)
		do_file_logging = kwargs['log_file'] if "log_file" in kwargs else False

		# Initialize a basic logging structure
		logging.basicConfig()

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

		# Create a stream handler so we can write to the console, and pretty it up with settings
		console = logging.StreamHandler()
		console.setLevel(console_level)
		fmt = logging.Formatter(console_fmt)
		console.setFormatter(fmt)
		log.addHandler(console)

		# Return the finalized logger
		return log