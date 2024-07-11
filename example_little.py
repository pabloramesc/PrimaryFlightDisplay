"""
 Copyright (c) 2022 Pablo Ramirez Escudero
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""
import sys
import pygame
from time import time
import numpy as np
from pfd import AircraftState, PrimaryFlightDisplay

FPS = 1000
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

PFD = PrimaryFlightDisplay((SCREEN_WIDTH, SCREEN_HEIGHT), masked=True, max_fps=60, little=True)

f1 = 1 / 90
f2 = 1 / 60

t0 = time()

while True:
    t = time() - t0
    state = AircraftState(
        pitch = 25.0 * np.sin(2 * np.pi * f1 * t),
        roll = 60.0 * np.sin(2 * np.pi * f2 * t),
        airspeed = 25.0 + 10.0 * np.cos(2 * np.pi * f1 * t),  # m/s
        airspeed_cmd=25.0,
        vspeed = 100.0 * np.sin(2 * np.pi * f1 * t),  # m per minute
        altitude = 80.0 - (100.0 * 60 / 2 * np.pi * f1) * np.cos(2 * np.pi * f1 * t),  # meters
        altitude_cmd=100.0,
        heading=20.0 - 20.0 * np.cos(2 * np.pi * f2 * t),
        heading_cmd=20.0,
        course=20.0 - 20.0 * np.cos(2 * np.pi * f2 * t) * np.sin(2 * np.pi * f1 * t),
    )
    
    PFD.update(state, t)
    PFD.draw()
    PFD.render()

    print(
        f"t={t:.2f}s fps={PFD.fps:.0f} Pitch={state.pitch:.2f}deg Roll={state.roll:.2f}deg Airspeed={state.airspeed:.2f}m"
        f" Vspeed={state.vspeed:.2f}m/min Altitude={state.altitude:.2f}m Heading={state.heading:.2f}deg"
    )

