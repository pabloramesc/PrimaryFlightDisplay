"""
 Copyright (c) 2022 Pablo Ramirez Escudero
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

import sys
from dataclasses import dataclass
from datetime import timedelta

import numpy as np
import pygame

from .airspeed import AirspeedIndicator
from .airspeed_little import AirspeedIndicatorLittle
from .altimeter import AltitudeIndicator
from .altimeter_little import AltitudeIndicatorLittle
from .attitude import ArtificalHorizon
from .heading import HeadingIndicator
from .vspeed import VerticalSpeedIndicator
from .vspeed_little import VerticalSpeedIndicatoLittle


@dataclass
class AircraftState:
    ### artificial horizon inputs
    roll: float
    pitch: float
    ### airspeed indicator inputs
    airspeed: float
    airspeed_cmd: float
    ### altitude indicator inputs
    altitude: float
    altitude_cmd: float
    ### vspeed indicator inputs
    vspeed: float
    ### heading indicator inputs
    heading: float
    heading_cmd: float
    course: float


class PrimaryFlightDisplay:
    def __init__(self, resolution: tuple, **kwargs) -> None:
        self.resolution = resolution

        pygame.init()
        self.game_clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.resolution[0], self.resolution[1]))
        self.screen_rect = self.screen.get_rect()
        pygame.display.set_caption("Primary Flight Display - v1.0")

        self.max_fps = kwargs.get("max_fps", None)
        self.fps = 0.0

        self.size = min(self.resolution)
        self.unit = self.size / 16

        self.artifical_horizon = ArtificalHorizon(self.screen, size=self.size / 2)
        self.airspeed_indicator = AirspeedIndicator(
            self.screen,
            size=self.size / 2,
            position=(self.screen_rect.center[0] - self.unit * 5, self.screen_rect.center[1]),
        )
        self.altitude_indicator = AltitudeIndicator(
            self.screen,
            size=self.size / 2,
            position=(self.screen_rect.center[0] + self.unit * 5, self.screen_rect.center[1]),
        )
        self.vspeed_indicator = VerticalSpeedIndicator(
            self.screen,
            size=self.size / 2.5,
            position=(self.altitude_indicator.background_rect.right + self.size / 100, self.screen_rect.center[1]),
        )
        self.heading_indicator = HeadingIndicator(
            self.screen,
            size=self.size / 2,
            position=(self.screen_rect.center[0], self.screen_rect.center[1] + self.unit * 5),
        )

        self.render_rects = [self.screen_rect]
        self.text_color = (0, 0, 0)

        self.masked = kwargs.get("masked", False)
        if self.masked:
            self.render_rects = self.get_render_rects()
            self.text_color = (255, 255, 255)
            self.ah_screen = pygame.Surface((self.resolution[1] / 2, self.resolution[1] / 2))
            self.ah_screen_rect = self.ah_screen.get_rect()
            self.ah_screen_rect.center = self.screen_rect.center
            self.artifical_horizon = ArtificalHorizon(self.ah_screen, size=self.resolution[1] / 2)

        self.little = kwargs.get("little", False)
        if self.little:
            self.airspeed_indicator = AirspeedIndicatorLittle(
                self.screen,
                size=self.size / 2,
                position=(self.screen_rect.center[0] - self.unit * 5, self.screen_rect.center[1]),
            )
            self.altitude_indicator = AltitudeIndicatorLittle(
                self.screen,
                size=self.size / 2,
                position=(self.screen_rect.center[0] + self.unit * 5, self.screen_rect.center[1]),
            )
            self.vspeed_indicator = VerticalSpeedIndicatoLittle(
                self.screen,
                size=self.size / 2.5,
                position=(self.altitude_indicator.background_rect.right + self.size / 100, self.screen_rect.center[1]),
            )

    def draw_fps(self) -> pygame.Rect:
        font = pygame.font.SysFont(None, 24)
        fps_txt = font.render(f"FPS: {self.fps:.0f}", True, self.text_color)
        fps_txt_rect = fps_txt.get_rect()
        fps_txt_rect.topleft = (12, 12)
        fps_txt_rect.w = 80
        self.screen.blit(fps_txt, fps_txt_rect)
        return fps_txt_rect

    def draw_real_time(self) -> pygame.Rect:
        font = pygame.font.SysFont(None, 24)
        time_txt = font.render(
            "real_time: " + str(timedelta(seconds=self.real_time))[:-4], True, self.text_color
        )
        time_txt_rect = time_txt.get_rect()
        time_txt_rect.topleft = (12, 36)
        time_txt_rect.w = 200
        self.screen.blit(time_txt, time_txt_rect)
        return time_txt_rect

    def draw_sim_time(self) -> pygame.Rect:
        font = pygame.font.SysFont(None, 24)
        time_txt = font.render("sim_time: " + str(timedelta(seconds=self.sim_time))[:-4], True, self.text_color)
        time_txt_rect = time_txt.get_rect()
        time_txt_rect.topleft = (12, 60)
        time_txt_rect.w = 200
        self.screen.blit(time_txt, time_txt_rect)
        return time_txt_rect

    def update(self, state: AircraftState, real_time: float = None, sim_time: float = None) -> None:
        self.state = state
        self.artifical_horizon.update(state.roll, state.pitch)
        self.airspeed_indicator.update(state.airspeed, state.airspeed_cmd)
        self.altitude_indicator.update(state.altitude, state.altitude_cmd)
        self.vspeed_indicator.update(state.vspeed)
        self.heading_indicator.update(state.heading, state.course, state.heading_cmd)
        self.real_time = real_time
        self.sim_time = sim_time

    def get_render_rects(self) -> list:
        render_rects = []
        render_rects.append(self.artifical_horizon.draw())
        render_rects.append(self.airspeed_indicator.draw())
        render_rects.append(self.altitude_indicator.draw())
        render_rects.append(self.vspeed_indicator.draw())
        render_rects.append(self.heading_indicator.draw())
        render_rects.append(self.draw_fps())
        self.real_time = 0.0
        render_rects.append(self.draw_real_time())
        self.sim_time = 0.0
        render_rects.append(self.draw_sim_time())
        return render_rects

    def draw_render_rects(self) -> None:
        for rect in self.render_rects:
            pygame.draw.rect(self.screen, (255, 0, 0), rect, width=1)

    def draw_aux_lines(self) -> None:
        N = 16
        for k in range(N + 1):
            posx = 0 + k * self.screen_rect.w / N
            p1 = (posx, 0)
            p2 = (posx, self.screen_rect.h)
            pygame.draw.line(self.screen, (255, 255, 0), p1, p2, width=1)
        for k in range(N + 1):
            posy = 0 + k * self.screen_rect.h / N
            p1 = (0, posy)
            p2 = (self.screen_rect.w, posy)
            pygame.draw.line(self.screen, (255, 255, 0), p1, p2, width=1)

    def draw(self, debug: bool = False) -> None:
        self.screen.fill((0, 0, 0))
        self.artifical_horizon.draw()
        self.airspeed_indicator.draw()
        self.vspeed_indicator.draw()
        self.altitude_indicator.draw()
        self.heading_indicator.draw()
        if debug:
            self.artifical_horizon.draw_aux_axis()
        if self.masked:
            self.screen.blit(self.ah_screen, self.ah_screen_rect)
        self.draw_fps()
        if not self.real_time is None:
            self.draw_real_time()
        if not self.sim_time is None:
            self.draw_sim_time()

    def render(self):
        ### pygame event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # exit pg screen
                sys.exit()  # exit python script
        ### pygame screen update (rendering)
        pygame.display.update(self.render_rects)
        if self.max_fps is None:
            self.game_clock.tick()
        else:
            self.game_clock.tick(self.max_fps)
        self.fps = self.game_clock.get_fps()
