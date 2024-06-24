# -*- coding: utf-8 -*-
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.
# Copyright (C) 2024 Ángel Reyes <angeldelosreyesfaz@gmail.com>

"""
La función de este addon es monitorear la batería del sistema.
"""

#Importamos las librerías del núcleo de NVDA
import globalPluginHandler
import ui
import tones
import globalVars
import addonHandler
addonHandler.initTranslation()
from scriptHandler import script
#Importamos librerías externas a NVDA
import os
import threading
import time
import sys

dirAddon=os.path.dirname(__file__)
sys.path.append(dirAddon)
sys.path.append(os.path.join(dirAddon, "lib"))
import psutil
psutil.__path__.append(os.path.join(dirAddon, "lib", "psutil"))
del sys.path[-2:]
from .timer import Timer
def disableInSecureMode(decoratedCls):
	"""
	Decorador para deshabilitar el uso de la clase a decorar en pantallas seguras.
	"""
	if globalVars.appArgs.secure: #Si se detecta la ejecución en este tipo de pantallas, se devuelve una instancia sin modificar de globalPluginHandler.GlobalPlugin, si no es así se devuelve la clase decorada.
		return globalPluginHandler.GlobalPlugin
	return decoratedCls

@disableInSecureMode #Se llama al decorador para deshabilitar el uso del complemento en pantallas seguras.
class GlobalPlugin (globalPluginHandler.GlobalPlugin):
	"""
	Clase que hereda de globalPluginHandler.GlobalPlugin para hacer los scripts relacionados a cada combinación de teclas pulsada, así como otras operaciones lógicas para el funcionamiento del addon.
	"""
	#Translators: name of the addon category that will appear in the input gestures section.
	scriptCategory = _("Battery Check")
	def __init__(self):
		"""
		Método de inicialización de la clase donde se inicializan valores tanto para la clase padre como para la clase hija (la actual).
		"""
		super(GlobalPlugin, self).__init__() #Se inicializa la clase padre con sus valores.

		#Se inicializan los valores de la instancia actual para su control.
		self.monitoring = False
		self.monitoringThread = None
		self.stopThread = False

	def terminate(self):
		self.stopMonitoring()

	def startMonitoring(self):
		battery = psutil.sensors_battery()
		if battery is None:
			ui.message(_("No hay batería del sistema."))
			return

		if not self.monitoring:
			self.monitoring = True
			self.monitoringThread = threading.Thread(target=self.checkBattery)
			self.monitoringThread.start()

			ui.message(_("Monitoreo de la batería iniciado."))

	def stopMonitoring(self):
		if self.monitoring:
			self.monitoring = False
			if self.monitoringThread is not None:
				self.stopThread = True
				self.monitoringThread = None
				self.stopThread = False

			ui.message(_("Monitoreo de la batería finalizado."))

	def checkBattery(self):
		verify = Timer()
		beep = Timer()
		needs_beep = False
		while self.monitoring and not self.stopThread:
			if verify.elapsed(1, False):
				verify.restart()
				battery = psutil.sensors_battery()
				needs_beep = (battery is not None and battery.percent == 100 and battery.power_plugged)
				if not battery.power_plugged:
					self.stopMonitoring()

			if needs_beep and beep.elapsed(10, False):
				beep.restart()
				tones.beep(432, 500)
				ui.message(_("¡Batería totalmente cargada!"))

			time.sleep(0.05)

	#Decorador para asignarle su descripción y atajo de teclado a esta función del addon.
	#Translators: The function of the command is described, which is to start or stop the battery monitoring.
	@script(
		description=_("Inicia o detiene el monitoreo de la batería."),
		gesture=None
	)
	def script_manageMonitoring(self, gesture):
		"""
		Método que ejecuta la acción de iniciar o detener el monitoreo de la batería.
		"""
		if not self.monitoring:
			self.startMonitoring()

		else:
			self.stopMonitoring()
