import pygame
import random
import sys

from pygame.math import Vector2

from settings import Settings



class Fruit:
    def __init__(self, screen):
        self.settings = Settings()
        self.screen = screen

        # ucitaj sliku jabuke
        self.apple = pygame.image.load('graphics/apple.png').convert_alpha()
        self.randomize()

    def randomize(self):
        # nasumicna x i y koordinata
        self.x = random.randint(0, self.settings.cell_number - 1)
        self.y = random.randint(0, self.settings.cell_number - 1)
        self.position = Vector2(self.x, self.y)

    def draw_fruit(self):
        x_pos = int(self.position.x * self.settings.cell_size)
        y_pos = int(self.position.y * self.settings.cell_size)
        fruit_rect = pygame.Rect(
            x_pos, y_pos, self.settings.cell_size, self.settings.cell_size)

        # crtaj jabuku
        self.screen.blit(self.apple, fruit_rect)
