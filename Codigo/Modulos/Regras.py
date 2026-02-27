from copy import deepcopy
from importlib import import_module


REGRAS_PARTIDA_PADRAO = {
    "tempo_entre_combates_ms": 40000,
    "trilha_batalhas": [
        {"tipo": "normal", "resultado": None},
        {"tipo": "augment", "resultado": None},
        {"tipo": "normal", "resultado": None},
        {"tipo": "normal", "resultado": None},
        {"tipo": "augment", "resultado": None},
        {"tipo": "normal", "resultado": None},
        {"tipo": "normal", "resultado": None},
        {"tipo": "augment", "resultado": None},
        {"tipo": "normal", "resultado": None},
    ],
    "custo_por_raridade": {
        "comum": 1,
        "incomum": 2,
        "raro": 3,
        "epico": 4,
        "lendario": 5,
        "mitico": 6,
    },
    "quantidade_estoque_por_raridade": {
        "comum": 12,
        "incomum": 11,
        "raro": 9,
        "epico": 8,
        "lendario": 5,
        "mitico": 4,
    },
    "raridades_bloqueadas_banco_inicial": ["epico", "lendario", "mitico"],
    "chances_loja_por_slots": {
        1: {"comum": 80, "incomum": 15, "raro": 5, "epico": 0, "lendario": 0, "mitico": 0},
        3: {"comum": 60, "incomum": 30, "raro": 9, "epico": 1, "lendario": 0, "mitico": 0},
        4: {"comum": 40, "incomum": 45, "raro": 12, "epico": 3, "lendario": 0, "mitico": 0},
        5: {"comum": 30, "incomum": 50, "raro": 15, "epico": 5, "lendario": 0, "mitico": 0},
        6: {"comum": 25, "incomum": 40, "raro": 25, "epico": 8, "lendario": 2, "mitico": 0},
        7: {"comum": 22, "incomum": 28, "raro": 35, "epico": 12, "lendario": 3, "mitico": 0},
        8: {"comum": 20, "incomum": 25, "raro": 30, "epico": 18, "lendario": 5, "mitico": 2},
        9: {"comum": 15, "incomum": 18, "raro": 26, "epico": 25, "lendario": 10, "mitico": 6},
        10: {"comum": 12, "incomum": 15, "raro": 20, "epico": 25, "lendario": 20, "mitico": 8},
        11: {"comum": 10, "incomum": 12, "raro": 16, "epico": 22, "lendario": 25, "mitico": 15},
        12: {"comum": 8, "incomum": 10, "raro": 12, "epico": 20, "lendario": 30, "mitico": 20},
    },
}


def _mesclar_dicts(base, sobrescrita):
    for chave, valor in sobrescrita.items():
        if isinstance(valor, dict) and isinstance(base.get(chave), dict):
            _mesclar_dicts(base[chave], valor)
        else:
            base[chave] = deepcopy(valor)


def carregar_regras_partida(set_escolhido):
    regras = deepcopy(REGRAS_PARTIDA_PADRAO)
    nome_set = str(set_escolhido or "BrawlStars")

    try:
        modulo_mecanicas = import_module(f"Sets.{nome_set}.Codigo.Mecanicas")
    except ModuleNotFoundError:
        return regras

    if hasattr(modulo_mecanicas, "REGRAS_PARTIDA"):
        _mesclar_dicts(regras, getattr(modulo_mecanicas, "REGRAS_PARTIDA"))

    if hasattr(modulo_mecanicas, "configurar_regras"):
        regras_customizadas = modulo_mecanicas.configurar_regras(deepcopy(regras))
        if isinstance(regras_customizadas, dict):
            _mesclar_dicts(regras, regras_customizadas)

    return regras
