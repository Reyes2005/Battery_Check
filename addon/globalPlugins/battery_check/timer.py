# -*- coding: utf-8 -*-
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.
# Copyright (C) 2024 Ángel Reyes <angeldelosreyesfaz@gmail.com>

#Importamos la librería time que será utilizada para medir intervalos de tiempo.
import time

class Timer:
    def __init__(self):
        # Se inicializa el temporizador con el tiempo actual y se establece Elapsed a 0.
        self.last_time = time.time()
        self.Elapsed = 0

    def elapsed(self, interval, ms=True):
        """
        Método que verifica si ha transcurrido un intervalo de tiempo específico desde la última vez que se verificó.
        """
        # Obtiene el tiempo actual.
        current_time = time.time()
        # Calcula el nuevo tiempo transcurrido desde la última vez que se verificó.
        new_time = (current_time - self.last_time) * 1000 if ms else (current_time - self.last_time)
        if new_time >= interval:
            # Si ha transcurrido el intervalo de tiempo especificado, actualiza last_time y Elapsed.
            self.last_time = current_time
            self.Elapsed = new_time
            return True
        return False

    def restart(self):
        """
        Método que reinicia el temporizador, estableciendo last_time al tiempo actual.
        """
        self.last_time = time.time()
