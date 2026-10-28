import pygame

pygame.init()

tela = pygame.display.set_mode((1280, 720))

imagem = pygame.image.load("assets/telas/JOGO_CIDADE_SUSTENTÁVEL_E_NÃO_SUSTENTÁVEL_MAIN.png").convert()
imagem = pygame.transform.scale(imagem, (1280, 720))

rodando = True

while rodando:

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.MOUSEBUTTONDOWN:

            if evento.button == 1:
                print("Posição:", evento.pos)

    tela.blit(imagem, (0, 0))

    # Pega a posição atual do mouse
    x, y = pygame.mouse.get_pos()

    fonte = pygame.font.SysFont(None, 30)

    texto = fonte.render(
        f"X: {x}  Y: {y}",
        True,
        (255, 0, 0)
    )

    tela.blit(texto, (10, 10))

    pygame.display.flip()

pygame.quit()