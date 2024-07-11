import numpy as np
import pygame

from .common import quit_out_range


class ArtificalHorizon:
    def __init__(self, screen: pygame.Surface, **kwargs) -> None:
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.screen_radius = np.sqrt(self.screen_rect.size[0] ** 2 + self.screen_rect.size[1] ** 2)

        self.size = kwargs.get("size", 400)
        self.angle_range = kwargs.get("angle_range", 45.0)
        self.render_angle = self.angle_range / 3
        self.angle2height = self.size / self.angle_range

        self.frame = pygame.Surface((self.size, self.size))
        self.frame_rect = self.frame.get_rect()
        self.frame_rect.center = self.screen_rect.center

        self.lines_color = pygame.Color("#FFFFFF")
        self.sky_color = pygame.Color("#008FFF")
        self.gnd_color = pygame.Color("#934100")

        self.lines_size = self.size / 2
        self.lines_10deg = np.delete(np.arange(-80.0, 80.0 + 10.0, 10.0), 8)
        self.lines_05deg = np.arange(-85.0, 85.0 + 10.0, 10.0)
        self.lines_025deg = np.arange(-87.5, 87.5 + 5.0, 5.0)
        self.marks_90deg = np.array([-90.0, +90.0])

        self.roll_arc_radius = self.size / 2.2
        self.small_bank_marks = [-45, -20, -10, 10, 20, 45]
        self.big_bank_marks = [-60, -30, 30, 60]

        self.line_width1 = int(1 + self.size // 800)
        self.line_width2 = int(1 + self.size // 400)
        self.line_width3 = int(1 + self.size // 200)
        self.line_width4 = int(1 + self.size // 100)

        self.marks_font = pygame.font.SysFont("helvetica", int(self.size // 16.5))

        ### pre-compute all constant shapes
        self.build_constant_elements()

        ### initialize
        self.update(0.0, 0.0)

    def build_constant_elements(self) -> None:
        ### render pitch values text and store them
        self.pitch_values_txt = {}
        for ang in np.arange(10, 80 + 10, 10):
            self.pitch_values_txt[ang] = self.marks_font.render(f"{ang:.0f}", True, (255, 255, 255))

        ### horizontal reference marks
        ref_size = self.size / 100
        self.reference_central_poly = [
            (self.frame_rect.centerx - ref_size, self.frame_rect.centery - ref_size),
            (self.frame_rect.centerx + ref_size, self.frame_rect.centery - ref_size),
            (self.frame_rect.centerx + ref_size, self.frame_rect.centery + ref_size),
            (self.frame_rect.centerx - ref_size, self.frame_rect.centery + ref_size),
        ]
        self.reference_rigth_poly = [
            (self.frame_rect.left + 5 * ref_size, self.frame_rect.centery - ref_size),
            (self.frame_rect.centerx - 20 * ref_size, self.frame_rect.centery - ref_size),
            (self.frame_rect.centerx - 20 * ref_size, self.frame_rect.centery + 4 * ref_size),
            (self.frame_rect.centerx - 22 * ref_size, self.frame_rect.centery + 4 * ref_size),
            (self.frame_rect.centerx - 22 * ref_size, self.frame_rect.centery + ref_size),
            (self.frame_rect.left + 5 * ref_size, self.frame_rect.centery + ref_size),
        ]
        self.reference_left_poly = [
            (self.frame_rect.right - 5 * ref_size, self.frame_rect.centery - ref_size),
            (self.frame_rect.centerx + 20 * ref_size, self.frame_rect.centery - ref_size),
            (self.frame_rect.centerx + 20 * ref_size, self.frame_rect.centery + 4 * ref_size),
            (self.frame_rect.centerx + 22 * ref_size, self.frame_rect.centery + 4 * ref_size),
            (self.frame_rect.centerx + 22 * ref_size, self.frame_rect.centery + ref_size),
            (self.frame_rect.right - 5 * ref_size, self.frame_rect.centery + ref_size),
        ]

        ### roll indicator marks
        self.roll_arc_rect = pygame.draw.circle(
            self.screen, (255, 255, 255, 0), self.screen_rect.center, self.roll_arc_radius
        )
        self.roll_pointer_height = self.frame_rect.w / 2 - self.roll_arc_radius
        self.roll_pointer_width = 0.75 * self.roll_pointer_height
        self.roll_pointer_poly = [
            (self.frame_rect.centerx - self.roll_pointer_width, self.frame_rect.top),
            (self.frame_rect.centerx, self.frame_rect.top + self.roll_pointer_height),
            (self.frame_rect.centerx + self.roll_pointer_width, self.frame_rect.top),
        ]
        self.roll_small_marks_lines = []
        for ang in self.small_bank_marks:
            sin = np.sin(np.deg2rad(ang))
            cos = np.cos(np.deg2rad(ang))
            p1 = (
                self.frame_rect.center[0] - self.roll_arc_radius * sin,
                self.frame_rect.center[1] - self.roll_arc_radius * cos,
            )
            p2 = (
                self.frame_rect.center[0] - (self.roll_arc_radius + self.roll_pointer_height) * sin,
                self.frame_rect.center[1] - (self.roll_arc_radius + self.roll_pointer_height) * cos,
            )
            self.roll_small_marks_lines.append((p1, p2))
        self.roll_big_marks_lines = []
        for ang in self.big_bank_marks:
            sin = np.sin(np.deg2rad(ang))
            cos = np.cos(np.deg2rad(ang))
            p1 = (
                self.frame_rect.center[0] - self.roll_arc_radius * sin,
                self.frame_rect.center[1] - self.roll_arc_radius * cos,
            )
            p2 = (
                self.frame_rect.center[0] - (self.roll_arc_radius + 2 * self.roll_pointer_height) * sin,
                self.frame_rect.center[1] - (self.roll_arc_radius + 2 * self.roll_pointer_height) * cos,
            )
            self.roll_big_marks_lines.append((p1, p2))

    def draw_aux_axis(self) -> None:
        fixed_lines_color = pygame.Color(255, 0, 0)
        frame_points = [
            (self.frame_rect.topleft),
            (self.frame_rect.topright),
            (self.frame_rect.bottomright),
            (self.frame_rect.bottomleft),
        ]
        pygame.draw.polygon(self.screen, fixed_lines_color, frame_points, width=self.line_width1)
        pygame.draw.line(
            self.screen, fixed_lines_color, self.frame_rect.midleft, self.frame_rect.midright, width=self.line_width2
        )
        pygame.draw.line(
            self.screen, fixed_lines_color, self.frame_rect.midtop, self.frame_rect.midbottom, width=self.line_width1
        )
        render_radius = self.render_angle * self.angle2height
        pygame.draw.circle(
            self.screen, fixed_lines_color, self.frame_rect.center, render_radius, width=self.line_width1
        )
        pygame.draw.circle(
            self.screen, fixed_lines_color, self.frame_rect.center, self.roll_arc_radius, width=self.line_width1
        )

        moving_lines_color = pygame.Color(0, 255, 0)

        p1v = (self.frame_rect.center[0] - self.rsin_roll, self.frame_rect.center[1] - self.rcos_roll)
        p2v = (self.frame_rect.center[0] + self.rsin_roll, self.frame_rect.center[1] + self.rcos_roll)
        pygame.draw.line(self.screen, moving_lines_color, p1v, p2v)

        p1h = (self.pitch_center[0] - self.rcos_roll, self.pitch_center[1] + self.rsin_roll)
        p2h = (self.pitch_center[0] + self.rcos_roll, self.pitch_center[1] - self.rsin_roll)
        pygame.draw.line(self.screen, moving_lines_color, p1h, p2h, width=self.line_width2)

        for ang in np.arange(10.0, 100.0, 10.0):
            dist = self.angle2height * ang
            dsin = dist * self.sin_roll
            dcos = dist * self.cos_roll
            p1v = (self.pitch_center[0] - dsin, self.pitch_center[1] - dcos)
            p2v = (self.pitch_center[0] + dsin, self.pitch_center[1] + dcos)
            pygame.draw.circle(self.screen, (255, 0, 0), p1v, 5)
            pygame.draw.circle(self.screen, (0, 0, 255), p2v, 5)

    def draw_background(self) -> None:
        p1a = (self.pitch_center[0] - self.rcos_roll, self.pitch_center[1] + self.rsin_roll)
        p1b = (self.pitch_center[0] + self.rcos_roll, self.pitch_center[1] - self.rsin_roll)

        outter_line_center = (
            self.screen_rect.center[0] + self.screen_radius * self.sin_roll,
            self.screen_rect.center[1] + self.screen_radius * self.cos_roll,
        )
        p2a = (outter_line_center[0] - self.rcos_roll, outter_line_center[1] + self.rsin_roll)
        p2b = (outter_line_center[0] + self.rcos_roll, outter_line_center[1] - self.rsin_roll)

        self.screen.fill(self.sky_color)
        pygame.draw.polygon(self.screen, self.gnd_color, [p1a, p2a, p2b, p1b])
        pygame.draw.line(self.screen, (255, 255, 255), p1a, p1b, width=self.line_width2)

    def draw_white_lines(self) -> None:
        max_ang = self.pitch + self.render_angle
        min_ang = self.pitch - self.render_angle

        ### PLOT MAIN LINES (10 DEG) AND PITCH VALUES ###
        line_radius = self.lines_size * 0.5
        lsin = line_radius * self.sin_roll
        lcos = line_radius * self.cos_roll
        tsin = line_radius * self.sin_roll * 1.2
        tcos = line_radius * self.cos_roll * 1.2
        for ang in quit_out_range(self.lines_10deg, min_ang, max_ang):
            dist = self.angle2height * ang
            dsin = dist * self.sin_roll
            dcos = dist * self.cos_roll
            line_center = (self.pitch_center[0] - dsin, self.pitch_center[1] - dcos)
            line_p1 = (line_center[0] - lcos, line_center[1] + lsin)
            line_p2 = (line_center[0] + lcos, line_center[1] - lsin)
            pygame.draw.line(self.screen, (255, 255, 255), line_p1, line_p2, width=self.line_width2)
            ang_num = self.pitch_values_txt[abs(ang)]
            ang_num = pygame.transform.rotate(ang_num, self.roll)
            # ang_num = pygame.transform.rotozoom(ang_num, self.roll, 1)
            ang_num_rect = ang_num.get_rect()
            line_p1 = (line_center[0] - tcos, line_center[1] + tsin)
            line_p2 = (line_center[0] + tcos, line_center[1] - tsin)
            ang_num_rect.center = line_p1
            self.screen.blit(ang_num, ang_num_rect)
            ang_num_rect.center = line_p2
            self.screen.blit(ang_num, ang_num_rect)

        ### PLOT SECOND LINES (5 DEG) ###
        line_radius = self.lines_size * 0.25
        lsin = line_radius * self.sin_roll
        lcos = line_radius * self.cos_roll
        for ang in quit_out_range(self.lines_05deg, min_ang, max_ang):
            dist = self.angle2height * ang
            dsin = dist * self.sin_roll
            dcos = dist * self.cos_roll
            line_center = (self.pitch_center[0] - dsin, self.pitch_center[1] - dcos)
            line_p1 = (line_center[0] - lcos, line_center[1] + lsin)
            line_p2 = (line_center[0] + lcos, line_center[1] - lsin)
            pygame.draw.line(self.screen, (255, 255, 255), line_p1, line_p2, width=self.line_width2)

        ### PLOT THIRD LINES (2.5 DEG) ###
        line_radius = self.lines_size * 0.125
        lsin = line_radius * self.sin_roll
        lcos = line_radius * self.cos_roll
        for ang in quit_out_range(self.lines_025deg, min_ang, max_ang):
            dist = self.angle2height * ang
            dsin = dist * self.sin_roll
            dcos = dist * self.cos_roll
            line_center = (self.pitch_center[0] - dsin, self.pitch_center[1] - dcos)
            line_p1 = (line_center[0] - lcos, line_center[1] + lsin)
            line_p2 = (line_center[0] + lcos, line_center[1] - lsin)
            pygame.draw.line(self.screen, (255, 255, 255), line_p1, line_p2, width=self.line_width2)

        ### PLOT 90 DEG MARKS ###
        mark_radius = self.lines_size * 0.02
        for ang in quit_out_range(self.marks_90deg, min_ang, max_ang):
            dist = self.angle2height * ang
            dsin = dist * self.sin_roll
            dcos = dist * self.cos_roll
            line_center = (self.pitch_center[0] - dsin, self.pitch_center[1] - dcos)
            pygame.draw.circle(self.screen, (255, 255, 255), line_center, mark_radius)

    def draw_roll_marks(self) -> None:
        pygame.draw.polygon(self.screen, (255, 255, 255), self.roll_pointer_poly)

        for line in self.roll_small_marks_lines:
            pygame.draw.line(self.screen, (255, 255, 255), line[0], line[1], width=self.line_width3)

        for line in self.roll_big_marks_lines:
            pygame.draw.line(self.screen, (255, 255, 255), line[0], line[1], width=self.line_width3)

        pygame.draw.arc(
            self.screen, (255, 255, 255), self.roll_arc_rect, np.deg2rad(30), np.deg2rad(150), width=self.line_width3
        )

        h1sin = self.roll_arc_radius * self.sin_roll
        h1cos = self.roll_arc_radius * self.cos_roll
        h2sin = (self.roll_arc_radius - self.roll_pointer_height) * self.sin_roll
        h2cos = (self.roll_arc_radius - self.roll_pointer_height) * self.cos_roll
        wsin = self.roll_pointer_width * self.sin_roll
        wcos = self.roll_pointer_width * self.cos_roll
        p1 = (self.frame_rect.center[0] - h1sin, self.frame_rect.center[1] - h1cos)
        p2 = (self.frame_rect.center[0] - h2sin, self.frame_rect.center[1] - h2cos)
        p2a = (p2[0] - wcos, p2[1] + wsin)
        p2b = (p2[0] + wcos, p2[1] - wsin)
        pygame.draw.polygon(self.screen, (255, 255, 255), [p1, p2a, p2b])

    def draw_reference_marks(self) -> None:
        pygame.draw.polygon(self.screen, (0, 0, 0), self.reference_central_poly)
        pygame.draw.polygon(self.screen, (255, 255, 255), self.reference_central_poly, width=self.line_width2)
        pygame.draw.polygon(self.screen, (0, 0, 0), self.reference_rigth_poly)
        pygame.draw.polygon(self.screen, (255, 255, 255), self.reference_rigth_poly, width=self.line_width2)
        pygame.draw.polygon(self.screen, (0, 0, 0), self.reference_left_poly)
        pygame.draw.polygon(self.screen, (255, 255, 255), self.reference_left_poly, width=self.line_width2)

    def update(self, roll: float, pitch: float) -> None:
        self.roll = np.clip(roll, -180.0, +180.0)
        self.pitch = np.clip(pitch, -90.0, +90.0)
        self.sin_roll = np.sin(np.deg2rad(self.roll))
        self.cos_roll = np.cos(np.deg2rad(self.roll))
        self.rsin_roll = self.screen_radius * self.sin_roll
        self.rcos_roll = self.screen_radius * self.cos_roll
        self.incy = self.angle2height * self.pitch
        self.pitch_center = (
            self.screen_rect.center[0] + self.incy * self.sin_roll,
            self.screen_rect.center[1] + self.incy * self.cos_roll,
        )

    def draw(self) -> pygame.Rect:
        self.draw_background()
        self.draw_white_lines()
        self.draw_roll_marks()
        self.draw_reference_marks()
        return self.frame_rect
