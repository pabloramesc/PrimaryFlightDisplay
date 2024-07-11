"""
 Copyright (c) 2022 Pablo Ramirez Escudero
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
"""

import numpy as np
import pygame

from .common import clip_angle_180, clip_angle_360, diff_angle_180


class HeadingIndicator:
    def __init__(self, screen: pygame.Surface, *args, **kwargs) -> None:
        self.screen = screen
        self.screen_rect = screen.get_rect()

        self.size = kwargs.get("size", 400)
        self.height = self.size / 6
        self.width = self.size
        self.position = kwargs.get("position", (0, 0))

        self.vmid = self.height / 2
        self.hmid = self.width / 2

        self.background = pygame.Surface((self.width, self.height))
        self.background = self.background.convert_alpha()
        self.background_rect = self.background.get_rect()
        self.background_rect.midtop = self.position
        self.background_color = pygame.Color(100, 100, 100, 200)

        self.indicator_range = 25
        self.indicator_range2 = 50
        self.indicator_marks_num = self.indicator_range2 // 5 + 1
        self.angle2width = self.width / self.indicator_range2
        self.lines_length = self.height / 5
        self.lines_length2 = self.lines_length * 2

        self.line_width1 = int(1 + self.size // 800)
        self.line_width2 = int(1 + self.size // 400)
        self.line_width3 = int(1 + self.size // 200)

        self.marks_font = pygame.font.SysFont("helvetica", int(self.size // 16.5))
        self.command_font = pygame.font.SysFont("helvetica", int(self.size // 10.5))
        self.command_separation = int(self.size // 50.0)

        ### pre-compute all constant shapes
        self.build_constant_elements()

        ### initialize
        self.update(0.0, 0.0)

    def build_constant_elements(self) -> None:
        ### heading numbers text
        font = self.marks_font
        self.heading_values_txt = {}
        for heading_value in np.arange(10, 360 + 10, 10):
            if heading_value == 360.0:
                heading_txt = font.render("N", True, (255, 255, 255))
            elif heading_value == 90.0:
                heading_txt = font.render("E", True, (255, 255, 255))
            elif heading_value == 180.0:
                heading_txt = font.render("S", True, (255, 255, 255))
            elif heading_value == 270.0:
                heading_txt = font.render("W", True, (255, 255, 255))
            else:
                heading_txt = font.render(f"{heading_value:.0f}", True, (255, 255, 255))
            heading_txt_rect = heading_txt.get_rect()
            self.heading_values_txt[heading_value] = (heading_txt, heading_txt_rect)

        ### course mark
        self.course_mark_color = pygame.Color("#23FF00")
        self.course_mark_original = [
            (self.hmid - self.height / 6, self.height / 3),
            (self.hmid, 0.0),
            (self.hmid + self.height / 6, self.height / 3),
        ]

        ### command mark
        self.command_mark_color = pygame.Color("#F000FF")
        self.command_mark_original = [
            (self.background_rect.centerx - self.height / 3, self.background_rect.top),
            (self.background_rect.centerx - self.height / 3, self.background_rect.top - self.height / 4),
            (self.background_rect.centerx - self.height / 6, self.background_rect.top - self.height / 4),
            (self.background_rect.centerx, self.background_rect.top),
            (self.background_rect.centerx + self.height / 6, self.background_rect.top - self.height / 4),
            (self.background_rect.centerx + self.height / 3, self.background_rect.top - self.height / 4),
            (self.background_rect.centerx + self.height / 3, self.background_rect.top),
        ]

        ### central mark
        self.central_mark = [
            (self.background_rect.centerx - self.height / 6, self.background_rect.top - self.height / 3),
            (self.background_rect.centerx, self.background_rect.top),
            (self.background_rect.centerx + self.height / 6, self.background_rect.top - self.height / 3),
        ]

        ### border lines
        self.border_line_h = (self.background_rect.topright, self.background_rect.topleft)
        self.border_line_v1 = (self.background_rect.topright, self.background_rect.bottomright)
        self.border_line_v2 = (self.background_rect.topleft, self.background_rect.bottomleft)

        ### render rectangle
        x = self.background_rect.x - 38 * 2 - 5
        y = self.background_rect.y - self.height / 3 - 5
        w = self.width + 38 * 2 + 10
        h = self.height + self.height / 3 + 10
        self.render_rect = pygame.Rect(x, y, w, h)

    def draw_lines(self) -> None:
        max_heading_mark = self.bar_max_heading // 5 * 5
        for kk in range(self.indicator_marks_num):
            mark = diff_angle_180(max_heading_mark, 5.0 * kk)
            ang_diff = diff_angle_180(self.heading, mark)
            incx = ang_diff * self.angle2width
            mark = clip_angle_360(mark)
            p1 = (self.hmid - incx, 0)
            if mark % 10 == 0:
                p2 = (self.hmid - incx, self.lines_length2)
                heading_txt, heading_txt_rect = self.heading_values_txt[mark]
                heading_txt_rect.midtop = p2
                self.background.blit(heading_txt, heading_txt_rect)
            else:
                p2 = (self.hmid - incx, self.lines_length)

            pygame.draw.line(self.background, (255, 255, 255), p1, p2, width=self.line_width2)

    def draw_course_mark(self) -> None:
        ang_diff = diff_angle_180(self.heading, self.course)
        incx = ang_diff * self.angle2width
        course_mark = [(mark[0] - incx, mark[1]) for mark in self.course_mark_original]
        pygame.draw.polygon(self.background, self.course_mark_color, course_mark, width=self.line_width3)

    def draw_command_mark(self) -> None:
        ang_diff = diff_angle_180(self.heading, self.command)
        if abs(ang_diff) < self.indicator_range:
            incx = ang_diff * self.angle2width
            command_mark = [(mark[0] - incx, mark[1]) for mark in self.command_mark_original]
            pygame.draw.polygon(self.screen, self.command_mark_color, command_mark, width=self.line_width3)

        command_value = self.command_font.render(f"{clip_angle_360(self.command):.0f}", True, self.command_mark_color)
        command_value_rect = command_value.get_rect()
        command_value_rect.midright = self.background_rect.midleft
        command_value_rect.move_ip(-self.command_separation, 0)
        self.screen.blit(command_value, command_value_rect)

    def draw_central_mark(self) -> None:
        pygame.draw.polygon(self.screen, (255, 255, 255), self.central_mark, width=self.line_width3)

    def draw_border_lines(self) -> None:
        pygame.draw.line(
            self.screen, (255, 255, 255), self.border_line_h[0], self.border_line_h[1], width=self.line_width3
        )
        pygame.draw.line(
            self.screen, (255, 255, 255), self.border_line_v1[0], self.border_line_v1[1], width=self.line_width3
        )
        pygame.draw.line(
            self.screen, (255, 255, 255), self.border_line_v2[0], self.border_line_v2[1], width=self.line_width3
        )

    def update(self, heading: float, course: float, command: float = None) -> None:
        self.heading = clip_angle_180(heading)
        self.course = clip_angle_180(course)

        if command is None:
            self.command = None
        else:
            self.command = clip_angle_180(command)

        # self.bar_min_heading = clip_angle_180(self.heading - self.indicator_range)
        self.bar_max_heading = clip_angle_180(self.heading + self.indicator_range)

    def draw(self) -> pygame.Rect:
        self.background.fill(self.background_color)
        self.draw_lines()
        self.draw_course_mark()
        self.screen.blit(self.background, self.background_rect)
        self.draw_border_lines()
        self.draw_central_mark()
        if not self.command is None:
            self.draw_command_mark()
        return self.render_rect
