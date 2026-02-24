import pygame
from Codigo.Modulos.GeradoresVisuais import obter_cor, obter_fonte
from Codigo.Prefabs.Barra import BarraArrastavel
from Codigo.Prefabs.Botao import Botao
from ConfigFixa import salvar_configuracoes_fixas


def InicializaTelaConfig(CONFIG):
    return {
        "Barras": {
            "Volume": BarraArrastavel(560, 260, 800, "Volume", CONFIG["Volume"], minimo=0, maximo=1, casas_decimais=2),
            "Claridade": BarraArrastavel(560, 390, 800, "Claridade", CONFIG["Claridade"], minimo=20, maximo=100),
            "FPS": BarraArrastavel(560, 520, 800, "FPS", CONFIG["FPS"], minimo=30, maximo=240),
        },
        "Alavancas": {
            "MostrarFPS": Botao(560, 660, 800, 60, "Mostrar FPS", estilo="alavanca", valor=CONFIG["MostrarFPS"]),
            "MostrarPing": Botao(560, 740, 800, 60, "Mostrar Ping", estilo="alavanca", valor=CONFIG["MostrarPing"]),
            "Mudo": Botao(560, 820, 800, 60, "Mudo", estilo="alavanca", valor=CONFIG["Mudo"]),
        },
        "BotaoCancelar": Botao(560, 930, 280, 70, "Cancelar"),
        "BotaoAplicar": Botao(1080, 930, 280, 70, "Aplicar"),
    }


def TelaConfig(TELA, ESTADOS, CONFIG, INFO, Parametros):
    TELA.fill((16, 24, 36))

    titulo = obter_fonte(56, negrito=True).render("Configurações", True, obter_cor("titulo"))
    TELA.blit(titulo, titulo.get_rect(center=(960, 140)))

    painel = (460, 210, 1000, 830)
    pygame.draw.rect(TELA, (30, 44, 66), painel, border_radius=18)
    pygame.draw.rect(TELA, obter_cor("botao_borda"), painel, width=3, border_radius=18)

    for barra in Parametros["Config"]["Barras"].values():
        barra.desenhar(TELA)

    for alavanca in Parametros["Config"]["Alavancas"].values():
        alavanca.desenhar(TELA)

    Parametros["Config"]["BotaoCancelar"].desenhar(TELA)
    Parametros["Config"]["BotaoAplicar"].desenhar(TELA)


def obter_configuracoes_da_tela(parametros_config):
    return {
        "Volume": parametros_config["Barras"]["Volume"].valor,
        "Claridade": parametros_config["Barras"]["Claridade"].valor,
        "FPS": parametros_config["Barras"]["FPS"].valor,
        "MostrarFPS": parametros_config["Alavancas"]["MostrarFPS"].ativo,
        "MostrarPing": parametros_config["Alavancas"]["MostrarPing"].ativo,
        "Mudo": parametros_config["Alavancas"]["Mudo"].ativo,
    }


def aplicar_configuracoes_em_tempo_real(CONFIG, parametros_config):
    CONFIG.update(obter_configuracoes_da_tela(parametros_config))


def aplicar_configuracoes(CONFIG, parametros_config):
    novas_configs = obter_configuracoes_da_tela(parametros_config)
    CONFIG.update(novas_configs)
    salvar_configuracoes_fixas(novas_configs)
