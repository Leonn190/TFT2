class Personagem:
    def __init__(
        self,
        personagem_id,
        nome,
        raridade,
        custo,
        sinergia,
        sinergia_secundaria=None,
        imagem=None,
        uid=None,
        set_nome="BrawlStars",
    ):
        self.personagem_id = personagem_id
        self.nome = nome
        self.raridade = raridade
        self.custo = int(custo)
        self.sinergia = sinergia
        self.sinergia_secundaria = sinergia_secundaria
        self.imagem = imagem
        self.uid = uid
        self.set_nome = set_nome

    @classmethod
    def de_dicionario(cls, dados):
        return cls(
            personagem_id=dados.get("id"),
            nome=dados.get("nome", "Desconhecido"),
            raridade=dados.get("raridade", "comum"),
            custo=dados.get("custo", 1),
            sinergia=dados.get("sinergia", "-"),
            sinergia_secundaria=dados.get("sinergia_secundaria"),
            imagem=dados.get("imagem"),
            uid=dados.get("uid"),
            set_nome=dados.get("set_nome", "BrawlStars"),
        )

    def para_dicionario(self):
        return {
            "id": self.personagem_id,
            "nome": self.nome,
            "raridade": self.raridade,
            "custo": self.custo,
            "sinergia": self.sinergia,
            "sinergia_secundaria": self.sinergia_secundaria,
            "imagem": self.imagem,
            "uid": self.uid,
            "set_nome": self.set_nome,
        }
