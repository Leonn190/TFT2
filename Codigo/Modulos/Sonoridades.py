from pathlib import Path

import pygame


_MIXER_DISPONIVEL = False
try:
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    _MIXER_DISPONIVEL = True
except pygame.error:
    _MIXER_DISPONIVEL = False

silencio = False
volume_global = 1.0

_BASE_DIR = Path(__file__).resolve().parents[2]

Sons = {
    "Clique": {"arquivo": "Recursos/Sonoridades/Sons/Clique.wav", "Volume": 0.75},
    "Bloq": {"arquivo": "Recursos/Sonoridades/Sons/Bloq.wav", "Volume": 0.85},
}

Musicas = {
    "Menu1": {
        "arquivo": "Recursos/Sonoridades/Musicas/Menu1.mp3",
        "loop": 0.0,
        "fimloop": None,
    },
    "Menu2": {
        "arquivo": "Recursos/Sonoridades/Musicas/Menu2.mp3",
        "loop": 0.0,
        "fimloop": None,
    },
    "TelaInicio": {
        "arquivo": "Recursos/Audio/Musicas/TelaInicio.ogg",
        "loop": 12.7,
        "fimloop": 110.55,
    },
    "ConfrontoDoVale": {
        "arquivo": "Recursos/Audio/Musicas/ConfrontoDoVale.ogg",
        "loop": 2.34,
        "fimloop": 83.6,
    },
    "ConfrontoDaNeve": {
        "arquivo": "Recursos/Audio/Musicas/ConfrontoDaNeve.ogg",
        "loop": 2.32,
        "fimloop": 83.6,
    },
    "ConfrontoDoMar": {
        "arquivo": "Recursos/Audio/Musicas/ConfrontoDoMar.ogg",
        "loop": 2.27,
        "fimloop": 83.64,
    },
    "ConfrontoDoDeserto": {
        "arquivo": "Recursos/Audio/Musicas/ConfrontoDoDeserto.ogg",
        "loop": 2.33,
        "fimloop": 83.655,
    },
    "ConfrontoDoVulcao": {
        "arquivo": "Recursos/Audio/Musicas/ConfrontoDoVulcao.ogg",
        "loop": 2.34,
        "fimloop": 83.62,
    },
    "ConfrontoDoMagia": {
        "arquivo": "Recursos/Audio/Musicas/ConfrontoDaMagia.ogg",
        "loop": 2.34,
        "fimloop": 83.62,
    },
    "ConfrontoDoPantano": {
        "arquivo": "Recursos/Audio/Musicas/ConfrontoDoPantano.ogg",
        "loop": 2.34,
        "fimloop": 83.62,
    },
    "Vale": {
        "arquivo": "Recursos/Audio/Musicas/Vale.ogg",
        "loop": 3.2,
        "fimloop": 111.9,
    },
    "Neve": {
        "arquivo": "Recursos/Audio/Musicas/Neve.ogg",
        "loop": 4.2,
        "fimloop": 68.35,
    },
    "Deserto": {
        "arquivo": "Recursos/Audio/Musicas/Deserto.ogg",
        "loop": 0.2,
        "fimloop": 87.45,
    },
}

_cache_sons = {}
_musica_atual = None
_musica_inicio_ms = 0

def _clamp(valor, minimo=0.0, maximo=1.0):
    return max(minimo, min(valor, maximo))


def _caminho(arquivo_relativo):
    return _BASE_DIR / arquivo_relativo


def VerificaSonoridade(config):
    global silencio
    global volume_global

    silencio = bool(config.get("Mudo", False))
    volume_global = float(config.get("Volume", 1.0))
    atualizar_volume_musica()


def registrar_som(nome, arquivo, volume=1.0):
    Sons[nome] = {"arquivo": arquivo, "Volume": float(volume)}


def registrar_musica(nome, arquivo, loop=0.0, fimloop=None):
    Musicas[nome] = {"arquivo": arquivo, "loop": float(loop), "fimloop": fimloop}


def tocar(som):
    if not _MIXER_DISPONIVEL or som not in Sons:
        return False

    definicao = Sons[som]
    caminho = _caminho(definicao["arquivo"])
    if not caminho.exists():
        return False

    audio = _cache_sons.get(som)
    if audio is None:
        audio = pygame.mixer.Sound(str(caminho))
        _cache_sons[som] = audio

    volume = definicao["Volume"] * volume_global
    if silencio:
        volume = 0

    audio.set_volume(_clamp(volume))
    audio.play()

    if volume > 1:
        audio2 = pygame.mixer.Sound(str(caminho))
        audio2.set_volume(_clamp(volume - 1))
        audio2.play()

    return True


def tocar_musica(nome, reiniciar=False):
    global _musica_atual
    global _musica_inicio_ms

    if not _MIXER_DISPONIVEL or nome not in Musicas:
        return False

    if _musica_atual == nome and pygame.mixer.music.get_busy() and not reiniciar:
        return True

    definicao = Musicas[nome]
    caminho = _caminho(definicao["arquivo"])
    if not caminho.exists():
        return False

    pygame.mixer.music.load(str(caminho))
    inicio = float(definicao.get("loop", 0.0) or 0.0)
    pygame.mixer.music.play(loops=0, start=max(0.0, inicio))
    _musica_inicio_ms = pygame.time.get_ticks() - int(inicio * 1000)
    _musica_atual = nome
    atualizar_volume_musica()
    return True


def atualizar_volume_musica():
    if not _MIXER_DISPONIVEL:
        return
    volume = 0.0 if silencio else _clamp(volume_global)
    pygame.mixer.music.set_volume(volume)


def parar_musica():
    global _musica_atual
    if not _MIXER_DISPONIVEL:
        return
    pygame.mixer.music.stop()
    _musica_atual = None


def atualizar_musica():
    global _musica_inicio_ms

    if not _MIXER_DISPONIVEL or _musica_atual is None:
        return

    definicao = Musicas.get(_musica_atual, {})
    fimloop = definicao.get("fimloop")
    loop = float(definicao.get("loop", 0.0) or 0.0)

    if fimloop is None:
        if not pygame.mixer.music.get_busy():
            tocar_musica(_musica_atual, reiniciar=True)
        return

    tempo_tocando_s = (pygame.time.get_ticks() - _musica_inicio_ms) / 1000
    if tempo_tocando_s >= float(fimloop):
        pygame.mixer.music.play(loops=0, start=max(0.0, loop))
        _musica_inicio_ms = pygame.time.get_ticks() - int(loop * 1000)
        atualizar_volume_musica()
