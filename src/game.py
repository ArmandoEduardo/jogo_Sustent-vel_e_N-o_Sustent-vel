import pygame
from pygame.locals import *
from sys import exit
import os
import unicodedata


class Game:
    def __init__(self):
        pygame.init()
        self.info_tela = pygame.display.Info()
        self.largura, self.altura = self.info_tela.current_w, self.info_tela.current_h
        pygame.display.set_caption("Sustentável e Não Sustentável")
        self.tela_jogo = pygame.display.set_mode((self.largura, self.altura), pygame.SCALED)

        # ================= Fundo =================
        self.imagem_jogo = pygame.image.load(
            "assets/telas/JOGO_CIDADE_SUSTENTÁVEL_E_NÃO_SUSTENTÁVEL_MAIN.png"
        ).convert_alpha()
        self.imagem_jogo = pygame.transform.smoothscale(
            self.imagem_jogo, (self.largura, self.altura)
        )

        # ================= Fontes =================
        self.fonte = pygame.font.SysFont("arial", 40, bold=True)
        self.fonte_grande = pygame.font.SysFont("arial", 80, bold=True)

        # ================= Zonas da tela =================
        self.y_inicio_faixa = int(self.altura * 0.87)
        self.y_centro_fila = self.y_inicio_faixa + (self.altura - self.y_inicio_faixa) // 2
        self.x_meio = self.largura // 2

        # ================= Configurações =================
        self.fator_mao = 0.15
        self.fator_fila = 0.10
        self.margem_meio = 0.04
        self.dist_minima_arrasto = 10
        self.limite_fila = 5

        # ================= Estado =================
        self.cenas = self._carregar_cenas("assets/figuras")

        self.fila = []
        self.proximas = []
        self._preparar_fila()

        self.colocadas = []

        self.imagem_mao = None
        self.resp_mao = None
        self.pos_mao = [self.largura // 2, self.altura // 2]

        self.arrastando = False
        self.pos_click_inicial = (0, 0)
        self.offset_x = 0
        self.offset_y = 0

        self.rodar = True
        self.finalizado = False

    def _carregar_cenas(self, pasta):
        cenas = []
        if not os.path.isdir(pasta):
            print(f"[AVISO] Pasta '{pasta}' não encontrada!")
            return cenas
        for raiz, _, arquivos in os.walk(pasta):
            for nome in sorted(arquivos):
                if not nome.lower().endswith((".png", ".jpg", ".jpeg")):
                    continue
                n = nome.lower()
                n_norm = unicodedata.normalize("NFKD", n)
                n_norm = "".join(c for c in n_norm if not unicodedata.combining(c))
                n_norm = n_norm.replace("-", "").replace("_", "").replace(" ", "")

                if "naosustentavel" in n_norm or "insustentavel" in n_norm:
                    resp = "nao_sustentavel"
                elif "sustentavel" in n_norm:
                    resp = "sustentavel"
                else:
                    continue
                cenas.append({"caminho": os.path.join(raiz, nome), "resp": resp})
        return cenas

    def _dimensionar(self, img, fator):
        w, h = img.get_size()
        max_w = self.largura * fator
        max_h = self.altura * fator
        escala = min(max_w / w, max_h / h)
        return pygame.transform.smoothscale(img, (int(w * escala), int(h * escala)))

    def _preparar_fila(self):
        todas = []
        for cena in self.cenas:
            original = pygame.image.load(cena["caminho"]).convert_alpha()
            todas.append({
                "img_fila": self._dimensionar(original, self.fator_fila),
                "img_mao": self._dimensionar(original, self.fator_mao),
                "resp": cena["resp"],
                "rect_fila": pygame.Rect(0, 0, 0, 0),
            })

        self.fila = todas[:self.limite_fila]
        self.proximas = todas[self.limite_fila:]
        self._layout_fila()

    def _reabastecer_fila(self):
        while len(self.fila) < self.limite_fila and self.proximas:
            self.fila.append(self.proximas.pop(0))
        self._layout_fila()

    def _layout_fila(self):
        if not self.fila:
            return
        n = len(self.fila)
        espacamento = self.largura // (n + 1)
        for i, item in enumerate(self.fila):
            cx = espacamento * (i + 1)
            item["rect_fila"] = item["img_fila"].get_rect(
                center=(cx, self.y_centro_fila)
            )

    def _devolver_para_fila(self):
        """Devolve a imagem da mão para a fila."""
        if self.imagem_mao is None:
            return

        item = {
            "img_fila": self._dimensionar(self.imagem_mao, self.fator_fila),
            "img_mao": self.imagem_mao,
            "resp": self.resp_mao,
            "rect_fila": pygame.Rect(0, 0, 0, 0),
        }

        self.fila.insert(0, item)

        # Garante que nunca passe do limite (devolve a última pro backlog)
        if len(self.fila) > self.limite_fila:
            self.proximas.insert(0, self.fila.pop())

        self._layout_fila()

        self.imagem_mao = None
        self.resp_mao = None

    def _pegar_da_fila(self, pos_mouse):
        for i, item in enumerate(self.fila):
            if item["rect_fila"].collidepoint(pos_mouse):
                self.imagem_mao = item["img_mao"]
                self.resp_mao = item["resp"]
                self.pos_mao = [pos_mouse[0], pos_mouse[1]]
                self.fila.pop(i)
                self._reabastecer_fila()
                return True
        return False

    def _pegar_colocada(self, pos_mouse):
        for i in range(len(self.colocadas) - 1, -1, -1):
            item = self.colocadas[i]
            rect = item["imagem"].get_rect(center=item["pos"])
            if rect.collidepoint(pos_mouse):
                item = self.colocadas.pop(i)
                self.imagem_mao = item["imagem"]
                self.resp_mao = item["resp"]
                self.pos_mao = [item["pos"][0], item["pos"][1]]
                return True
        return False

    def _rect_mao(self):
        if self.imagem_mao is None:
            return pygame.Rect(0, 0, 0, 0)
        return self.imagem_mao.get_rect(center=self.pos_mao)

    def _esta_no_meio(self):
        margem = self.largura * self.margem_meio
        return abs(self.pos_mao[0] - self.x_meio) < margem

    def _soltar_imagem(self, movimento_total):
        if self.imagem_mao is None:
            return

        # Se foi um clique muito curto, devolve pra fila
        if movimento_total < self.dist_minima_arrasto:
            self._devolver_para_fila()
            return

        # Se soltou na faixa amarela ou no meio, devolve pra fila
        if self.pos_mao[1] > self.y_inicio_faixa or self._esta_no_meio():
            self._devolver_para_fila()
            return

        # Soltou no lado certo, coloca e fixa
        self.colocadas.append({
            "imagem": self.imagem_mao,
            "pos": tuple(self.pos_mao),
            "resp": self.resp_mao,
        })
        self.imagem_mao = None
        self.resp_mao = None

        if not self.fila and not self.proximas:
            self.finalizado = True

    def _calcular_placar(self):
        acertos = 0
        for item in self.colocadas:
            direita = item["pos"][0] > self.x_meio
            correta = (
                (direita and item["resp"] == "nao_sustentavel") or
                (not direita and item["resp"] == "sustentavel")
            )
            if correta:
                acertos += 1
        return acertos

    def _desenhar_fila(self):
        for item in self.fila:
            self.tela_jogo.blit(item["img_fila"], item["rect_fila"])

    def _desenhar_colocadas(self):
        for item in self.colocadas:
            rect = item["imagem"].get_rect(center=item["pos"])
            self.tela_jogo.blit(item["imagem"], rect)

    def _desenhar_mao(self):
        if self.imagem_mao is None:
            return
        rect = self.imagem_mao.get_rect(center=self.pos_mao)
        self.tela_jogo.blit(self.imagem_mao, rect)

    def _desenhar_final(self):
        overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.tela_jogo.blit(overlay, (0, 0))

        acertos = self._calcular_placar()
        titulo = self.fonte_grande.render("FIM DE JOGO!", True, (255, 255, 255))
        placar = self.fonte.render(
            f"Você acertou {acertos} de {len(self.colocadas)}",
            True, (200, 255, 200)
        )
        dica = self.fonte.render("Pressione ESC para sair", True, (180, 180, 180))

        self.tela_jogo.blit(titulo, titulo.get_rect(center=(self.largura // 2, self.altura // 2 - 120)))
        self.tela_jogo.blit(placar, placar.get_rect(center=(self.largura // 2, self.altura // 2)))
        self.tela_jogo.blit(dica, dica.get_rect(center=(self.largura // 2, self.altura // 2 + 120)))

    def rodando(self):
        while self.rodar:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.rodar = False

                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.rodar = False

                elif not self.finalizado:
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        if self._pegar_colocada(event.pos):
                            self.arrastando = True
                            self.pos_click_inicial = event.pos
                            self.offset_x = self.pos_mao[0] - event.pos[0]
                            self.offset_y = self.pos_mao[1] - event.pos[1]
                            continue

                        if self._pegar_da_fila(event.pos):
                            self.arrastando = True
                            self.pos_click_inicial = event.pos
                            self.offset_x = self.pos_mao[0] - event.pos[0]
                            self.offset_y = self.pos_mao[1] - event.pos[1]
                            continue

                        if self._rect_mao().collidepoint(event.pos):
                            self.arrastando = True
                            self.pos_click_inicial = event.pos
                            self.offset_x = self.pos_mao[0] - event.pos[0]
                            self.offset_y = self.pos_mao[1] - event.pos[1]

                    elif event.type == MOUSEBUTTONUP and event.button == 1 and self.arrastando:
                        self.arrastando = False
                        dx = event.pos[0] - self.pos_click_inicial[0]
                        dy = event.pos[1] - self.pos_click_inicial[1]
                        movimento = (dx * dx + dy * dy) ** 0.5
                        self._soltar_imagem(movimento)

            if self.arrastando and self.imagem_mao is not None:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.pos_mao = [mouse_x + self.offset_x, mouse_y + self.offset_y]

            # ========= Desenho =========
            self.tela_jogo.blit(self.imagem_jogo, (0, 0))
            self._desenhar_colocadas()
            self._desenhar_fila()
            self._desenhar_mao()

            if self.finalizado:
                self._desenhar_final()

            pygame.display.flip()

        pygame.quit()
        exit()