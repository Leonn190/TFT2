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
        }

    def obter(self, campo, valor_padrao=None):
        return getattr(self, campo, valor_padrao)
