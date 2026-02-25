class Personagem:
    def __init__(self, dados):
        self.id = dados.get("id")
        self.uid = dados.get("uid")
        self.nome = dados.get("nome", "Desconhecido")
        self.sinergia = dados.get("sinergia", "-")
        self.sinergia_secundaria = dados.get("sinergia_secundaria")
        self.custo = int(dados.get("custo", 1))
        self.raridade = dados.get("raridade", "comum")
        self.imagem = dados.get("imagem")

        self.vida = self._normalizar_int(dados, "vida", "Vida", padrao=100)
        self.atk = self._normalizar_int(dados, "atk", "Atk", padrao=0)
        self.spd = self._normalizar_int(dados, "spd", "SpD", padrao=0)
        self.spa = self._normalizar_int(dados, "spa", "SpA", padrao=0)
        self.vel = self._normalizar_int(dados, "vel", "Vel", padrao=0)
        self.defesa = self._normalizar_int(dados, "def", "Def", padrao=0)

    @staticmethod
    def _normalizar_int(dados, *campos, padrao=0):
        for campo in campos:
            valor = dados.get(campo)
            if valor in (None, "", "-"):
                continue
            try:
                return int(float(valor))
            except (TypeError, ValueError):
                continue
        return padrao

    @classmethod
    def de_dict(cls, dados):
        return cls(dados)

    def para_dict(self):
        return {
            "id": self.id,
            "uid": self.uid,
            "nome": self.nome,
            "sinergia": self.sinergia,
            "sinergia_secundaria": self.sinergia_secundaria,
            "custo": self.custo,
            "raridade": self.raridade,
            "imagem": self.imagem,
            "vida": self.vida,
            "atk": self.atk,
            "spd": self.spd,
            "spa": self.spa,
            "vel": self.vel,
            "def": self.defesa,
        }

    def obter(self, campo, valor_padrao=None):
        return getattr(self, campo, valor_padrao)
