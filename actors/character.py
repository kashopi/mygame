from hashlib import md5
import pygame


class Character(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.id = md5(str(self).encode("utf-8")).hexdigest()


class Scenario(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self._image = pygame.image.load("/home/ksp/p/mygame/assets/bg.png")
        self.width = self._image.get_width()
        self.height = self._image.get_height()

    def get_image(self):
        return self._image


class Camera:
    def __init__(self, viewport_width: int, viewport_height: int, scenario: Scenario):
        self._viewport_width = viewport_width
        self._viewport_height = viewport_height
        self._scenario = scenario
        self._center_x = self._scenario.width // 2
        self._center_y = self._scenario.height // 2

    def move(self, translation_x: int, translation_y: int):

        self._center_x += translation_x
        self._center_y += translation_y
        distance_to_border_left = self._center_x - self._viewport_width/2 + translation_x
        distance_to_border_right = self._viewport_width / 2 + self._center_x + translation_x
        distance_to_border_top = self._center_y - self._viewport_height/2 + translation_y
        distance_to_border_bottom = self._viewport_height / 2 + self._center_y + translation_y

        if distance_to_border_left < 0:
            self._center_x = self._viewport_width // 2
        elif distance_to_border_right > self._scenario.width:
            self._center_x = self._scenario.width - self._viewport_width //2

        if distance_to_border_top < 0:
            self._center_y = self._viewport_height // 2
        elif distance_to_border_bottom > self._scenario.height:
            self._center_y = self._scenario.height - self._viewport_height // 2

    def get_view_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self._center_x - self._viewport_width // 2,
            self._center_y - self._viewport_height // 2,
            self._viewport_width,
            self._viewport_height
        )

    def __str__(self):
        return f"Camera> x={self._center_x}, y={self._center_y}, vp:({self._viewport_width}x{self._viewport_height})"


class Scene:
    def __init__(self, scenario: Scenario, camera: Camera):
        self.scenario = scenario
        self.camera = camera

    def move_camera(self, translation_x: int, translation_y: int):
        self.camera.move(translation_x, translation_y)

    def draw(self, screen):
        view_rect = self.camera.get_view_rect()
        screen.blit(self.scenario.get_image(), (0, 0), view_rect)


s = Scenario()
c = Camera(320, 240, s)
scene = Scene(s, c)
screen = pygame.display.set_mode((320, 240))  # , pygame.FULLSCREEN)
clock = pygame.time.Clock()

running = True
while running:
    dt = clock.tick(60) / 1000
    keys = pygame.key.get_pressed()
    for e in pygame.event.get():
        if e.type == pygame.QUIT or keys[pygame.K_q]:
            running = False
    if keys[pygame.K_LEFT]:
        scene.move_camera(-25, 0)
    if keys[pygame.K_RIGHT]:
        scene.move_camera(25, 0)
    if keys[pygame.K_UP]:
        scene.move_camera(0, -25)
    if keys[pygame.K_DOWN]:
        scene.move_camera(0, 25)

    screen.fill("gray")
    scene.draw(screen)
    pygame.display.flip()
    clock.tick(60)
    print(str(c))
