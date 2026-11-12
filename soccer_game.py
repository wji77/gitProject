"""
2022 카타르 월드컵 3 vs 3 미니 축구 게임
- 16강 진출 국가 및 AI 난이도(쉬움/보통/어려움) 선택
- 총 6명 경기: 아군 3명(플레이어 + AI 동료 2명) vs 상대팀 AI 3명
- 실제 사람 형태의 선수 그래픽 (헤어, 유니폼, 축구화, 러닝 애니메이션)
"""

import math
import random
import sys
import pygame
from teams import DIFFICULTIES, TEAMS_DATA, create_flag_surface

WIDTH, HEIGHT = 940, 640
FPS = 60

COLOR_PITCH_1 = (46, 139, 87)
COLOR_PITCH_2 = (52, 158, 98)
COLOR_LINE = (240, 240, 240)
COLOR_BALL = (255, 255, 255)
COLOR_BALL_PENTAGON = (30, 30, 30)
COLOR_TEXT = (255, 255, 255)
COLOR_YELLOW = (255, 215, 0)

PITCH_LEFT = 50
PITCH_RIGHT = WIDTH - 50
PITCH_TOP = 65
PITCH_BOTTOM = HEIGHT - 50
GOAL_TOP = 230
GOAL_BOTTOM = 410
GOAL_DEPTH = 35

MAX_GOALS = 5
MATCH_TIME = 90


class Particle:
    """골 축하 파티클 효과"""
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = random.randint(30, 55)
        self.radius = random.uniform(3, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.lifetime -= 1
        self.radius = max(0.0, self.radius - 0.07)

    def draw(self, surface):
        if self.lifetime > 0 and self.radius > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))


class Ball:
    def __init__(self, x, y):
        self.radius = 11
        self.reset(x, y)

    def reset(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.friction = 0.985
        self.rotation = 0.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.friction
        self.vy *= self.friction
        self.rotation += math.hypot(self.vx, self.vy) * 0.15

        if abs(self.vx) < 0.04:
            self.vx = 0.0
        if abs(self.vy) < 0.04:
            self.vy = 0.0

        if self.y - self.radius < PITCH_TOP:
            self.y = PITCH_TOP + self.radius
            self.vy = -self.vy * 0.8
        elif self.y + self.radius > PITCH_BOTTOM:
            self.y = PITCH_BOTTOM - self.radius
            self.vy = -self.vy * 0.8

        in_goal_y = GOAL_TOP <= self.y <= GOAL_BOTTOM
        if self.x - self.radius < PITCH_LEFT:
            if in_goal_y:
                if self.x - self.radius < PITCH_LEFT - GOAL_DEPTH:
                    self.x = PITCH_LEFT - GOAL_DEPTH + self.radius
                    self.vx = -self.vx * 0.5
            else:
                self.x = PITCH_LEFT + self.radius
                self.vx = -self.vx * 0.8

        if self.x + self.radius > PITCH_RIGHT:
            if in_goal_y:
                if self.x + self.radius > PITCH_RIGHT + GOAL_DEPTH:
                    self.x = PITCH_RIGHT + GOAL_DEPTH - self.radius
                    self.vx = -self.vx * 0.5
            else:
                self.x = PITCH_RIGHT - self.radius
                self.vx = -self.vx * 0.8

    def draw(self, surface):
        pos = (int(self.x), int(self.y))
        pygame.draw.ellipse(surface, (20, 20, 20), (int(self.x) - 10, int(self.y) + 3, 20, 8))
        pygame.draw.circle(surface, COLOR_BALL, pos, self.radius)
        pygame.draw.circle(surface, COLOR_BALL_PENTAGON, pos, 4)
        for i in range(5):
            angle = i * (2 * math.pi / 5) + self.rotation
            ox = int(self.x + math.cos(angle) * (self.radius - 3))
            oy = int(self.y + math.sin(angle) * (self.radius - 3))
            pygame.draw.circle(surface, COLOR_BALL_PENTAGON, (ox, oy), 2)
        pygame.draw.circle(surface, (120, 120, 120), pos, self.radius, 1)


class Player:
    def __init__(self, x, y, team: dict, role: str, is_user: bool, is_home: bool, difficulty: dict):
        self.start_x = x
        self.start_y = y
        self.radius = 19
        self.team = team
        self.role = role  # "GK", "MF", "FW"
        self.is_user = is_user
        self.is_home = is_home  # True: 왼쪽 진영(아군), False: 오른쪽 진영(상대)
        self.difficulty = difficulty

        # 역할 및 난이도별 속도
        base_speed = difficulty["ai_speed"] if not is_user else 4.7
        if role == "GK":
            self.speed = base_speed * 0.95
        elif role == "MF":
            self.speed = base_speed * 0.98
        else:
            self.speed = base_speed * 1.05

        self.shot_power = difficulty["ai_shot_power"] if not is_user else 15.0

        self.target_goal_x = PITCH_RIGHT if is_home else PITCH_LEFT
        self.home_goal_x = PITCH_LEFT if is_home else PITCH_RIGHT
        self.label = "YOU" if is_user else (f"아군-{role}" if is_home else f"AI-{role}")

        self.shoot_cooldown = 0
        self.facing_angle = 0.0 if is_home else math.pi
        self.run_cycle = 0.0
        self.is_moving = False
        self.kick_anim = 0

        self.mini_flag = create_flag_surface(team["code"], 18, 12)
        self.reset()

    def reset(self):
        self.x = float(self.start_x)
        self.y = float(self.start_y)
        self.vx = 0.0
        self.vy = 0.0
        self.facing_angle = 0.0 if self.is_home else math.pi
        self.kick_anim = 0

    def update_user(self, keys, ball):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        self.is_moving = (dx != 0 or dy != 0)
        if self.is_moving:
            if dx != 0 and dy != 0:
                dx *= 0.7071
                dy *= 0.7071
            self.facing_angle = math.atan2(dy, dx)
            self.run_cycle += 0.25

        self.vx = dx * self.speed
        self.vy = dy * self.speed
        self.x += self.vx
        self.y += self.vy
        self.clamp_position(PITCH_LEFT + self.radius, PITCH_RIGHT - self.radius)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        elif keys[pygame.K_SPACE]:
            dist = math.hypot(ball.x - self.x, ball.y - self.y)
            if dist < self.radius + ball.radius + 18:
                target_y = (GOAL_TOP + GOAL_BOTTOM) / 2
                angle = math.atan2(target_y - ball.y, self.target_goal_x - ball.x)
                angle += random.uniform(-0.10, 0.10)
                ball.vx = math.cos(angle) * self.shot_power
                ball.vy = math.sin(angle) * self.shot_power
                self.shoot_cooldown = 22
                self.kick_anim = 12
                self.facing_angle = angle

        if self.kick_anim > 0:
            self.kick_anim -= 1

    def update_ai(self, ball):
        target_x = self.x
        target_y = self.y
        goal_mid_y = (GOAL_TOP + GOAL_BOTTOM) / 2

        if self.role == "GK":
            # 골키퍼 AI: 골문 앞 사수 및 근접 볼 걷어내기
            base_x = PITCH_LEFT + 28 if self.is_home else PITCH_RIGHT - 28
            in_danger_zone = (ball.x < PITCH_LEFT + 150) if self.is_home else (ball.x > PITCH_RIGHT - 150)

            if in_danger_zone and (GOAL_TOP - 20 <= ball.y <= GOAL_BOTTOM + 20):
                target_x = ball.x
                target_y = ball.y
            else:
                target_x = base_x
                target_y = max(GOAL_TOP + 10, min(GOAL_BOTTOM - 10, ball.y))

        elif self.role == "MF":
            # 미드필더 AI: 공수 밸런스 유지 및 중원 압박
            if self.is_home:
                if ball.x < WIDTH * 0.45:
                    target_x = ball.x + (10 if ball.x < self.x else 25)
                    target_y = ball.y
                else:
                    target_x = WIDTH * 0.40 + (ball.x - WIDTH * 0.5) * 0.3
                    target_y = goal_mid_y + (ball.y - goal_mid_y) * 0.5
            else:
                if ball.x > WIDTH * 0.55:
                    target_x = ball.x - (10 if ball.x > self.x else 25)
                    target_y = ball.y
                else:
                    target_x = WIDTH * 0.60 + (ball.x - WIDTH * 0.5) * 0.3
                    target_y = goal_mid_y + (ball.y - goal_mid_y) * 0.5

        else:  # "FW" 공격수 AI
            if self.is_home:
                target_x = ball.x + (10 if ball.x < self.x else 22)
                target_y = ball.y
            else:
                target_x = ball.x - (10 if ball.x > self.x else 22)
                target_y = ball.y

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        self.is_moving = (dist > 4)
        if self.is_moving:
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
            self.facing_angle = math.atan2(self.vy, self.vx)
            self.run_cycle += 0.22
        else:
            self.vx = 0.0
            self.vy = 0.0
            self.facing_angle = math.atan2(ball.y - self.y, ball.x - self.x)

        self.x += self.vx
        self.y += self.vy

        # 역할별 위치 제한
        if self.role == "GK":
            if self.is_home:
                self.clamp_position(PITCH_LEFT + self.radius, PITCH_LEFT + 150)
            else:
                self.clamp_position(PITCH_RIGHT - 150, PITCH_RIGHT - self.radius)
        else:
            self.clamp_position(PITCH_LEFT + self.radius, PITCH_RIGHT - self.radius)

        if self.kick_anim > 0:
            self.kick_anim -= 1

    def clamp_position(self, min_x, max_x):
        self.x = max(min_x, min(max_x, self.x))
        self.y = max(PITCH_TOP + self.radius, min(PITCH_BOTTOM - self.radius, self.y))

    def collide_with_ball(self, ball):
        dx = ball.x - self.x
        dy = ball.y - self.y
        dist = math.hypot(dx, dy)
        min_dist = self.radius + ball.radius

        if 0 < dist < min_dist:
            overlap = min_dist - dist
            nx = dx / dist
            ny = dy / dist
            ball.x += nx * overlap
            ball.y += ny * overlap

            if not self.is_user:
                # AI 선수 슈팅/클리어 판단
                target_y = (GOAL_TOP + GOAL_BOTTOM) / 2
                angle = math.atan2(target_y - ball.y, self.target_goal_x - ball.x)
                angle += random.uniform(-0.15, 0.15)
                power = self.shot_power if (self.role in ("FW", "GK")) else self.shot_power * 0.85
                ball.vx = math.cos(angle) * power
                ball.vy = math.sin(angle) * power
            else:
                push_power = 6.2
                ball.vx = nx * push_power + self.vx * 1.3
                ball.vy = ny * push_power + self.vy * 1.3

            self.kick_anim = 8

    def draw(self, surface):
        px, py = int(self.x), int(self.y)
        ang = self.facing_angle
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        perp_cos = -sin_a
        perp_sin = cos_a

        # 1. 그림자
        pygame.draw.ellipse(surface, (20, 20, 20), (px - 15, py + 8, 30, 12))

        # 2. 플레이어(YOU) 강조 표시 링
        if self.is_user:
            pygame.draw.circle(surface, COLOR_YELLOW, (px, py), self.radius + 4, 2)

        # 3. 다리 & 축구화
        leg_swing = math.sin(self.run_cycle) * 7.0 if self.is_moving else 0.0
        if self.kick_anim > 0:
            leg_swing = 10.0

        for side, swing in [(-1, leg_swing), (1, -leg_swing)]:
            lx = px + perp_cos * (side * 7) + cos_a * swing
            ly = py + perp_sin * (side * 7) + sin_a * swing
            pygame.draw.circle(surface, self.team["secondary"], (int(lx), int(ly)), 5)
            boot_x = int(lx + cos_a * 5)
            boot_y = int(ly + sin_a * 5)
            pygame.draw.circle(surface, (25, 25, 25), (boot_x, boot_y), 3)
            pygame.draw.circle(surface, (230, 230, 230), (boot_x, boot_y), 1)

        # 4. 양팔 & 손
        arm_swing = -leg_swing * 0.7
        for side, swing in [(-1, arm_swing), (1, -arm_swing)]:
            ax = px + perp_cos * (side * 12) + cos_a * swing
            ay = py + perp_sin * (side * 12) + sin_a * swing
            pygame.draw.circle(surface, self.team["color"], (int(ax), int(ay)), 4)
            hx = int(ax + cos_a * 4)
            hy = int(ay + sin_a * 4)
            pygame.draw.circle(surface, self.team["skin"], (hx, hy), 3)

        # 5. 몸통 (국가대표 유니폼 저지)
        pygame.draw.ellipse(surface, self.team["color"], (px - 11, py - 9, 22, 18))
        pygame.draw.circle(surface, self.team["accent"], (px, py - 2), 4, 1)

        # 6. 머리 & 얼굴
        hx = int(px + cos_a * 2)
        hy = int(py + sin_a * 2 - 3)
        pygame.draw.circle(surface, self.team["skin"], (hx, hy), 9)
        hair_ox = int(hx - cos_a * 2)
        hair_oy = int(hy - sin_a * 2 - 2)
        pygame.draw.circle(surface, self.team["hair"], (hair_ox, hair_oy), 8)
        eye_x = int(hx + cos_a * 5)
        eye_y = int(hy + sin_a * 5)
        pygame.draw.circle(surface, (20, 20, 20), (eye_x, eye_y), 1)

        # 7. 머리 위 뱃지 및 라벨
        flag_y = py - 34
        surface.blit(self.mini_flag, (px - 9, flag_y))
        font = pygame.font.SysFont("arial", 10, bold=True)
        lbl_color = COLOR_YELLOW if self.is_user else (240, 240, 240)
        txt_s = font.render(self.label, True, lbl_color)
        surface.blit(txt_s, txt_s.get_rect(center=(px, flag_y - 6)))


class SoccerGame:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("⚽ 2022 월드컵 3 vs 3 미니 축구 게임")
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("malgungothic,segoeui,arial", 30, bold=True)
        self.font_large = pygame.font.SysFont("malgungothic,segoeui,arial", 40, bold=True)
        self.font_medium = pygame.font.SysFont("malgungothic,segoeui,arial", 20, bold=True)
        self.font_small = pygame.font.SysFont("malgungothic,segoeui,arial", 13)
        self.font_card = pygame.font.SysFont("malgungothic,segoeui,arial", 14, bold=True)

        # 팀 국기 캐싱
        self.team_flags = {}
        for t in TEAMS_DATA:
            self.team_flags[t["code"]] = {
                "large": create_flag_surface(t["code"], 64, 42),
                "medium": create_flag_surface(t["code"], 44, 29),
                "small": create_flag_surface(t["code"], 24, 16),
            }

        self.selected_index = 0
        self.diff_index = 1  # 0: 쉬움, 1: 보통, 2: 어려움 (기본값: 보통)
        self.state = "SELECT_TEAM"  # 'SELECT_TEAM', 'PLAYING', 'GOAL', 'GAME_OVER'

        self.player_team = TEAMS_DATA[0]
        self.ai_team = TEAMS_DATA[1]
        self.current_diff = DIFFICULTIES[1]

        self.ball = None
        self.players = []
        self.user_player = None

        self.score_player = 0
        self.score_ai = 0
        self.time_left = MATCH_TIME
        self.last_timer_tick = 0
        self.goal_anim_timer = 0
        self.goal_scorer = ""
        self.particles = []
        self.winner = ""

    def setup_match(self):
        self.player_team = TEAMS_DATA[self.selected_index]
        self.current_diff = DIFFICULTIES[self.diff_index]

        available_ai = [t for i, t in enumerate(TEAMS_DATA) if i != self.selected_index]
        self.ai_team = random.choice(available_ai)

        self.ball = Ball(WIDTH // 2, HEIGHT // 2)

        # 아군 3명 구성 (GK, MF, 플레이어 FW)
        home_gk = Player(PITCH_LEFT + 35, HEIGHT // 2, self.player_team, "GK", is_user=False, is_home=True, difficulty=self.current_diff)
        home_mf = Player(WIDTH * 0.28, HEIGHT // 2 - 80, self.player_team, "MF", is_user=False, is_home=True, difficulty=self.current_diff)
        home_user = Player(WIDTH * 0.38, HEIGHT // 2 + 50, self.player_team, "FW", is_user=True, is_home=True, difficulty=self.current_diff)
        self.user_player = home_user

        # 상대 AI 3명 구성 (GK, MF, FW)
        away_gk = Player(PITCH_RIGHT - 35, HEIGHT // 2, self.ai_team, "GK", is_user=False, is_home=False, difficulty=self.current_diff)
        away_mf = Player(WIDTH * 0.72, HEIGHT // 2 + 80, self.ai_team, "MF", is_user=False, is_home=False, difficulty=self.current_diff)
        away_fw = Player(WIDTH * 0.62, HEIGHT // 2 - 50, self.ai_team, "FW", is_user=False, is_home=False, difficulty=self.current_diff)

        self.players = [home_gk, home_mf, home_user, away_gk, away_mf, away_fw]

        self.score_player = 0
        self.score_ai = 0
        self.time_left = MATCH_TIME
        self.last_timer_tick = pygame.time.get_ticks()
        self.particles.clear()
        self.winner = ""
        self.state = "PLAYING"

    def handle_selection_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_KP1):
                self.diff_index = 0
            elif event.key in (pygame.K_2, pygame.K_KP2):
                self.diff_index = 1
            elif event.key in (pygame.K_3, pygame.K_KP3):
                self.diff_index = 2
            elif event.key == pygame.K_TAB:
                self.diff_index = (self.diff_index + 1) % 3
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                if self.selected_index % 4 > 0:
                    self.selected_index -= 1
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                if self.selected_index % 4 < 3 and self.selected_index < len(TEAMS_DATA) - 1:
                    self.selected_index += 1
            elif event.key in (pygame.K_UP, pygame.K_w):
                if self.selected_index >= 4:
                    self.selected_index -= 4
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                if self.selected_index + 4 < len(TEAMS_DATA):
                    self.selected_index += 4
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.setup_match()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # 난이도 버튼 클릭 감지
            diff_w, diff_h = 170, 36
            diff_start_x = (WIDTH - (3 * diff_w + 2 * 16)) // 2
            diff_y = 82
            for d in range(3):
                dx = diff_start_x + d * (diff_w + 16)
                if pygame.Rect(dx, diff_y, diff_w, diff_h).collidepoint(mx, my):
                    self.diff_index = d
                    return

            # 팀 카드 클릭 감지
            card_w, card_h = 190, 88
            gap_x, gap_y = 20, 14
            start_x = (WIDTH - (4 * card_w + 3 * gap_x)) // 2
            start_y = 158
            for i in range(len(TEAMS_DATA)):
                col = i % 4
                row = i // 4
                x = start_x + col * (card_w + gap_x)
                y = start_y + row * (card_h + gap_y)
                if pygame.Rect(x, y, card_w, card_h).collidepoint(mx, my):
                    self.selected_index = i
                    self.setup_match()
                    break

    def draw_selection_screen(self):
        self.screen.fill((18, 28, 40))
        pygame.draw.rect(self.screen, (26, 42, 60), (0, 0, WIDTH, 142))

        # 메인 타이틀
        title = self.font_title.render("🏆 2022 월드컵 3 vs 3 축구: 국가 및 난이도 선택 🏆", True, COLOR_YELLOW)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 28)))

        # 1. 난이도 선택 바
        diff_w, diff_h = 170, 36
        diff_start_x = (WIDTH - (3 * diff_w + 2 * 16)) // 2
        diff_y = 60

        for d, diff in enumerate(DIFFICULTIES):
            dx = diff_start_x + d * (diff_w + 16)
            d_rect = pygame.Rect(dx, diff_y, diff_w, diff_h)
            is_active = (d == self.diff_index)

            bg_c = (42, 70, 95) if is_active else (25, 36, 50)
            pygame.draw.rect(self.screen, bg_c, d_rect, border_radius=6)
            bdr_c = diff["color"] if is_active else (60, 75, 95)
            pygame.draw.rect(self.screen, bdr_c, d_rect, 3 if is_active else 1, border_radius=6)

            txt_c = (255, 255, 255) if is_active else (180, 190, 205)
            d_txt = self.font_medium.render(f"[{d+1}] {diff['name']}", True, txt_c)
            self.screen.blit(d_txt, d_txt.get_rect(center=d_rect.center))

        # 선택된 난이도 설명 문구
        active_diff = DIFFICULTIES[self.diff_index]
        desc_txt = self.font_small.render(f"💡 {active_diff['desc']}  (키보드 1 / 2 / 3 또는 클릭)", True, active_diff["color"])
        self.screen.blit(desc_txt, desc_txt.get_rect(center=(WIDTH // 2, 118)))

        # 2. 16개국 카드 그리드 (4x4)
        card_w, card_h = 190, 88
        gap_x, gap_y = 20, 14
        start_x = (WIDTH - (4 * card_w + 3 * gap_x)) // 2
        start_y = 158

        for i, team in enumerate(TEAMS_DATA):
            col = i % 4
            row = i // 4
            x = start_x + col * (card_w + gap_x)
            y = start_y + row * (card_h + gap_y)
            rect = pygame.Rect(x, y, card_w, card_h)
            is_selected = (i == self.selected_index)

            bg_color = (40, 68, 96) if is_selected else (24, 38, 52)
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)

            border_color = COLOR_YELLOW if is_selected else (50, 72, 95)
            border_width = 3 if is_selected else 1
            pygame.draw.rect(self.screen, border_color, rect, border_width, border_radius=8)

            flag = self.team_flags[team["code"]]["medium"]
            self.screen.blit(flag, (x + 10, y + 14))

            name_txt = self.font_card.render(team["name"], True, (255, 255, 255) if is_selected else (220, 220, 220))
            self.screen.blit(name_txt, (x + 62, y + 14))
            en_txt = self.font_small.render(team["name_en"], True, (170, 190, 210))
            self.screen.blit(en_txt, (x + 62, y + 34))

            pygame.draw.circle(self.screen, team["color"], (x + 70, y + 64), 7)
            pygame.draw.circle(self.screen, team["secondary"], (x + 90, y + 64), 7)
            code_lbl = self.font_small.render(team["code"], True, (150, 165, 185))
            self.screen.blit(code_lbl, (x + 108, y + 56))

        # 하단 가이드 문구
        guide = self.font_medium.render("국가 선택 후 [ENTER] 또는 [SPACE]를 눌러 3 vs 3 매치 시작!", True, COLOR_YELLOW)
        self.screen.blit(guide, guide.get_rect(center=(WIDTH // 2, HEIGHT - 22)))

    def reset_positions(self):
        self.ball.reset(WIDTH // 2, HEIGHT // 2)
        for p in self.players:
            p.reset()

    def check_goal(self):
        if self.ball.x > PITCH_RIGHT and GOAL_TOP <= self.ball.y <= GOAL_BOTTOM:
            self.score_player += 1
            self.trigger_goal(f"{self.player_team['name']} (아군)")
        elif self.ball.x < PITCH_LEFT and GOAL_TOP <= self.ball.y <= GOAL_BOTTOM:
            self.score_ai += 1
            self.trigger_goal(f"{self.ai_team['name']} (상대)")

    def trigger_goal(self, scorer):
        self.state = "GOAL"
        self.goal_scorer = scorer
        self.goal_anim_timer = 100
        team = self.player_team if "아군" in scorer else self.ai_team
        for _ in range(70):
            self.particles.append(Particle(self.ball.x, self.ball.y, team["color"]))
            self.particles.append(Particle(self.ball.x, self.ball.y, COLOR_YELLOW))

        if self.score_player >= MAX_GOALS:
            self.winner = f"🏆 {self.player_team['name']} (아군 승리!) 🏆"
        elif self.score_ai >= MAX_GOALS:
            self.winner = f"🏆 {self.ai_team['name']} (상대 승리) 🏆"

    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)

        if self.state == "GOAL":
            self.goal_anim_timer -= 1
            self.ball.update()
            if self.goal_anim_timer <= 0:
                if self.winner:
                    self.state = "GAME_OVER"
                else:
                    self.reset_positions()
                    self.state = "PLAYING"
            return

        if self.state == "GAME_OVER":
            return

        now = pygame.time.get_ticks()
        if now - self.last_timer_tick >= 1000:
            self.time_left -= 1
            self.last_timer_tick = now
            if self.time_left <= 0:
                self.time_left = 0
                if self.score_player > self.score_ai:
                    self.winner = f"🏆 {self.player_team['name']} (아군 승리!) 🏆"
                elif self.score_ai > self.score_player:
                    self.winner = f"🏆 {self.ai_team['name']} (상대 승리) 🏆"
                else:
                    self.winner = "🤝 DRAW MATCH (무승부)! 🤝"
                self.state = "GAME_OVER"
                return

        keys = pygame.key.get_pressed()

        # 선수들 이동 업데이트
        for p in self.players:
            if p.is_user:
                p.update_user(keys, self.ball)
            else:
                p.update_ai(self.ball)
            p.collide_with_ball(self.ball)

        # 6명 선수 간 충돌 판정
        self.collide_all_players()

        # 공 이동 및 골 체크
        self.ball.update()
        self.check_goal()

    def collide_all_players(self):
        n = len(self.players)
        for i in range(n):
            for j in range(i + 1, n):
                p1 = self.players[i]
                p2 = self.players[j]
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                dist = math.hypot(dx, dy)
                min_dist = p1.radius + p2.radius
                if 0 < dist < min_dist:
                    overlap = (min_dist - dist) / 2
                    nx = dx / dist
                    ny = dy / dist
                    p1.x -= nx * overlap
                    p1.y -= ny * overlap
                    p2.x += nx * overlap
                    p2.y += ny * overlap

    def draw_pitch(self):
        stripe_width = 70
        for i, x in enumerate(range(PITCH_LEFT, PITCH_RIGHT, stripe_width)):
            color = COLOR_PITCH_1 if i % 2 == 0 else COLOR_PITCH_2
            w = min(stripe_width, PITCH_RIGHT - x)
            pygame.draw.rect(self.screen, color, (x, PITCH_TOP, w, PITCH_BOTTOM - PITCH_TOP))

        pygame.draw.rect(self.screen, (24, 60, 40), (0, 0, WIDTH, HEIGHT), PITCH_TOP)
        pygame.draw.rect(self.screen, COLOR_LINE, (PITCH_LEFT, PITCH_TOP, PITCH_RIGHT - PITCH_LEFT, PITCH_BOTTOM - PITCH_TOP), 3)

        mid_x = WIDTH // 2
        mid_y = (PITCH_TOP + PITCH_BOTTOM) // 2
        pygame.draw.line(self.screen, COLOR_LINE, (mid_x, PITCH_TOP), (mid_x, PITCH_BOTTOM), 2)
        pygame.draw.circle(self.screen, COLOR_LINE, (mid_x, mid_y), 70, 2)
        pygame.draw.circle(self.screen, COLOR_LINE, (mid_x, mid_y), 5)

        box_w, box_h = 110, 240
        box_top = (HEIGHT - box_h) // 2
        pygame.draw.rect(self.screen, COLOR_LINE, (PITCH_LEFT, box_top, box_w, box_h), 2)
        pygame.draw.rect(self.screen, COLOR_LINE, (PITCH_RIGHT - box_w, box_top, box_w, box_h), 2)

        pygame.draw.rect(self.screen, (220, 220, 220), (PITCH_LEFT - GOAL_DEPTH, GOAL_TOP, GOAL_DEPTH, GOAL_BOTTOM - GOAL_TOP))
        pygame.draw.rect(self.screen, (100, 100, 100), (PITCH_LEFT - GOAL_DEPTH, GOAL_TOP, GOAL_DEPTH, GOAL_BOTTOM - GOAL_TOP), 2)
        pygame.draw.rect(self.screen, (220, 220, 220), (PITCH_RIGHT, GOAL_TOP, GOAL_DEPTH, GOAL_BOTTOM - GOAL_TOP))
        pygame.draw.rect(self.screen, (100, 100, 100), (PITCH_RIGHT, GOAL_TOP, GOAL_DEPTH, GOAL_BOTTOM - GOAL_TOP), 2)

    def draw_hud(self):
        pygame.draw.rect(self.screen, (18, 28, 40), (0, 0, WIDTH, PITCH_TOP))

        # 아군 (왼쪽)
        flag_p = self.team_flags[self.player_team["code"]]["medium"]
        self.screen.blit(flag_p, (PITCH_LEFT, 16))
        p_name = self.font_medium.render(f"{self.player_team['name']} (아군 3명)", True, (255, 255, 255))
        self.screen.blit(p_name, (PITCH_LEFT + 52, 19))

        # 중앙 스코어보드 & 타이머 & 난이도 표시
        mid_x = WIDTH // 2
        score_txt = self.font_large.render(f"{self.score_player}  :  {self.score_ai}", True, COLOR_YELLOW)
        self.screen.blit(score_txt, score_txt.get_rect(center=(mid_x, 28)))

        diff_badge = self.font_small.render(f"난이도: {self.current_diff['name'].split()[0]}", True, self.current_diff["color"])
        self.screen.blit(diff_badge, diff_badge.get_rect(center=(mid_x, 50)))

        # 상대 AI (오른쪽)
        flag_ai = self.team_flags[self.ai_team["code"]]["medium"]
        ai_name = self.font_medium.render(f"(상대 3명) {self.ai_team['name']}", True, (255, 255, 255))
        self.screen.blit(ai_name, (WIDTH - PITCH_LEFT - 52 - ai_name.get_width(), 19))
        self.screen.blit(flag_ai, (WIDTH - PITCH_LEFT - 44, 16))

        # 타이머
        mins, secs = self.time_left // 60, self.time_left % 60
        timer_txt = self.font_medium.render(f"⏱ {mins:02d}:{secs:02d}", True, (240, 240, 240))
        self.screen.blit(timer_txt, (mid_x + 95, 18))

        # 하단 가이드 문구
        guide = "조작: 이동 [방향키 / WASD]  |  슈팅 [스페이스바]  |  난이도/팀 다시선택 [T]  |  재시작 [R]  |  종료 [ESC]"
        guide_txt = self.font_small.render(guide, True, (230, 230, 230))
        self.screen.blit(guide_txt, guide_txt.get_rect(center=(WIDTH // 2, HEIGHT - 20)))

    def draw_overlays(self):
        if self.state == "GOAL":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 130))
            self.screen.blit(overlay, (0, 0))

            goal_txt = self.font_large.render("⚽ GOAL !!! ⚽", True, COLOR_YELLOW)
            self.screen.blit(goal_txt, goal_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))

            sub_txt = self.font_medium.render(f"{self.goal_scorer} 득점 성공!", True, COLOR_TEXT)
            self.screen.blit(sub_txt, sub_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25)))

        elif self.state == "GAME_OVER":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            win_txt = self.font_large.render(self.winner, True, COLOR_YELLOW)
            self.screen.blit(win_txt, win_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))

            score_txt = self.font_medium.render(
                f"최종 스코어  {self.player_team['name']} {self.score_player} : {self.score_ai} {self.ai_team['name']}",
                True,
                COLOR_TEXT,
            )
            self.screen.blit(score_txt, score_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))

            guide_end = self.font_medium.render("다시 시작: [R]  |  국가/난이도 다시 선택: [T]  |  종료: [ESC]", True, (255, 255, 255))
            self.screen.blit(guide_end, guide_end.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.state == "SELECT_TEAM":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.handle_selection_events(event)
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_r:
                            self.setup_match()
                        elif event.key == pygame.K_t:
                            self.state = "SELECT_TEAM"

            if self.state == "SELECT_TEAM":
                self.draw_selection_screen()
            else:
                self.update()
                self.draw_pitch()

                # 공 그리기
                self.ball.draw(self.screen)

                # 6명 선수 그리기
                for p in self.players:
                    p.draw(self.screen)

                # 파티클 그리기
                for p in self.particles:
                    p.draw(self.screen)

                self.draw_hud()
                self.draw_overlays()

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SoccerGame()
    game.run()


