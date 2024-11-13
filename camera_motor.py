# motor_control.py
from gpiozero import OutputDevice
import time

class MotorControl:
    def __init__(self, dir_pin=22, step_pin=23, enable_pin=24):
        # Inicjalizacja pinów GPIO
        self.DIR_PIN = OutputDevice(dir_pin)      # Kierunek obrotów
        self.STEP_PIN = OutputDevice(step_pin)    # Krok
        self.ENABLE_PIN = OutputDevice(enable_pin)  # Włączanie (LOW = włączony)
        
        # Ustawienia początkowe
        self.ENABLE_PIN.off()  # Ustaw ENABLE na LOW, aby włączyć sterownik

    def rotate_motor(self, steps, direction=False, step_delay=0.001):
        
        # Ustawienie kierunku
        self.DIR_PIN.value = direction

        # Kroki silnika z minimalnym opóźnieniem
        for _ in range(steps):
            self.STEP_PIN.on()
            time.sleep(step_delay)  # Minimalne opóźnienie
            self.STEP_PIN.off()
            time.sleep(step_delay)  # Minimalne opóźnienie

    def disable_motor(self):
        """Wyłączenie silnika, ustawiając ENABLE na HIGH"""
        self.ENABLE_PIN.on()
