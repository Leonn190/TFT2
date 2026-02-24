import math
import pygame

GerouSurface = False
surface = None


def Clarear(tela, Info, cor=(0, 0, 0), velocidade=3):
    """
    Clareia gradualmente a tela, reduzindo Info["Escuro"] até 0.
    Deve ser chamada a cada frame dentro do loop principal.
    """
    if Info["Escuro"] > 0:
        Info["Escuro"] -= velocidade
        if Info["Escuro"] < 0:
            Info["Escuro"] = 0

        alpha = int((Info["Escuro"] / 100) * 255)
        camada = pygame.Surface(tela.get_size()).convert_alpha()
        camada.fill((*cor, alpha))
        tela.blit(camada, (0, 0))


def Escurecer(tela, Info, cor=(0, 0, 0), velocidade=3, fps=100):
    """
    Escurece a tela até Info["Escuro"] chegar a 100.
    Possui seu próprio loop bloqueante.
    """
    clock = pygame.time.Clock()
    largura, altura = tela.get_size()

    while Info["Escuro"] < 100:
        Info["Escuro"] += velocidade
        if Info["Escuro"] > 100:
            Info["Escuro"] = 100

        alpha = int((Info["Escuro"] / 100) * 255)
        camada = pygame.Surface((largura, altura)).convert_alpha()
        camada.fill((*cor, alpha))

        tela.blit(camada, (0, 0))
        pygame.display.update()
        clock.tick(fps)


def FecharIris(tela, Info, cor=(0, 0, 0), velocidade=3, fps=100, borda_suave=0):
    """
    Transição 'iris close': escuro avança das bordas até o centro, deixando um
    círculo de clareza que encolhe até 0.
    - Usa Info["Escuro"] de 0 a 100 (incrementa até 100).
    - velocidade: quanto Info["Escuro"] sobe por frame (como em Escurecer).
    - borda_suave: largura (px) da transição suave na borda do círculo (0 = dura).
    """
    clock = pygame.time.Clock()
    w, h = tela.get_size()
    cx, cy = w // 2, h // 2

    max_radius = int(math.hypot(w * 0.5, h * 0.5))

    if "Escuro" not in Info:
        Info["Escuro"] = 0

    while Info["Escuro"] < 100:
        Info["Escuro"] += velocidade
        if Info["Escuro"] > 100:
            Info["Escuro"] = 100

        t = Info["Escuro"] / 100.0
        r = max(0, int(round(max_radius * (1.0 - t))))

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((*cor, 255))

        pygame.draw.circle(overlay, (0, 0, 0, 0), (cx, cy), r)

        if borda_suave > 0 and r > 0:
            steps = max(4, min(24, borda_suave // 2))
            for i in range(1, steps + 1):
                rr = r + i
                a = int(200 * (i / steps))
                pygame.draw.circle(overlay, (*cor, a), (cx, cy), rr, width=1)

        tela.blit(overlay, (0, 0))
        pygame.display.update()
        clock.tick(fps)


def AplicarClaridade(tela, claridade):
    global GerouSurface, surface

    if GerouSurface is False or surface is None or surface.get_size() != tela.get_size():
        surface = pygame.Surface(tela.get_size())
        surface = surface.convert_alpha()
        GerouSurface = True

    if claridade == 75:
        return

    if claridade < 75:
        intensidade = int((75 - claridade) / 50 * 50)
        surface.fill((0, 0, 0, intensidade))
    else:
        intensidade = int((claridade - 75) / 25 * 70)
        surface.fill((255, 255, 255, intensidade))

    tela.blit(surface, (0, 0))


def DesenharFPS(tela, relogio, config):
    if not config.get("MostrarFPS", False):
        return

    fonte = pygame.font.Font(None, 28)
    fps = int(relogio.get_fps())
    texto = fonte.render(f"FPS: {fps}", True, (255, 255, 255))
    tela.blit(texto, (10, 10))
