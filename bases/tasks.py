from plugins.bases.plugin import PluginBase

class Task_Base(PluginBase):
	# Override to disable plugin from operating (won't be loaded)
	plugin_disabled = False

	# Cron format of scheduling tasks (empty if not being scheduled)
	task_cron = {}

	"""
	Various options to initialize the database (override this in your task class)
	"""
	def init(self, *args, **kwargs):
		pass

	# When tasks are created within celery, the task name will be the class name (see: @property/name in plugins/bases/base.py)
	@property
	def task_name(self):
		return self.name

	"""
	Override to perform task.
	"""
	def run(self, *args, **kwargs):
		pass