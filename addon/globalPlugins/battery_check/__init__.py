# -*- coding: utf-8 -*-
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.
# Copyright (C) 2024 Ángel Reyes <angeldelosreyesfaz@gmail.com>

"""
La función de este addon es monitorear la batería del sistema y emitir un aviso al esta llegar al 100%.
"""

#Importamos las librerías del núcleo de NVDA
import config
from gui import settingsDialogs
import globalPluginHandler
import ui
import tones
import globalVars
import config
import addonHandler
addonHandler.initTranslation()
from scriptHandler import script
#Importamos librerías externas a NVDA
import os
import threading
import time
import sys
import psutil
from .timer import Timer
from .settings import battery_check_Settings

def disableInSecureMode(decoratedCls):
	"""
	Decorador para deshabilitar el uso de la clase a decorar en pantallas seguras.
	"""
	if globalVars.appArgs.secure: #Si se detecta la ejecución en este tipo de pantallas, se devuelve una instancia sin modificar de globalPluginHandler.GlobalPlugin, si no es así se devuelve la clase decorada.
		return globalPluginHandler.GlobalPlugin
	return decoratedCls

confspec = {
	# se establecen opciones por defecto para el complemento. En este caso, el monitoreo estará desactivado.
	"AutoMonitor": "boolean(default=False)"
}
config.conf.spec["battery_check"] = confspec

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

		# Establecemos ajustes de usuario para el  complemento a una nueva categoría en las opciones de NVDA.
		settingsDialogs.NVDASettingsDialog.categoryClasses.append(battery_check_Settings)
		#Se inicializan los valores de la instancia actual para su control.
		self.monitoring = False
		self.monitoringThread = None
		self.stopThread = False

		# Se verifica la opción de monitoreo cuando NVDA se inicia. Si el usuario la activó, empezará la acción.
		if config.conf["battery_check"]["AutoMonitor"]:
			self.startMonitoring(True) # Agregamos True como argumento para evitar mensajes de aviso del monitoreo al iniciar.

	def terminate(self):
		"""
		Método que se ejecuta al salir de NVDA para cerrar adecuadamente todo lo que se tenga que cerrar.
		"""
		self.stopMonitoring()
		settingsDialogs.NVDASettingsDialog.categoryClasses.remove(battery_check_Settings)

	def startMonitoring(self, quiet=False):
		"""
		Método que ejecuta la acción de iniciar el monitoreo de la batería.
		"""
		battery = psutil.sensors_battery() #Se crea una instancia de sensors_battery para verificar si existe batería en el sistema.
		if battery is None: #Si no es así se emite un mensaje y se detiene la ejecución del método.
			#Translators: Message to inform the user that there is no battery in the system.
			if not quiet: ui.message(_("No hay batería del sistema."))
			return

		if not self.monitoring: #Se verifica si el monitoreo no está activado para si es así, iniciarlo.
			self.monitoring = True
			self.monitoringThread = threading.Thread(target=self.checkBattery)
			self.monitoringThread.start()
			#Translators: Message to indicate that battery monitoring has started.
			if not quiet: ui.message(_("Monitoreo de la batería iniciado."))

	def stopMonitoring(self, quiet=False):
		"""
		Método que ejecuta la acción de detener el monitoreo de la batería.
		"""
		if self.monitoring: #Se verifica si el monitoreo está activado para si es así, detenerlo.
			self.monitoring = False
			if self.monitoringThread is not None:
				self.stopThread = True
				self.monitoringThread = None
				self.stopThread = False

			#Translators: Message to indicate that battery monitoring has finished.
			if not quiet: ui.message(_("Monitoreo de la batería finalizado."))

	def checkBattery(self):
		"""
		Método que se ejecuta en otro hilo y que estará monitoreando constantemente el porcentaje y estado de la batería.
		"""
		#Se instancian 2 objetos de temporizador y se inicializa una variable de control en False.
		verify = Timer()
		beep = Timer()
		needs_beep = False
		batteryStatus = None
		while self.monitoring and not self.stopThread: #Bucle while para mantener la monitorización, la condición para mantener este activo será que si el monitoreo está activado y no se ha establecido la variable stopThread en True entonces seguirá funcionando.
			if verify.elapsed(1, False): #Se verifica cada segundo si existe batería en el sistema, si el porcentaje de la misma es 100% y si está conectada a la corriente, para si es así entonces establecer una variable de control en True, encargada de manejar el temporizador de los avisos.
				verify.restart()
				battery = psutil.sensors_battery()
				if batteryStatus is None:
					batteryStatus = battery.power_plugged

				needs_beep = (battery.percent == 100 and batteryStatus)
				if not batteryStatus and config.conf['batterycheck']['startMonitorAtConnect'] is False: #Si la batería ya no está conectada pero sigue el monitoreo (el bucle ejecutándose y a menos de que la monitorización al conectarse esté desactivada) este se detiene.
					self.stopMonitoring()

				if batteryStatus != battery.power_plugged:
					batteryStatus = battery.power_plugged
					ui.message(_("Batería {}.".format('conectada' if batteryStatus else 'desconectada')))

			if needs_beep and beep.elapsed(10, False): #Si la variable de control está establecida en True y pasan 10 segundos, entonces se emite un tono y se lanza un aviso por el TTS.
				beep.restart()
				tones.beep(432, 500)
				#Translators: Message to indicate to the user that their battery is fully charged.
				ui.message(_("¡Batería totalmente cargada!"))

			time.sleep(0.05) #Se hace una espera de 5 milisegundos para no matar el CPU.

	#Decorador para asignarle su descripción y atajo de teclado a esta función del addon.
	#Translators: The function of the command is described, which is to start or stop the battery monitoring.
	@script(
		description=_("Inicia o detiene el monitoreo de la batería"),
		gesture=None
	)
	def script_manageMonitoring(self, gesture):
		"""
		Método que ejecuta la acción de iniciar o detener el monitoreo de la batería.
		"""
		if not self.monitoring: #Se verifica si el monitoreo no está activado para si es así activarlo y viceversa.
			self.startMonitoring()

		else:
			self.stopMonitoring()
