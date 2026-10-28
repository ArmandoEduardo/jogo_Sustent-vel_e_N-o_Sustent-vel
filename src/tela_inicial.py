import pygame
from pygame.locals import *
from sys import exit

class TelaInicial:
    def __init__(self):
        pygame.init()
        self.info_tela = pygame.display.Info()
        self.largura, self.altura = self.info_tela.current_w, self.info_tela.current_h
        pygame.display.set_caption("Sustentável e Não Sustentável")
        self.tela_inicial = pygame.display.set_mode((self.largura, self.altura), pygame.SCALED)
        self.image = pygame.image.load("../assets/telas/JOGO_CIDADE_SUSTENTÁVEL_E_NÃO_SUSTENTÁVEL_TELA_INICIAL.png").convert_alpha()
        self.rodar = True


    def rodando(self):
        while self.rodar:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.rodar = False
                    pygame.quit()
                    exit()

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.rodar = False
                        pygame.quit()
                        exit()

                if event.type == MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if event.button == 1 and mouse_x >= 637 and mouse_x <= 814 and mouse_y >= 386 and mouse_y <= 442:
                        self.rodar = False
                        # pygame.quit()
                        # exit()

            self.image = pygame.transform.smoothscale(self.image, (self.largura, self.altura))
            self.tela_inicial.blit(self.image, (0, 0))

            pygame.display.flip() 