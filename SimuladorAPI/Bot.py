import random
from copy import deepcopy


class Player:
    CATEGORIA_PLAYER = "player"
    CATEGORIA_SIMULADO = "simulado"
    CATEGORIA_BOT = "bot"

    def __init__(self, player_id, nome, set_escolhido=None, is_bot=False, categoria=None):
        self.player_id = player_id
        self.nome = nome
        self.set_escolhido = set_escolhido
        self.is_bot = is_bot
        self.categoria = categoria or (self.CATEGORIA_BOT if is_bot else self.CATEGORIA_SIMULADO)

    def para_json(self):
        return {
            "player_id": self.player_id,
            "nome": self.nome,
            "set_escolhido": self.set_escolhido,
            "is_bot": self.is_bot,
            "categoria": self.categoria,
        }


class Bot(Player):
    def __init__(self, player_id, nome, set_escolhido=None):
        super().__init__(player_id=player_id, nome=nome, set_escolhido=set_escolhido, is_bot=True, categoria=Player.CATEGORIA_BOT)

    @staticmethod
    def gerar_loja(catalogo, quantidade=5):
        if not catalogo:
            return []
        return [deepcopy(random.choice(catalogo)) for _ in range(quantidade)]

    @staticmethod
    def _sinergias_carta(carta):
        if not isinstance(carta, dict):
            return []
        sinergias = []
        for campo in ("sinergia", "sinergia_secundaria", "sinergia_terciaria", "sinergia_quaternaria"):
            valor = carta.get(campo)
            if valor and valor != "-":
                sinergias.append(str(valor))
        for valor in carta.get("sinergias", []):
            if valor and valor != "-":
                sinergias.append(str(valor))
        return sinergias

    @classmethod
    def _pontuacao_sinergia(cls, carta, sinergias_atuais):
        pontuacao = 0
        for sinergia in cls._sinergias_carta(carta):
            qtd = sinergias_atuais.get(sinergia, 0)
            pontuacao += 8 if qtd == 1 else 4 if qtd >= 2 else 2
        return pontuacao

    def _sinergias_atuais(self, estado):
        out = {}
        for slot in estado.get("mapa", []):
            carta = slot.get("carta")
            if carta is None:
                continue
            for sinergia in self._sinergias_carta(carta):
                out[sinergia] = out.get(sinergia, 0) + 1
        return out

    def jogar_turno(self, ativador, partida, player_id):
        estado = ativador._partidas[ativador._chave(partida)]["jogadores"].get(player_id)
        if estado is None:
            return False, "jogador_inexistente", False

        if not estado.get("loja"):
            ativador.roletar_loja(partida, player_id, custo=0)

        acoes = []
        if estado.get("banco") and any(s.get("desbloqueado") and s.get("carta") is None for s in estado.get("mapa", [])):
            acoes.append((45, "colocar"))
        if estado.get("loja") and len(estado.get("banco", [])) < 10:
            acoes.append((14, "comprar"))
        if estado.get("ouro", 0) >= 2:
            acoes.append((10, "roletar"))
        if estado.get("banco") and estado.get("ouro", 0) <= 8:
            acoes.append((4, "vender"))
        if any((not s.get("desbloqueado")) and s.get("custo_desbloqueio") and estado.get("ouro", 0) >= s.get("custo_desbloqueio", 0) and ativador._slot_pode_desbloquear(estado["mapa"], s) for s in estado.get("mapa", [])):
            acoes.append((8, "slot"))
        acoes.append((10, "upar"))

        while acoes:
            _, acao = random.choices(acoes, weights=[a[0] for a in acoes], k=1)[0]
            if acao == "colocar":
                slot = next((s for s in estado["mapa"] if s.get("desbloqueado") and s.get("carta") is None), None)
                sin = self._sinergias_atuais(estado)
                idx = max(range(len(estado["banco"])), key=lambda i: self._pontuacao_sinergia(estado["banco"][i], sin))
                ok, motivo = ativador.mover_banco_para_mapa(partida, player_id, idx, slot.get("slot_id", 0)) if slot else (False, "sem_slot")
                if ok:
                    return True, "colocar", False
            elif acao == "comprar":
                sin = self._sinergias_atuais(estado)
                ids = {s.get("carta", {}).get("id") for s in estado.get("mapa", []) if s.get("carta")}
                candidatos = []
                for i, carta in enumerate(estado.get("loja", [])):
                    custo = int(carta.get("custo", 999))
                    if custo > estado.get("ouro", 0):
                        continue
                    score = self._pontuacao_sinergia(carta, sin) + (6 if carta.get("id") in ids else 0)
                    candidatos.append((score, i))
                if candidatos:
                    idx = sorted(candidatos, reverse=True)[0][1]
                    ok, _ = ativador.comprar_carta_loja(partida, player_id, idx)
                    if ok:
                        return True, "comprar", False
            elif acao == "roletar":
                ok, _ = ativador.roletar_loja(partida, player_id, custo=2)
                if ok:
                    return True, "roletar", True
            elif acao == "vender":
                ok, _ = ativador.vender_do_banco(partida, player_id, len(estado["banco"]) - 1)
                if ok:
                    return True, "vender", False
            elif acao == "slot":
                slot = next((s for s in estado["mapa"] if (not s.get("desbloqueado")) and s.get("custo_desbloqueio") and estado.get("ouro", 0) >= s.get("custo_desbloqueio", 0) and ativador._slot_pode_desbloquear(estado["mapa"], s)), None)
                ok, _ = ativador.desbloquear_slot_mapa(partida, player_id, slot.get("slot_id", -1)) if slot else (False, "sem_slot")
                if ok:
                    return True, "slot", False
            elif acao == "upar":
                ok, _ = ativador.aumentar_nivel_personagem(partida, player_id)
                if ok:
                    return True, "upar", True

            acoes = [a for a in acoes if a[1] != acao]

        return False, "sem_acao_valida", False
