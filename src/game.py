import pygame
from pygame.locals import *
from sys import exit

class Game:
    def __init__(self):
        pygame.init()
        self.info_tela = pygame.display.Info()
        self.largura, self.altura = self.info_tela.current_w, self.info_tela.current_h
        pygame.display.set_caption("Sustentável e Não Sustentável")
        self.tela_jogo = pygame.display.set_mode((self.largura, self.altura), pygame.SCALED)
        self.imagem_jogo = pygame.image.load("assets/telas/JOGO_CIDADE_SUSTENTÁVEL_E_NÃO_SUSTENTÁVEL_MAIN.png").convert_alpha()
        self.imagem_ods_1_sustentavel = pygame.image.load("assets/figuras/ODS_1/ODS_1_Sustentavel.png")
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
                    if event.button == 1:
                        self.mouse_x, self.mouse_y = event.pos
                        print(f"x: {self.mouse_x}, y: {self.mouse_y}")

            self.imagem_jogo = pygame.transform.smoothscale(self.imagem_jogo, (self.largura, self.altura))
            self.tela_jogo.blit(self.imagem_jogo, (0, 0))
            self.tela_jogo.blit(self.imagem_ods_1_sustentavel, (628, 191))

            pygame.display.flip()