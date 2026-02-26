from copy import deepcopy


class SimuladoCombate:
    """Simulador de combate instantâneo sem etapa visual."""

    @staticmethod
    def _obter_campo(carta, campo, padrao=None):
        if carta is None:
            return padrao
        if isinstance(carta, dict):
            return carta.get(campo, padrao)
        return getattr(carta, campo, padrao)

    @classmethod
    def _sinergias_carta(cls, carta):
        sinergias = []
        for campo in ("sinergia", "sinergia_secundaria", "sinergia_terciaria", "sinergia_quaternaria"):
            valor = cls._obter_campo(carta, campo)
            if valor and valor != "-":
                sinergias.append(str(valor))

        extras = cls._obter_campo(carta, "sinergias", [])
        if isinstance(extras, (list, tuple)):
            for valor in extras:
                if valor and valor != "-":
                    sinergias.append(str(valor))
        return sinergias

    @classmethod
    def _forca_jogador(cls, estado_jogador):
        cartas = [slot.get("carta") for slot in estado_jogador.get("mapa", []) if slot.get("carta") is not None]
        if not cartas:
            return 0

        forca_base = sum(max(1, int(cls._obter_campo(carta, "custo", 1))) for carta in cartas)
        sinergias = {}
        for carta in cartas:
            for sinergia in cls._sinergias_carta(carta):
                sinergias[sinergia] = sinergias.get(sinergia, 0) + 1

        bonus_sinergia = sum((quantidade - 1) * 2 for quantidade in sinergias.values() if quantidade >= 2)
        bonus_diversidade = len([nome for nome, qtd in sinergias.items() if qtd >= 2])
        bonus_ouro = min(6, int(estado_jogador.get("ouro", 0)) // 20)
        return forca_base + bonus_sinergia + bonus_diversidade + bonus_ouro

    def simular(self, player_a_id, estado_a, player_b_id, estado_b):
        forca_a = self._forca_jogador(estado_a)
        forca_b = self._forca_jogador(estado_b)

        vencedor_id = player_a_id
        perdedor_id = player_b_id
        diferenca = forca_a - forca_b

        if forca_b > forca_a:
            vencedor_id = player_b_id
            perdedor_id = player_a_id
            diferenca = forca_b - forca_a
        elif forca_a == forca_b:
            # Critério determinístico para evitar incongruências entre clientes.
            if str(player_b_id) < str(player_a_id):
                vencedor_id = player_b_id
                perdedor_id = player_a_id
            diferenca = 0

        dano = 4 + max(1, diferenca // 2)
        return {
            "vencedor_id": vencedor_id,
            "perdedor_id": perdedor_id,
            "forca_vencedor": max(forca_a, forca_b),
            "forca_perdedor": min(forca_a, forca_b),
            "diferenca_forca": diferenca,
            "dano": dano,
            "snapshot": deepcopy({
                "forca_a": forca_a,
                "forca_b": forca_b,
            }),
        }
