import time
import board
import busio
from adafruit_pca9685 import PCA9685

class MotorController:
    def __init__(self, ena, in1, in2, enb, in3, in4, pwm_frequency=60):
        # Motor control pins
        self.ENA = ena
        self.IN1 = in1
        self.IN2 = in2
        self.ENB = enb
        self.IN3 = in3
        self.IN4 = in4

        # Initialize I2C bus and PCA9685 module
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = pwm_frequency

        self.current_duty_cycle = 0

    def set_motor_duty_cycle(self, duty_cycle):
        self.current_duty_cycle = max(0, min(1.0, duty_cycle))

        # Set PWM duty cycle for motor speed
        self.pca.channels[self.ENA].duty_cycle = int(self.current_duty_cycle * 0xFFFF)
        self.pca.channels[self.ENB].duty_cycle = int(self.current_duty_cycle * 0xFFFF)
        
        if self.current_duty_cycle == 0:
            self.pca.channels[self.IN1].duty_cycle = 0
            self.pca.channels[self.IN2].duty_cycle = 0
            self.pca.channels[self.IN3].duty_cycle = 0
            self.pca.channels[self.IN4].duty_cycle = 0
        else:
            self.pca.channels[self.IN1].duty_cycle = 0xFFFF
            self.pca.channels[self.IN2].duty_cycle = 0
            self.pca.channels[self.IN3].duty_cycle = 0xFFFF
            self.pca.channels[self.IN4].duty_cycle = 0

        print("Motor duty cycle set to:", self.current_duty_cycle)

    def stop(self):
        self.set_motor_duty_cycle(0)
        self.pca.deinit()
        print("Motor control stopped.")
