# Copyright (C) 2024 Mateo Cedillo <angelitomateocedillo@gmail.com>
# This file is covered by the GNU General Public License.
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# imports:
from gui import guiHelper
# To support future NVDA versions with API updates.
from gui.settingsDialogs import SettingsPanel
import wx
import config
import addonHandler

addonHandler.initTranslation()

class battery_check_Settings(SettingsPanel):
	title = _("Battery Check")
	def makeSettings(self, settingsSizer):
		Helper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		self.AutoMonitor = Helper.addItem(wx.CheckBox(self, label=_("Monitorear la batería cuando inicie NVDA")))
		self.StartMonitorAtConnect = Helper.addItem(wx.CheckBox(self, label=_("Monitorear automáticamente la batería cuando se conecte el cargador")))
		self.BatteryPercentLimit = Helper.addLabeledControl(_("Porcentaje de batería máximo desde que se empezará a emitir la alerta"), wx.SpinCtrl)
		self.AutoMonitor.SetValue(config.conf["battery_check"]["AutoMonitor"])
		self.StartMonitorAtConnect.SetValue(config.conf["battery_check"]["StartMonitorAtConnect"])
		self.BatteryPercentLimit.SetValue(config.conf["battery_check"]["BatteryPercentLimit"])

	def onSave(self):
		config.conf["battery_check"]["AutoMonitor"] = self.AutoMonitor.GetValue()
		config.conf["battery_check"]["StartMonitorAtConnect"] = self.StartMonitorAtConnect.GetValue()
		config.conf["battery_check"]["BatteryPercentLimit"] = self.BatteryPercentLimit.GetValue()
