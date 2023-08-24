from random import randint
import time

import pygame


MAX_SCREEN_X = 1280
MAX_SCREEN_Y = 720
MAX_ENEMIES = 5
MAX_POWERUPS = 2


class Engine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((MAX_SCREEN_X, MAX_SCREEN_Y)) # , pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()

    def flip(self):
        pygame.display.flip()


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
            if e.type == pygame.QUIT or keys[pygame.K_q]:
                self.running = False

    def start(self):
        pass


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


def move_bullets(dt, bullets, max_bullet_bounces):
    for b in bullets[:]:
        x, y = b.move(dt)
        if x > MAX_SCREEN_X or x < 0 or \
                y > MAX_SCREEN_Y or y < 0:
            b.bounces += 1
            if b.bounces > max_bullet_bounces:
                bullets.remove(b)
            else:
                if b.x<0:
                    b.direction = (1, b.direction[1])
                else:
                    b.direction = (-1, b.direction[1])
                if b.y<0:
                    b.direction = (b.direction[0], 1)
                else:
                    b.direction = (b.direction[0], -1)

    return bullets


def draw_bullets(screen, bullets):
    for b in bullets:
        b.draw(screen)


def move_enemies(dt, player, enemies):
    for e in enemies:
        v = pygame.Vector2(e.x, e.y).move_towards(
                pygame.Vector2(player.x, player.y), 200 * dt)
        e.move(dt,
               v.x, v.y)
    return enemies


def draw_enemies(screen, enemies):
    for e in enemies:
        e.draw(screen)


def draw_powerups(screen, powerups):
    for p in powerups:
        p.draw(screen)


def check_enemy_hits(enemies, bullets):
    for enemy in enemies[:]:
        hit = enemy.rect.collidelist([b.rect for b in bullets])
        if hit >= 0:
            bullets.remove(bullets[hit])
            enemies.remove(enemy)


def check_powerup_pickup(player, powerups):
    hit = player.rect.collidelist([p.rect for p in powerups])
    if hit >= 0:
        powerups.remove(powerups[hit])
        return True
    else:
        return False


def can_generate_enemies(enemies):
    return len(enemies) < MAX_ENEMIES


def can_generate_powerup(powerups):
    return len(powerups) < MAX_POWERUPS


engine = Engine()
screen = engine.screen
clock = engine.clock

player = Player()
bullets = []
enemies = []
powerups = []
last_shot = time.time()
shot_delay = 0.3
framerate = 60
enabled_autofire = False
last_autofire_press = time.time()
running = True
max_bullet_bounces = 0

while running:
    dt = clock.tick(framerate) / 1000
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_q]:
            running = False

    if keys[pygame.K_f]:
        if time.time() - last_autofire_press > 1:
            enabled_autofire = not enabled_autofire
            last_autofire_press = time.time()

    move_y = (keys[pygame.K_DOWN] - keys[pygame.K_UP])
    move_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT])
    player.move(dt, move_x, move_y)

    if (keys[pygame.K_SPACE] or enabled_autofire) and player.is_moving:
        if time.time() - last_shot > shot_delay:
            last_shot = time.time()
            bullet = Bullet(player.x, player.y, (move_x, move_y))
            bullets.append(bullet)

    if can_generate_enemies(enemies):
        generate_enemy = randint(0, 100)
        if keys[pygame.K_RETURN] or generate_enemy>95:
            enemy = Enemy()
            enemies.append(enemy)

    if can_generate_powerup(powerups):
        generate_powerup = randint(0, 500)
        if generate_powerup > 480:
            powerup = Powerup()
            powerups.append(powerup)

    if check_powerup_pickup(player, powerups):
        max_bullet_bounces += 1
        screen.fill("gray")
    else:
        screen.fill("black")
    bullets = move_bullets(dt, bullets, max_bullet_bounces)
    enemies = move_enemies(dt, player, enemies)
    draw_bullets(screen, bullets)
    draw_enemies(screen, enemies)
    draw_powerups(screen, powerups)
    player.draw(screen)
    check_enemy_hits(enemies, bullets)
    engine.flip()
    clock.tick(framerate)
    pygame.display.set_caption(str(round(clock.get_fps())))
    print(len(bullets))

pygame.quit()