import pygame
import sys

from pygame.math import Vector2

from settings import Settings
from snake import Snake
from fruit import Fruit



class SnakeGame:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()

        self.settings = Settings()

        # podesavanje prozora
        self.screen = pygame.display.set_mode(
            (self.settings.cell_number * self.settings.cell_size, self.settings.cell_number * self.settings.cell_size))
        pygame.display.set_caption('Zmija')

        self.clock = pygame.time.Clock()
        self.game_font = pygame.font.Font('font/PoetsenOne-Regular.ttf', 25)

        self.snake = Snake(self.screen)
        self.fruit = Fruit(self.screen)

    def draw_grass(self):
        for row in range(self.settings.cell_number):
            if row % 2 == 0:
                for column in range(self.settings.cell_number):
                    if column % 2 == 0:
                        grass_rect = pygame.Rect(column * self.settings.cell_size, row * self.settings.cell_size, self.settings.cell_size, self.settings.cell_size)
                        pygame.draw.rect(self.screen, self.settings.grass_color, grass_rect)
            else:
                for column in range(self.settings.cell_number):
                    if column % 2 == 1:
                        grass_rect = pygame.Rect(column * self.settings.cell_size, row * self.settings.cell_size, self.settings.cell_size, self.settings.cell_size)
                        pygame.draw.rect(self.screen, self.settings.grass_color, grass_rect)

    def draw_score(self):
        score_text = str(len(self.snake.body) - 3)
        score_surface = self.game_font.render(score_text, True, (56, 74, 12))
        score_x = int(self.settings.cell_size * self.settings.cell_number - 60)
        score_y = int(self.settings.cell_size * self.settings.cell_number - 40)
        score_rect = score_surface.get_rect(center=(score_x, score_y))
        apple_rect = self.fruit.apple.get_rect(midright=(score_rect.left, score_rect.centery))
        scoreboard_rect = pygame.Rect(apple_rect.left, apple_rect.top, apple_rect.width + score_rect.width + 6, apple_rect.height)

        pygame.draw.rect(self.screen, (167, 209, 61), scoreboard_rect)
        self.screen.blit(score_surface, score_rect)
        self.screen.blit(self.fruit.apple, apple_rect)
        pygame.draw.rect(self.screen, (56, 74, 12), scoreboard_rect, 2)

    def draw_elements(self):
        self.draw_grass()
        self.fruit.draw_fruit()
        self.snake.draw_snake()
        self.draw_score()

    def check_collision(self):
        # proveri da li je jabuka pojedena
        if self.fruit.position == self.snake.body[0]:
            self.fruit.randomize()
            self.snake.add_block()
            self.snake.play_crunch_sound()

        # promeni poziciju jabuke ako je u telu zmije
        for block in self.snake.body[1:]:
            if block == self.fruit.position:
                self.fruit.randomize()

    def check_fail(self):
        # kraj igre ukoliko je dodirnut zid
        if not 0 <= self.snake.body[0].x < self.settings.cell_number:
            self.game_over()
        if not 0 <= self.snake.body[0].y < self.settings.cell_number:
            self.game_over()

        # kraj igre ukoliko je dodirnuta zmija
        for block in self.snake.body[1:]:
            if block == self.snake.body[0]:
                self.game_over()

    def update(self):
        self.snake.move_snake()
        self.check_collision()
        self.check_fail()

    def key_events(self, event):
        if event.key == pygame.K_UP:
            if self.snake.direction.y != 1:
                self.snake.direction = Vector2(0, -1)

        if event.key == pygame.K_DOWN:
            if self.snake.direction.y != -1:
                self.snake.direction = Vector2(0, 1)

        if event.key == pygame.K_LEFT:
            if self.snake.direction.x != 1:
                self.snake.direction = Vector2(-1, 0)

        if event.key == pygame.K_RIGHT:
            if self.snake.direction.x != -1:
                self.snake.direction = Vector2(1, 0)

    def game_over(self):
        pygame.quit()
        sys.exit()

    def play(self):
        SCREEN_UPDATE = pygame.USEREVENT
        pygame.time.set_timer(SCREEN_UPDATE, 150)

        while True:
            for event in pygame.event.get():
                # izadji ako je pritisnuto dugme
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == SCREEN_UPDATE:
                    self.update()
                if event.type == pygame.KEYDOWN:
                    self.key_events(event)

            # boji ekran RGB = (175, 210, 70)
            self.screen.fill(self.settings.screen_color)
            self.draw_elements()

            pygame.display.update()

            self.clock.tick(60)  # fps = 60


if __name__ == '__main__':
    game = SnakeGame()
    game.play()
