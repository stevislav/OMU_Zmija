
import pygame
import sys
import numpy as np
import matplotlib.pyplot as plt 

from pygame.math import Vector2
from settings import Settings
from snake import Snake
from fruit import Fruit
from snake_game import SnakeGame


class Agent:
    def __init__(self):
        '''
        Stanja:
            0. Nagrada ispred
            1. Nagrada iza
            2. Nagrada desno
            3. Nagrada levo
            
            4. Prepreka pravo
            5. Prepreka desno
            6. Prepreka levo
        '''
        # Broj stanja 2 ** 7
        self.stanja = 128

        '''
        Akcije:
            0: Ne radi nista
            1: Skreni levo
            2: Skreni desno
        '''
        self.akcije = 3

        self.snake_game = SnakeGame()
        self.akcija_vrednost_funkcija = np.zeros((self.stanja, self.akcije))

    def uzmi_stanje(self):
        stanje_0 = Vector2.dot(self.snake_game.snake.direction, self.snake_game.fruit.position - self.snake_game.snake.body[0]) > 0
        stanje_1 = Vector2.dot(self.snake_game.snake.direction, self.snake_game.fruit.position - self.snake_game.snake.body[0]) < 0

        stanje_2 = Vector2.cross(self.snake_game.snake.direction, self.snake_game.fruit.position - self.snake_game.snake.body[0]) < 0
        stanje_3 = Vector2.cross(self.snake_game.snake.direction, self.snake_game.fruit.position - self.snake_game.snake.body[0]) > 0

        stanje_4 = 0
        stanje_5 = 0
        stanje_6 = 0
        if self.snake_game.snake.direction.y == 0:
            prepreka_napred_x = self.snake_game.snake.body[0].x + self.snake_game.snake.direction.x
            prepreka_napred_y = self.snake_game.snake.body[0].y

            prepreka_desno_x = self.snake_game.snake.body[0].x
            prepreka_desno_y = self.snake_game.snake.body[0].y + self.snake_game.snake.direction.x

            prepreka_levo_x = self.snake_game.snake.body[0].x
            prepreka_levo_y = self.snake_game.snake.body[0].y - self.snake_game.snake.direction.x

        elif self.snake_game.snake.direction.x == 0:
            prepreka_napred_x = self.snake_game.snake.body[0].x
            prepreka_napred_y = self.snake_game.snake.body[0].y + self.snake_game.snake.direction.y

            prepreka_desno_x = self.snake_game.snake.body[0].x - self.snake_game.snake.direction.y
            prepreka_desno_y = self.snake_game.snake.body[0].y

            prepreka_levo_x = self.snake_game.snake.body[0].x + self.snake_game.snake.direction.y
            prepreka_levo_y = self.snake_game.snake.body[0].y

        for prepreka in self.snake_game.snake.body[1:]:
            if prepreka.x == prepreka_napred_x and prepreka.y == prepreka_napred_y:
                stanje_4 = 1

            if prepreka.x == prepreka_desno_x and prepreka.y == prepreka_desno_y:
                stanje_5 = 1

            if prepreka.x == prepreka_levo_x and prepreka.y == prepreka_levo_y:
                stanje_6 = 1

        if prepreka_napred_x == -1 or prepreka_napred_x == self.snake_game.settings.cell_number:
            stanje_4 = 1

        if prepreka_desno_y == -1 or prepreka_desno_y == self.snake_game.settings.cell_number:
            stanje_5 = 1

        if prepreka_levo_y == -1 or prepreka_levo_y == self.snake_game.settings.cell_number:
            stanje_6 = 1

        return stanje_0 + 2 * stanje_1 + 4 * stanje_2 + 8 * stanje_3 + 16 * stanje_4 + 32 * stanje_5 + 64 * stanje_6

    def epsilon_pohlepno(self, akcija_vrednost_funkcija, stanje, epsilon=0.01):
        if np.random.uniform(low=0.0, high=1.0) < epsilon:
            akcija = np.random.randint(0, self.akcije)
        else:
            akcija = np.random.choice(np.flatnonzero(akcija_vrednost_funkcija[stanje, :] == akcija_vrednost_funkcija[stanje, :].max()))

        return akcija

    def azuriraj_smer(self, akcija):
        if akcija == 0:
            pass

        elif akcija == 1:
            if self.snake_game.snake.direction.x == 1:
                self.snake_game.snake.direction = Vector2(0, 1)

            elif self.snake_game.snake.direction.x == -1:
                self.snake_game.snake.direction = Vector2(0, -1)

            elif self.snake_game.snake.direction.y == 1:
                self.snake_game.snake.direction = Vector2(-1, 0)

            elif self.snake_game.snake.direction.y == -1:
                self.snake_game.snake.direction = Vector2(1, 0)

        elif akcija == 2:
            if self.snake_game.snake.direction.x == 1:
                self.snake_game.snake.direction = Vector2(0, -1)

            elif self.snake_game.snake.direction.x == -1:
                self.snake_game.snake.direction = Vector2(0, 1)

            elif self.snake_game.snake.direction.y == 1:
                self.snake_game.snake.direction = Vector2(1, 0)

            elif self.snake_game.snake.direction.y == -1:
                self.snake_game.snake.direction = Vector2(-1, 0)

    def izlaz(self):
        # izlaz ako udari u okvir
        if not 0 <= self.snake_game.snake.body[0].x < self.snake_game.settings.cell_number:
            return True
        if not 0 <= self.snake_game.snake.body[0].y < self.snake_game.settings.cell_number:
            return True

        # izlaz ako udari u sebe
        for block in self.snake_game.snake.body[1:]:
            if block == self.snake_game.snake.body[0]:
                return True

        return False

    def rl_epizoda(self, gamma=0.9, epsilon=0.01, alpha=0.05):
        SCREEN_UPDATE = pygame.USEREVENT
        pygame.time.set_timer(SCREEN_UPDATE, 150)

        '''Nagrade:
            Ide ka jabuci +5
            Ide od jakuke -5
            Jede jabuku +500
            Udari u prepreku -1000
            
        '''
        ka_jabuci = +5
        od_jabuke = -5
        jedi_jabuku = +500
        slupaj = -1000

        while True:
            trenutno_stanje = self.uzmi_stanje()
            akcija = self.epsilon_pohlepno(self.akcija_vrednost_funkcija, trenutno_stanje, epsilon=epsilon)
            self.azuriraj_smer(akcija)

            nagrada = od_jabuke

            stara_distanca = Vector2.magnitude(self.snake_game.snake.body[0] - self.snake_game.fruit.position)

            if self.snake_game.snake.new_block == True:
                nagrada = jedi_jabuku

            self.snake_game.snake.move_snake()
        
            sledece_stanje = self.uzmi_stanje()

            nova_distanca = Vector2.magnitude(self.snake_game.snake.body[0] - self.snake_game.fruit.position)
            if nova_distanca < stara_distanca:
                nagrada = ka_jabuci

            self.snake_game.check_collision()

            if self.izlaz() == True:
                nagrada = slupaj

            greska = nagrada + gamma * np.max(self.akcija_vrednost_funkcija[sledece_stanje, :]) - self.akcija_vrednost_funkcija[trenutno_stanje, akcija]
            self.akcija_vrednost_funkcija[trenutno_stanje, akcija] += alpha * greska

            if self.izlaz() == True:
                break

            # boji ekran = (175, 210, 70)
            self.snake_game.screen.fill(self.snake_game.settings.screen_color)
            self.snake_game.draw_elements()
            pygame.display.update()

            #PROMENA BRZINE SIMULACIJE
            self.snake_game.clock.tick(180)

        rezultat = len(self.snake_game.snake.body) - 3

        self.snake_game.snake.reset()
        self.snake_game.fruit.randomize()

        return rezultat

if __name__ == '__main__':

    rl_napredak = []
    epizode = 100
    
    rl_agent = Agent()
    rl_akcija_vrednost_funkcija = []
    rl_akcija_vrednost_funkcija.append(np.zeros(rl_agent.akcija_vrednost_funkcija.shape))

    for epizoda in range(epizode):
        epsilon = 0.01 / len(rl_akcija_vrednost_funkcija)
        alpha = 0.5 / len(rl_akcija_vrednost_funkcija)
        rl_rezultat = rl_agent.rl_epizoda(gamma=0.9, epsilon=epsilon, alpha=alpha)
        rl_napredak.append(rl_rezultat)

        nova_akcija_vrednost_funkcija = np.copy(rl_agent.akcija_vrednost_funkcija)
        rl_akcija_vrednost_funkcija.append(nova_akcija_vrednost_funkcija)
        print(len(rl_akcija_vrednost_funkcija) - 1, " ", rl_rezultat)

        print("=======")

    
    plt.plot(rl_napredak)
    plt.xlabel('Epizoda')
    plt.ylabel('Rezultat')

 
    plt.show()