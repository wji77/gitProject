"""
Mini Soccer Game (미니 축구 게임)
Controls:
  - 이동: 방향키(화살표) 또는 W / A / S / D
  - 슈팅(파워 슛): 스페이스바 (공 근처에서)
  - 재시작: R 키
  - 종료: ESC 키
"""

import math
import random
import sys
import pygame

WIDTH, HEIGHT = 900, 600
FPS = 60

COLOR_PITCH_1 = (46, 139, 87)
COLOR_PITCH_2 = (52, 158, 98)
COLOR_LINE = (240, 240, 240)
COLOR_BLUE = (30, 144, 255)
COLOR_BLUE_DARK = (16, 78, 139)
COLOR_RED = (238, 44, 44)
COLOR_RED_DARK = (139, 26, 26)
COLOR_BALL = (255, 255, 255)
COLOR_BALL_PENTAGON = (30, 30, 30)
COLOR_TEXT = (255, 255, 255)
COLOR_YELLOW = (255, 215, 0)

PITCH_LEFT = 50
PITCH_RIGHT = WIDTH - 50
PITCH_TOP = 50
PITCH_BOTTOM = HEIGHT - 50
GOAL_TOP = 220
GOAL_BOTTOM = 380
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
        speed = random.uniform(2, 7)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = random.randint(30, 55)
        self.radius = random.uniform(3, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.lifetime -= 1
        self.radius = max(0.0, self.radius - 0.06)

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

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.friction
        self.vy *= self.friction

        if abs(self.vx) < 0.05:
            self.vx = 0.0
        if abs(self.vy) < 0.05:
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
        pygame.draw.circle(surface, (20, 20, 20), (int(self.x) + 2, int(self.y) + 3), self.radius)
        pygame.draw.circle(surface, COLOR_BALL, pos, self.radius)
        pygame.draw.circle(surface, COLOR_BALL_PENTAGON, pos, 4)
        for i in range(5):
            angle = i * (2 * math.pi / 5)
            ox = int(self.x + math.cos(angle) * (self.radius - 3))
            oy = int(self.y + math.sin(angle) * (self.radius - 3))
            pygame.draw.circle(surface, COLOR_BALL_PENTAGON, (ox, oy), 2)
        pygame.draw.circle(surface, (100, 100, 100), pos, self.radius, 1)


class Player:
    def __init__(self, x, y, color, dark_color, is_ai=False):
        self.start_x = x
        self.start_y = y
        self.radius = 18
        self.color = color
        self.dark_color = dark_color
        self.is_ai = is_ai
        self.speed = 4.2 if is_ai else 4.6
        self.shoot_cooldown = 0
        self.reset()

    def reset(self):
        self.x = float(self.start_x)
        self.y = float(self.start_y)
        self.vx = 0.0
        self.vy = 0.0

    def update_human(self, keys, ball):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.vx = dx * self.speed
        self.vy = dy * self.speed
        self.x += self.vx
        self.y += self.vy
        self.clamp_position(PITCH_LEFT + self.radius, PITCH_RIGHT - self.radius)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        elif keys[pygame.K_SPACE]:
            dist = math.hypot(ball.x - self.x, ball.y - self.y)
            if dist < self.radius + ball.radius + 15:
                target_x = PITCH_RIGHT
                target_y = (GOAL_TOP + GOAL_BOTTOM) / 2
                angle = math.atan2(target_y - ball.y, target_x - ball.x)
                angle += random.uniform(-0.12, 0.12)
                ball.vx = math.cos(angle) * 14.0
                ball.vy = math.sin(angle) * 14.0
                self.shoot_cooldown = 25

    def update_ai(self, ball):
        if ball.x < WIDTH * 0.45:
            target_x = WIDTH * 0.75
            target_y = (GOAL_TOP + GOAL_BOTTOM) / 2 + (ball.y - HEIGHT / 2) * 0.35
        else:
            target_x = ball.x + (10 if ball.x < self.x else 25)
            target_y = ball.y

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        if dist > 4:
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
        else:
            self.vx = 0.0
            self.vy = 0.0

        self.x += self.vx
        self.y += self.vy
        self.clamp_position(WIDTH * 0.4, PITCH_RIGHT - self.radius)

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
            push_power = 6.0
            ball.vx = nx * push_power + self.vx * 1.3
            ball.vy = ny * push_power + self.vy * 1.3

    def draw(self, surface):
        pos = (int(self.x), int(self.y))
        pygame.draw.circle(surface, (20, 20, 20), (pos[0] + 3, pos[1] + 4), self.radius)
        pygame.draw.circle(surface, self.color, pos, self.radius)
        pygame.draw.circle(surface, self.dark_color, pos, self.radius, 3)
        label = "AI" if self.is_ai else "YOU"
        font = pygame.font.SysFont("arial", 11, bold=True)
        txt = font.render(label, True, (255, 255, 255))
        rect = txt.get_rect(center=pos)
        surface.blit(txt, rect)



class SoccerGame:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("⚽ 미니 축구 게임 (Mini Soccer)")
        self.clock = pygame.time.Clock()

        self.font_large = pygame.font.SysFont("malgungothic,segoeui,arial", 46, bold=True)
        self.font_medium = pygame.font.SysFont("malgungothic,segoeui,arial", 26, bold=True)
        self.font_small = pygame.font.SysFont("malgungothic,segoeui,arial", 15)

        self.ball = Ball(WIDTH // 2, HEIGHT // 2)
        self.player = Player(WIDTH * 0.25, HEIGHT // 2, COLOR_BLUE, COLOR_BLUE_DARK, is_ai=False)
        self.ai = Player(WIDTH * 0.75, HEIGHT // 2, COLOR_RED, COLOR_RED_DARK, is_ai=True)

        self.score_player = 0
        self.score_ai = 0
        self.time_left = MATCH_TIME
        self.last_timer_tick = pygame.time.get_ticks()

        self.goal_anim_timer = 0
        self.goal_scorer = ""
        self.particles = []
        self.state = 'PLAYING'
        self.winner = ""

    def reset_positions(self):
        self.ball.reset(WIDTH // 2, HEIGHT // 2)
        self.player.reset()
        self.ai.reset()

    def check_goal(self):
        if self.ball.x > PITCH_RIGHT and GOAL_TOP <= self.ball.y <= GOAL_BOTTOM:
            self.score_player += 1
            self.trigger_goal("PLAYER (BLUE)")
        elif self.ball.x < PITCH_LEFT and GOAL_TOP <= self.ball.y <= GOAL_BOTTOM:
            self.score_ai += 1
            self.trigger_goal("AI (RED)")

    def trigger_goal(self, scorer):
        self.state = 'GOAL'
        self.goal_scorer = scorer
        self.goal_anim_timer = 100
        color = COLOR_BLUE if "BLUE" in scorer else COLOR_RED
        for _ in range(60):
            self.particles.append(Particle(self.ball.x, self.ball.y, color))
            self.particles.append(Particle(self.ball.x, self.ball.y, COLOR_YELLOW))

        if self.score_player >= MAX_GOALS:
            self.winner = "PLAYER (BLUE) WIN!"
        elif self.score_ai >= MAX_GOALS:
            self.winner = "AI (RED) WIN!"

    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.lifetime <= 0:
                self.particles.remove(p)

        if self.state == 'GOAL':
            self.goal_anim_timer -= 1
            self.ball.update()
            if self.goal_anim_timer <= 0:
                if self.winner:
                    self.state = 'GAME_OVER'
                else:
                    self.reset_positions()
                    self.state = 'PLAYING'
            return

        if self.state == 'GAME_OVER':
            return

        now = pygame.time.get_ticks()
        if now - self.last_timer_tick >= 1000:
            self.time_left -= 1
            self.last_timer_tick = now
            if self.time_left <= 0:
                self.time_left = 0
                if self.score_player > self.score_ai:
                    self.winner = "PLAYER (BLUE) WIN!"
                elif self.score_ai > self.score_player:
                    self.winner = "AI (RED) WIN!"
                else:
                    self.winner = "DRAW MATCH!"
                self.state = 'GAME_OVER'
                return

        keys = pygame.key.get_pressed()
        self.player.update_human(keys, self.ball)
        self.ai.update_ai(self.ball)
        self.player.collide_with_ball(self.ball)
        self.ai.collide_with_ball(self.ball)
        self.collide_players()
        self.ball.update()
        self.check_goal()

    def collide_players(self):
        dx = self.ai.x - self.player.x
        dy = self.ai.y - self.player.y
        dist = math.hypot(dx, dy)
        min_dist = self.player.radius + self.ai.radius
        if 0 < dist < min_dist:
            overlap = (min_dist - dist) / 2
            nx = dx / dist
            ny = dy / dist
            self.player.x -= nx * overlap
            self.player.y -= ny * overlap
            self.ai.x += nx * overlap
            self.ai.y += ny * overlap

    def draw_pitch(self):
        stripe_width = 70
        for i, x in enumerate(range(PITCH_LEFT, PITCH_RIGHT, stripe_width)):
            color = COLOR_PITCH_1 if i % 2 == 0 else COLOR_PITCH_2
            w = min(stripe_width, PITCH_RIGHT - x)
            pygame.draw.rect(self.screen, color, (x, PITCH_TOP, w, PITCH_BOTTOM - PITCH_TOP))

        pygame.draw.rect(self.screen, (30, 80, 50), (0, 0, WIDTH, HEIGHT), PITCH_TOP)
        pygame.draw.rect(self.screen, COLOR_LINE, (PITCH_LEFT, PITCH_TOP, PITCH_RIGHT - PITCH_LEFT, PITCH_BOTTOM - PITCH_TOP), 3)

        mid_x, mid_y = WIDTH // 2, HEIGHT // 2
        pygame.draw.line(self.screen, COLOR_LINE, (mid_x, PITCH_TOP), (mid_x, PITCH_BOTTOM), 2)
        pygame.draw.circle(self.screen, COLOR_LINE, (mid_x, mid_y), 70, 2)
        pygame.draw.circle(self.screen, COLOR_LINE, (mid_x, mid_y), 5)

        box_w, box_h = 100, 220
        box_top = (HEIGHT - box_h) // 2
        pygame.draw.rect(self.screen, COLOR_LINE, (PITCH_LEFT, box_top, box_w, box_h), 2)
        pygame.draw.rect(self.screen, COLOR_LINE, (PITCH_RIGHT - box_w, box_top, box_w, box_h), 2)

        pygame.draw.rect(self.screen, (220, 220, 220), (PITCH_LEFT - GOAL_DEPTH, GOAL_TOP, GOAL_DEPTH, GOAL_BOTTOM - GOAL_TOP))
        pygame.draw.rect(self.screen, (100, 100, 100), (PITCH_LEFT - GOAL_DEPTH, GOAL_TOP, GOAL_DEPTH, GOAL_BOTTOM - GOAL_TOP), 2)
        pygame.draw.rect(self.screen, (220, 220, 220), (PITCH_RIGHT, GOAL_TOP, GOAL_DEPTH, GOAL_BOTTOM - GOAL_TOP))
        pygame.draw.rect(self.screen, (100, 100, 100), (PITCH_RIGHT, GOAL_TOP, GOAL_DEPTH, GOAL_BOTTOM - GOAL_TOP), 2)

    def draw_hud(self):
        mid_x = WIDTH // 2
        p_txt = self.font_medium.render(f"BLUE  {self.score_player}", True, COLOR_BLUE)
        self.screen.blit(p_txt, (mid_x - 130, 12))

        vs_txt = self.font_medium.render(":", True, COLOR_TEXT)
        self.screen.blit(vs_txt, (mid_x - 5, 12))

        ai_txt = self.font_medium.render(f"{self.score_ai}  RED", True, COLOR_RED)
        self.screen.blit(ai_txt, (mid_x + 35, 12))

        mins, secs = self.time_left // 60, self.time_left % 60
        timer_txt = self.font_medium.render(f"{mins:02d}:{secs:02d}", True, COLOR_YELLOW)
        self.screen.blit(timer_txt, (WIDTH - 110, 12))

        guide = "조작: 이동 [화살표 / WASD]  |  파워 슛 [스페이스바]  |  재시작 [R]  |  종료 [ESC]"
        guide_txt = self.font_small.render(guide, True, (230, 230, 230))
        self.screen.blit(guide_txt, guide_txt.get_rect(center=(WIDTH // 2, HEIGHT - 22)))

    def draw_overlays(self):
        if self.state == 'GOAL':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))
            goal_txt = self.font_large.render("⚽ GOAL !!! ⚽", True, COLOR_YELLOW)
            self.screen.blit(goal_txt, goal_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 25)))
            sub_txt = self.font_medium.render(f"{self.goal_scorer} SCORED!", True, COLOR_TEXT)
            self.screen.blit(sub_txt, sub_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25)))

        elif self.state == 'GAME_OVER':
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            self.screen.blit(overlay, (0, 0))
            win_color = COLOR_BLUE if "BLUE" in self.winner else (COLOR_RED if "RED" in self.winner else COLOR_YELLOW)
            res_txt = self.font_large.render(self.winner, True, win_color)
            self.screen.blit(res_txt, res_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 45)))
            score_txt = self.font_medium.render(f"최종 스코어  BLUE {self.score_player} : {self.score_ai} RED", True, COLOR_TEXT)
            self.screen.blit(score_txt, score_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))
            restart_txt = self.font_medium.render("다시 시작: [R]  |  종료: [ESC]", True, (255, 255, 255))
            self.screen.blit(restart_txt, restart_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60)))

    def restart_game(self):
        self.score_player = 0
        self.score_ai = 0
        self.time_left = MATCH_TIME
        self.last_timer_tick = pygame.time.get_ticks()
        self.winner = ""
        self.state = 'PLAYING'
        self.reset_positions()
        self.particles.clear()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.restart_game()

            self.update()
            self.draw_pitch()
            self.player.draw(self.screen)
            self.ai.draw(self.screen)
            self.ball.draw(self.screen)

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

