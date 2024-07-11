"""
 Copyright (c) 2022 Pablo Ramirez Escudero
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

import numpy as np
import pygame

from .common import get_digit, quit_out_range


class AltitudeIndicator:
    def __init__(self, screen: pygame.Surface, *args, **kwargs) -> None:
        self.screen = screen
        self.screen_rect = screen.get_rect()

        self.size = kwargs.get("size", 400)
        self.height = self.size
        self.width = self.size / 5
        self.position = kwargs.get("position", (0, 0))

        self.vmid = self.height / 2
        self.hmid = self.width / 2

        self.background = pygame.Surface((self.width, self.height))
        self.background = self.background.convert_alpha()
        self.background_rect = self.background.get_rect()
        self.background_rect.midleft = self.position
        self.background_color = pygame.Color(100, 100, 100, 200)

        self.indicator_range = 500
        self.indicator_range2 = 1000
        self.altitude2heigth = self.height / self.indicator_range2
        self.lines_length = self.width / 5
        self.lines_length2 = self.lines_length * 1.2

        self.line_width1 = int(1 + self.size // 800)
        self.line_width2 = int(1 + self.size // 400)
        self.line_width3 = int(1 + self.size // 200)
        self.line_width4 = int(1 + self.size // 100)

        self.marks_font_size = int(self.size // 15.5)
        self.marks_font_separation = int(self.size // 31.0) + 1
        self.command_font_size = int(self.size // 10.5)
        self.command_position = (
            self.background_rect.left + int(self.size // 100.0),
            self.background_rect.top - int(self.size // 9.0),
        )
        self.digit_font_size1 = int(self.size // 15.5)
        self.digit_font_size2 = int(self.size // 19.5)

        self.build_constant_elements()

        self.update(0.0)

    def build_constant_elements(self) -> None:
        ### digits display
        self.box_size = self.width * (3 / 5)
        self.box_poly = [
            (self.background_rect.right + self.box_size / 3, self.background_rect.centery - self.box_size / 2),
            (self.background_rect.right - self.box_size, self.background_rect.centery - self.box_size / 2),
            (self.background_rect.right - self.box_size, self.background_rect.centery - self.box_size / 4),
            (self.background_rect.left + self.lines_length, self.background_rect.centery),
            (self.background_rect.right - self.box_size, self.background_rect.centery + self.box_size / 4),
            (self.background_rect.right - self.box_size, self.background_rect.centery + self.box_size / 2),
            (self.background_rect.right + self.box_size / 3, self.background_rect.centery + self.box_size / 2),
        ]
        self.box_surface = pygame.Surface((self.box_size * (4 / 3), self.box_size - 8))
        self.box_surface_rect = self.box_surface.get_rect()
        self.box_surface_rect.midright = (self.background_rect.right + self.box_size / 3, self.background_rect.centery)
        self.digits_display_rect = pygame.draw.polygon(
            self.screen, (255, 255, 255), self.box_poly, width=self.line_width3
        )

        ### digits position
        self.digit5_pos = (self.box_size * 0.25, self.box_size * 0.5 - 3)
        self.digit4_pos = (self.box_size * 0.5, self.box_size * 0.5 - 3)
        self.digit3_pos = (self.box_size * 0.725, self.box_size * 0.5 - 3)
        self.digit12_pos = (self.box_size * 1.0, self.box_size * 0.5 - 3)

        ### command mark
        self.command_mark_color = pygame.Color("#F000FF")
        self.command_mark_original = [
            (self.background_rect.left + self.box_size * 0.33, self.background_rect.centery - self.box_size / 2),
            (self.background_rect.left - self.box_size * 0.33, self.background_rect.centery - self.box_size / 2),
            (self.background_rect.left - self.box_size * 0.33, self.background_rect.centery - self.box_size / 4),
            (self.background_rect.left, self.background_rect.centery),
            (self.background_rect.left - self.box_size * 0.33, self.background_rect.centery + self.box_size / 4),
            (self.background_rect.left - self.box_size * 0.33, self.background_rect.centery + self.box_size / 2),
            (self.background_rect.left + self.box_size * 0.33, self.background_rect.centery + self.box_size / 2),
        ]

        ### border lines
        # self.border_line_v = (self.background_rect.topleft, self.background_rect.bottomleft)
        # self.border_line_h1 = (
        #     self.background_rect.topright,
        #     (self.background_rect.left - self.width / 3, self.background_rect.top),
        # )
        # self.border_line_h2 = (
        #     self.background_rect.bottomright,
        #     (self.background_rect.left - self.width / 3, self.background_rect.bottom),
        # )

        ### render rectangle
        x = self.background_rect.x - self.box_size * 0.33 - 5
        y = self.background_rect.y - 38 - 5
        w = self.width + self.box_size * 0.67 + 10
        h = self.height + 38 + 10
        self.render_rect = pygame.Rect(x, y, w, h)

    @staticmethod
    def draw_altitude_number(screen: pygame.Surface, altitude: float, size: int, **kwargs) -> pygame.Rect:
        color = kwargs.get("color", (255, 255, 255))
        position = kwargs.get("position", (0, 0))

        altitude = np.round(altitude, -2)
        thousands_value = altitude // 1000
        houndreds_value = altitude - thousands_value * 1000

        font = pygame.font.SysFont("helvetica", size)
        thousands = font.render(f"{thousands_value:.0f}", True, color)
        thousands_rect = thousands.get_rect()

        font = pygame.font.SysFont("helvetica", int(size * 0.8))
        houndreds = font.render(f"{houndreds_value:03.0f}", True, color)
        houndreds_rect = houndreds.get_rect()

        thousands_rect.topleft = position
        houndreds_rect.bottom = thousands_rect.bottom - size // 16
        houndreds_rect.left = thousands_rect.right

        screen.blit(thousands, thousands_rect)
        screen.blit(houndreds, houndreds_rect)

        return pygame.Rect(thousands_rect.x, thousands_rect.y, thousands_rect.w + houndreds_rect.w, thousands_rect.h)

    def draw_lines(self) -> None:
        min_altitude_mark = np.round(self.bar_min_altitude, -2)
        max_altitude_mark = np.round(self.bar_max_altitude, -2)
        marks = np.arange(min_altitude_mark, max_altitude_mark + 100, 100.0)
        for mark in quit_out_range(marks, self.bar_min_altitude, self.bar_max_altitude):
            incy = (self.altitude - mark) * self.altitude2heigth
            p1 = (0, self.vmid + incy)
            mark_color = (255, 255, 255)
            if mark <= 0:
                mark = abs(mark)
                mark_color = (255, 0, 0)
            if mark % 1000 == 0:
                p2 = (self.lines_length2, self.vmid + incy)
                pygame.draw.line(self.background, mark_color, p1, p2, width=self.line_width4)
            else:
                p2 = (self.lines_length2, self.vmid + incy)
                pygame.draw.line(self.background, mark_color, p1, p2, width=self.line_width2)
            if mark % 200 == 0:
                num_pos = (self.lines_length * 1.5, self.vmid + incy - self.marks_font_separation)
                self.draw_altitude_number(
                    self.background, mark, self.marks_font_size, color=mark_color, position=num_pos
                )

    def draw_digits_display(self) -> None:
        pygame.draw.polygon(self.screen, (0, 0, 0), self.box_poly)

        altitude_abs = self.altitude
        digits_color = (255, 255, 255)
        if self.altitude <= 0.0:
            altitude_abs = abs(self.altitude)
            digits_color = (255, 0, 0)

        digit2_value = get_digit(altitude_abs, 1)
        digit3_value = get_digit(altitude_abs, 2)
        digit4_value = get_digit(altitude_abs, 3)
        digit5_value = get_digit(altitude_abs, 4)

        self.box_surface.fill((0, 0, 0))

        font = pygame.font.SysFont("helvetica", self.digit_font_size1)

        digit5 = font.render(f"{digit5_value:.0f}", True, digits_color)
        digit5_rect = digit5.get_rect()
        digit5_rect.center = self.digit5_pos
        self.box_surface.blit(digit5, digit5_rect)

        digit4 = font.render(f"{digit4_value:.0f}", True, digits_color)
        digit4_rect = digit4.get_rect()
        digit4_rect.center = self.digit4_pos
        self.box_surface.blit(digit4, digit4_rect)

        font = pygame.font.SysFont("helvetica", self.digit_font_size2)

        digit3 = font.render(f"{digit3_value:.0f}", True, digits_color)
        digit3_rect = digit3.get_rect()
        digit3_rect.center = self.digit3_pos
        self.box_surface.blit(digit3, digit3_rect)

        digit12_value = digit2_value // 2 * 20
        fract_part = np.modf(altitude_abs * 0.05)[0]
        for num in np.arange(digit12_value - 40, digit12_value + 60, 20):
            incy = (fract_part + (digit12_value - num) * 0.05) * 0.36
            if num < 0:
                num += 100
            if num > 90:
                num -= 100
            digits = font.render(f"{num:02.0f}", True, digits_color)
            digits_rect = digits.get_rect()
            digits_rect.center = (self.digit12_pos[0], self.box_size * (0.5 + incy) - 3)
            self.box_surface.blit(digits, digits_rect)

        self.screen.blit(self.box_surface, self.box_surface_rect)

        pygame.draw.polygon(self.screen, (255, 255, 255), self.box_poly, width=self.line_width3)

    def draw_command_mark(self) -> None:
        if self.bar_min_altitude < self.command < self.bar_max_altitude:
            incy = (self.altitude - self.command) * self.altitude2heigth
            command_mark = [
                (self.command_mark_original[0][0], self.command_mark_original[0][1] + incy),
                (self.command_mark_original[1][0], self.command_mark_original[1][1] + incy),
                (self.command_mark_original[2][0], self.command_mark_original[2][1] + incy),
                (self.command_mark_original[3][0], self.command_mark_original[3][1] + incy),
                (self.command_mark_original[4][0], self.command_mark_original[4][1] + incy),
                (self.command_mark_original[5][0], self.command_mark_original[5][1] + incy),
                (self.command_mark_original[6][0], self.command_mark_original[6][1] + incy),
            ]
            pygame.draw.polygon(self.screen, self.command_mark_color, command_mark, width=self.line_width3)

        AltitudeIndicator.draw_altitude_number(
            self.screen,
            self.command,
            size=self.command_font_size,
            position=self.command_position,
            color=self.command_mark_color,
        )

    def draw_border_lines(self):
        # pygame.draw.line(self.screen, (255, 255, 255), self.border_line_v[0], self.border_line_v[1], width=self.line_width3)
        # pygame.draw.line(self.screen, (255, 255, 255), self.border_line_h1[0], self.border_line_h1[1], width=self.line_width3)
        # pygame.draw.line(self.screen, (255, 255, 255), self.border_line_h2[0], self.border_line_h2[1], width=self.line_width3)
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            self.background_rect.topleft,
            self.background_rect.bottomleft,
            width=self.line_width3,
        )
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            self.background_rect.topleft,
            self.background_rect.topright,
            width=self.line_width3,
        )
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            self.background_rect.bottomleft,
            self.background_rect.bottomright,
            width=self.line_width3,
        )

    def update(self, altitude: float, command: float = None):
        # self.altitude = np.clip(altitude, 0.0, None)
        self.altitude = altitude

        if command is None:
            self.command = None
        else:
            # self.command = np.clip(command, 0.0, None)
            self.command = command

        self.bar_min_altitude = self.altitude - self.indicator_range
        self.bar_max_altitude = self.altitude + self.indicator_range

    def draw(self):
        self.background.fill(self.background_color)
        self.draw_lines()
        self.screen.blit(self.background, self.background_rect)
        self.draw_border_lines()
        self.draw_digits_display()
        if not self.command is None:
            self.draw_command_mark()
        return self.render_rect
