import os
import time

try:
    from pypresence import Presence
except ImportError:  # pypresence é opcional
    Presence = None


class DiscordPresence:
    """Controla Rich Presence do Discord sem quebrar o jogo quando indisponível."""

    def __init__(self, client_id=None):
        self.client_id = str(client_id or os.getenv("DISCORD_CLIENT_ID", "")).strip()
        self.rpc = None
        self.ativo = False
        self.inicio_sessao = int(time.time())
        self.ultimo_payload = None
        self.ultimo_update_ts = 0.0
        self.intervalo_minimo_s = 2.0

    def conectar(self):
        if self.ativo:
            return True
        if Presence is None or not self.client_id:
            return False

        try:
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            self.ativo = True
            return True
        except Exception:
            self.rpc = None
            self.ativo = False
            return False

    def desconectar(self):
        if not self.rpc:
            return
        try:
            self.rpc.clear()
            self.rpc.close()
        except Exception:
            pass
        finally:
            self.rpc = None
            self.ativo = False

    def atualizar(self, details, state, large_image="tft2", large_text="TFT2", small_image=None, small_text=None, force=False):
        if not self.ativo and not self.conectar():
            return

        payload = {
            "details": str(details)[:128],
            "state": str(state)[:128],
            "start": self.inicio_sessao,
            "large_image": large_image,
            "large_text": large_text,
        }
        if small_image:
            payload["small_image"] = small_image
        if small_text:
            payload["small_text"] = small_text

        agora = time.time()
        if not force and payload == self.ultimo_payload and (agora - self.ultimo_update_ts) < self.intervalo_minimo_s:
            return

        try:
            self.rpc.update(**payload)
            self.ultimo_payload = payload
            self.ultimo_update_ts = agora
        except Exception:
            self.ativo = False

    def atualizar_menu(self, modo="base"):
        textos = {
            "base": "No menu principal",
            "config": "Ajustando configurações",
            "escolha_set": "Escolhendo sets",
            "pareamento": "Procurando partida",
        }
        self.atualizar("No menu", textos.get(modo, "Navegando"), small_image="menu", small_text="Menu")

    def atualizar_estrategista(self, partida, jogador, indice_batalha=0, tempo_restante_ms=0):
        if partida is None or jogador is None:
            self.atualizar("Planejamento", "Organizando o tabuleiro")
            return

        rodada = int(indice_batalha) + 1
        segundos = max(0, int(tempo_restante_ms / 1000))
        set_nome = getattr(jogador, "set_escolhido", "Set desconhecido")
        self.atualizar(
            details=f"Planejando rodada {rodada}",
            state=f"{jogador.nome} | Ouro: {jogador.ouro} | Vida: {jogador.vida} | {segundos}s",
            large_text=f"Set: {set_nome}",
            small_image="strategy",
            small_text="Fase de planejamento",
        )

    def atualizar_batalha(self, jogador, inimigo=None):
        if jogador is None:
            self.atualizar("Em combate", "Assistindo batalha")
            return

        if inimigo is not None:
            state = f"{jogador.nome} vs {inimigo.nome}"
        else:
            state = f"{jogador.nome} em combate"

        self.atualizar(
            details="Em batalha",
            state=state,
            small_image="battle",
            small_text="Fase de combate",
        )

