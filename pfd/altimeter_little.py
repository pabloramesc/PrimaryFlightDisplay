"""
 Copyright (c) 2022 Pablo Ramirez Escudero
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

import numpy as np
import pygame

from .common import get_digit, quit_out_range


class AltitudeIndicatorLittle:
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

        self.indicator_range = 15
        self.indicator_range2 = self.indicator_range * 2
        self.altitude2heigth = self.height / self.indicator_range2
        self.lines_length = self.width / 5
        self.lines_length2 = self.lines_length * 1.5

        self.line_width1 = int(1 + self.size // 800)
        self.line_width2 = int(1 + self.size // 400)
        self.line_width3 = int(1 + self.size // 200)
        self.line_width4 = int(1 + self.size // 100)

        self.marks_font = pygame.font.SysFont("helvetica", int(self.size // 16.5))
        self.digits_font = pygame.font.SysFont("helvetica", int(self.size // 15.0))
        self.command_font = pygame.font.SysFont("helvetica", int(self.size // 10.5))
        self.command_separation = int(self.size // 100.0)

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
        self.digit4_pos = (self.box_size * 0.25, self.box_size * 0.5 - 3)
        self.digit3_pos = (self.box_size * 0.50, self.box_size * 0.5 - 3)
        self.digit2_pos = (self.box_size * 0.75, self.box_size * 0.5 - 3)
        self.digit1_pos = (self.box_size * 1.00, self.box_size * 0.5 - 3)

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

    def draw_lines(self) -> None:
        min_altitude_mark = self.bar_min_altitude//2.5*2.5
        max_altitude_mark = self.bar_max_altitude//2.5*2.5
        marks = np.arange(min_altitude_mark, max_altitude_mark + 2.5, 2.5)
        for mark in quit_out_range(marks, self.bar_min_altitude, self.bar_max_altitude):
            incy = (self.altitude - mark) * self.altitude2heigth
            p1 = (0, self.vmid + incy)
            mark_color = (255, 255, 255)
            if mark <= 0:
                mark = abs(mark)
                mark_color = (255, 0, 0)
            if mark % 50 == 0:
                p2 = (self.lines_length2, self.vmid + incy)
                pygame.draw.line(self.background, mark_color, p1, p2, width=self.line_width4)
            elif mark % 5 == 0:
                p2 = (self.lines_length2, self.vmid + incy)
                pygame.draw.line(self.background, mark_color, p1, p2, width=self.line_width2)
                altitude_num = self.marks_font.render(f"{mark:.0f}", True, mark_color)
                altitude_num_rect = altitude_num.get_rect()
                altitude_num_rect.midleft = (self.lines_length2 * 1.2, self.vmid + incy)
                self.background.blit(altitude_num, altitude_num_rect)
            else:
                p2 = (self.lines_length, self.vmid + incy)
                pygame.draw.line(self.background, mark_color, p1, p2, width=self.line_width2)

    def draw_digits_display(self) -> None:
        pygame.draw.polygon(self.screen, (0, 0, 0), self.box_poly)

        altitude_abs = self.altitude
        digits_color = (255, 255, 255)
        if self.altitude <= 0.0:
            altitude_abs = abs(self.altitude)
            digits_color = (255, 0, 0)

        digit1_value = get_digit(altitude_abs, 0)
        digit2_value = get_digit(altitude_abs, 1)
        digit3_value = get_digit(altitude_abs, 2)
        digit4_value = get_digit(altitude_abs, 3)

        self.box_surface.fill((0, 0, 0))
        
        fract_part = np.modf(self.altitude)[0]

        if altitude_abs > 999.5:
            if digit3_value == 9 and digit2_value == 9 and digit1_value == 9 and fract_part > 0.5:
                digit4_value += 1
                digit4_value %= 10
            digit4 = self.digits_font.render(f"{digit4_value:.0f}", True, digits_color)
            digit4_rect = digit4.get_rect()
            digit4_rect.center = self.digit4_pos
            self.box_surface.blit(digit4, digit4_rect)

        if digit2_value == 9 and digit1_value == 9 and fract_part > 0.5:
            digit3_value += 1
            digit3_value %= 10
        digit3 = self.digits_font.render(f"{digit3_value:.0f}", True, digits_color)
        digit3_rect = digit3.get_rect()
        digit3_rect.center = self.digit3_pos
        self.box_surface.blit(digit3, digit3_rect)


        if digit1_value == 9 and fract_part > 0.5:
            digit2_value += 1
            digit2_value %= 10
        digit2 = self.digits_font.render(f"{digit2_value:.0f}", True, digits_color)
        digit2_rect = digit2.get_rect()
        digit2_rect.center = self.digit2_pos
        self.box_surface.blit(digit2, digit2_rect)

        rolling_nums = np.arange(digit1_value - 2, digit1_value + 3, 1)
        for num in rolling_nums:
            incy = (fract_part + digit1_value - num) * 0.5
            if self.altitude < 0:
                incy = (-fract_part + digit1_value - num) * 0.5
            num %= 10
            digit1 = self.digits_font.render(f"{num:.0f}", True, digits_color)
            digit1_rect = digit1.get_rect()
            digit1_rect.center = (self.digit1_pos[0], self.box_size * (0.5 + incy) - 3)
            self.box_surface.blit(digit1, digit1_rect)

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

        command_value = self.command_font.render(f"{self.command:.0f}", True, self.command_mark_color)
        command_value_rect = command_value.get_rect()
        command_value_rect.midbottom = self.background_rect.midtop
        command_value_rect.move_ip(0, -self.command_separation)
        self.screen.blit(command_value, command_value_rect)

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
