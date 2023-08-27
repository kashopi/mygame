from random import randint
import time

import pygame


MAX_SCREEN_X = 1280
MAX_SCREEN_Y = 800
MAX_ENEMIES = 5
MAX_POWERUPS = 2


class Engine:
    def __init__(self):
        pygame.init()
        self.dt = None
        self.screen = pygame.display.set_mode((MAX_SCREEN_X, MAX_SCREEN_Y)) # , pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()

    def flip(self):
        pygame.display.flip()


class Player:
    def __init__(self):
        self.x = 100
        self.y = 100
        self.width = 20
        self.height = 20
        self.is_moving = False
        self.movement_factor = 550
        self.last_aim = (1, 0)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, dt, direction_x, direction_y):
        old_x, old_y = self.x, self.y
        self.x += direction_x * self.movement_factor * dt
        self.y += direction_y * self.movement_factor * dt
        self.last_aim = (direction_x, direction_y)
        if old_x != self.x or old_y != self.y:
            self.is_moving = True
        else:
            self.is_moving = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)


    def draw(self, screen):
        pygame.draw.rect(screen, "red", pygame.Rect(self.x, self.y, self.width, self.height))


class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.width = 5
        self.height = 5
        self.direction = direction
        self.speed_factor = 800
        self.bounces = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, dt) -> tuple:
        speed_x, speed_y = self.direction
        self.x += speed_x * self.speed_factor * dt
        self.y += speed_y * self.speed_factor * dt
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return self.x, self.y

    def draw(self, screen):
        pygame.draw.rect(screen, "green", self.rect)


class Enemy:
    def __init__(self):
        self.x = randint(0, MAX_SCREEN_X)
        self.y = randint(0, MAX_SCREEN_Y)
        self.width = 35
        self.height = 35
        self.is_moving = False
        self.movement_factor = 150
        self.last_aim = (1, 0)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, dt, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        pygame.draw.rect(screen, "yellow", self.rect)


class Powerup:
    def __init__(self):
        self.x = randint(0, MAX_SCREEN_X)
        self.y = randint(0, MAX_SCREEN_Y)
        self.width = 45
        self.height = 45
        self.is_moving = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        pygame.draw.rect(screen, "cyan", self.rect)


class Game(Engine):
    def __init__(self):
        super().__init__()
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.powerups = []
        self.last_shot = time.time()
        self.shot_delay = 0.3
        self.framerate = 60
        self.enabled_autofire = False
        self.last_autofire_press = time.time()
        self.running = True
        self.max_bullet_bounces = 0
        self.keys = None

    def process_input_events(self):
        self.keys = pygame.key.get_pressed()
        for e in pygame.event.get():
            if e.type == pygame.QUIT or self.keys[pygame.K_q]:
                self.running = False

        if self.keys[pygame.K_f]:
            if time.time() - self.last_autofire_press > 1:
                self.enabled_autofire = not self.enabled_autofire
                self.last_autofire_press = time.time()

    def process_player_actions(self):
        move_y = (self.keys[pygame.K_DOWN] - self.keys[pygame.K_UP])
        move_x = (self.keys[pygame.K_RIGHT] - self.keys[pygame.K_LEFT])
        self.player.move(self.dt, move_x, move_y)

        if (self.keys[pygame.K_SPACE] or self.enabled_autofire) and self.player.is_moving:
            if time.time() - self.last_shot > self.shot_delay:
                last_shot = time.time()
                bullet = Bullet(self.player.x, self.player.y, (move_x, move_y))
                self.bullets.append(bullet)

    def process_enemies_actions(self):
        if self._can_generate_enemies():
            generate_enemy = randint(0, 100)
            if self.keys[pygame.K_RETURN] or generate_enemy > 95:
                enemy = Enemy()
                self.enemies.append(enemy)

    def process_gamefield_events(self):
        if self._can_generate_powerup():
            generate_powerup = randint(0, 500)
            if generate_powerup > 480:
                powerup = Powerup()
                self.powerups.append(powerup)

    def process_secondary_collisions(self):
        if self._check_powerup_pickup():
            self.max_bullet_bounces += 1
            self.screen.fill("gray")
        else:
            self.screen.fill("black")

    def execute_logic(self):
        self.process_player_actions()
        self.process_enemies_actions()
        self.process_gamefield_events()
        self._check_enemy_hits()
        self.process_secondary_collisions()

        self._move_bullets()
        self._move_enemies()
        self._draw_bullets()
        self._draw_enemies()
        self._draw_powerups()
        self.player.draw(self.screen)

    def process_end_of_frame(self):
        self.flip()
        self.clock.tick(self.framerate)
        pygame.display.set_caption(str(round(self.clock.get_fps())))

    def _move_bullets(self):
        for b in self.bullets[:]:
            x, y = b.move(self.dt)
            if x > MAX_SCREEN_X or x < 0 or \
                    y > MAX_SCREEN_Y or y < 0:
                b.bounces += 1
                if b.bounces > self.max_bullet_bounces:
                    self.bullets.remove(b)
                else:
                    if b.x < 0:
                        b.direction = (1, b.direction[1])
                    else:
                        b.direction = (-1, b.direction[1])
                    if b.y < 0:
                        b.direction = (b.direction[0], 1)
                    else:
                        b.direction = (b.direction[0], -1)

    def _draw_bullets(self):
        for b in self.bullets:
            b.draw(self.screen)

    def _move_enemies(self):
        for e in self.enemies:
            v = pygame.Vector2(e.x, e.y).move_towards(
                pygame.Vector2(self.player.x, self.player.y), 200 * self.dt)
            e.move(self.dt,
                   v.x, v.y)

    def _draw_enemies(self):
        for e in self.enemies:
            e.draw(self.screen)

    def _draw_powerups(self):
        for p in self.powerups:
            p.draw(self.screen)

    def _check_enemy_hits(self):
        for enemy in self.enemies[:]:
            hit = enemy.rect.collidelist([b.rect for b in self.bullets])
            if hit >= 0:
                self.bullets.remove(self.bullets[hit])
                self.enemies.remove(enemy)

    def _check_powerup_pickup(self):
        hit = self.player.rect.collidelist([p.rect for p in self.powerups])
        if hit >= 0:
            self.powerups.remove(self.powerups[hit])
            return True
        else:
            return False

    def _can_generate_enemies(self):
        return len(self.enemies) < MAX_ENEMIES

    def _can_generate_powerup(self):
        return len(self.powerups) < MAX_POWERUPS

    def start(self):
        while self.running:
            self.dt = self.clock.tick(self.framerate) / 1000
            self.process_input_events()
            self.execute_logic()
            self.process_end_of_frame()
        pygame.quit()


game = Game()
game.start()