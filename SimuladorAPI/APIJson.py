import json
from types import SimpleNamespace

from SimuladorAPI.Ativador import ativador_global
from SimuladorAPI.GerenciadorPartidas import gerenciador_partidas


class APIJsonSimulada:
    """Camada de transporte JSON para simular comunicação cliente-servidor."""

    def __init__(self):
        self._rotas = {
            "pareamento.entrar_na_fila": self._pareamento_entrar_na_fila,
            "pareamento.atualizar": self._pareamento_atualizar,
            "pareamento.cancelar_fila": self._pareamento_cancelar_fila,
            "pareamento.registrar_saida": self._pareamento_registrar_saida,
            "pareamento.simular_rodada": self._pareamento_simular_rodada,
            "pareamento.simular_partida": self._pareamento_simular_partida,
            "pareamento.estado_partida": self._pareamento_estado_partida,
            "estrategista.sincronizar": self._estrategista_sincronizar,
            "estrategista.definir_ping": self._estrategista_definir_ping,
            "estrategista.comprar_loja": self._estrategista_comprar_loja,
            "estrategista.roletar": self._estrategista_roletar,
            "estrategista.vender_banco": self._estrategista_vender_banco,
            "estrategista.posicionar_banco": self._estrategista_posicionar_banco,
            "estrategista.alocar_sinergia": self._estrategista_alocar_sinergia,
            "estrategista.desbloquear_slot": self._estrategista_desbloquear_slot,
            "estrategista.banco_para_mapa": self._estrategista_banco_para_mapa,
            "estrategista.mapa_para_banco": self._estrategista_mapa_para_banco,
            "estrategista.mapa_para_mapa": self._estrategista_mapa_para_mapa,
            "estrategista.registrar_fim_batalha": self._estrategista_registrar_fim_batalha,
        }

    def enviar(self, rota, payload):
        payload_json = json.dumps(payload, ensure_ascii=False, default=self._serializar_objeto)
        payload_dict = json.loads(payload_json)
        handler = self._rotas.get(rota)
        if handler is None:
            return json.loads(json.dumps({"ok": False, "erro": f"rota_desconhecida:{rota}"}, ensure_ascii=False))

        resposta = handler(payload_dict)
        return json.loads(json.dumps(resposta, ensure_ascii=False))

    @staticmethod
    def _serializar_objeto(obj):
        if hasattr(obj, "para_json"):
            return obj.para_json()
        if hasattr(obj, "espelho"):
            return obj.espelho()
        if hasattr(obj, "__dict__"):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        return str(obj)

    def _obj(self, payload, chave="partida"):
        valor = payload.get(chave)
        if chave != "partida" or not isinstance(valor, dict):
            return valor

        jogadores = [SimpleNamespace(**j) for j in valor.get("jogadores", []) if isinstance(j, dict)]
        dados = dict(valor)
        dados["jogadores"] = jogadores
        return SimpleNamespace(**dados)

    def _pareamento_entrar_na_fila(self, payload):
        return gerenciador_partidas.entrar_na_fila(self._obj(payload, "jogador"), payload.get("set_escolhido"))

    def _pareamento_atualizar(self, payload):
        return gerenciador_partidas.atualizar_pareamento(set_escolhido=payload.get("set_escolhido"))

    def _pareamento_cancelar_fila(self, payload):
        return gerenciador_partidas.cancelar_busca_fila(payload.get("set_escolhido"), payload.get("player_id"))

    def _pareamento_registrar_saida(self, payload):
        return gerenciador_partidas.registrar_saida_da_partida(payload.get("partida_id"), payload.get("player_id"))

    def _pareamento_simular_rodada(self, payload):
        return gerenciador_partidas.simular_rodada(payload.get("partida_id"))

    def _pareamento_simular_partida(self, payload):
        return gerenciador_partidas.simular_partida_completa(payload.get("partida_id"), max_rodadas=payload.get("max_rodadas", 100))

    def _pareamento_estado_partida(self, payload):
        return gerenciador_partidas.obter_estado_partida(payload.get("partida_id"))

    def _estrategista_sincronizar(self, payload):
        partida = self._obj(payload)
        player_local_id = payload.get("player_local_id", "local-1")
        ativador_global.sincronizar_partida(partida, player_local_id=player_local_id)
        return {
            "ok": True,
            "partida_id": getattr(partida, "partida_id", None),
            "snapshot": ativador_global.snapshot_partida(partida),
        }

    def _estrategista_definir_ping(self, payload):
        ativador_global.definir_ping(payload.get("ping_ms", 35))
        return {"ok": True}

    @staticmethod
    def _resposta_acao(ok, motivo, partida=None):
        resposta = {"ok": bool(ok), "motivo": motivo}
        if partida is not None:
            resposta["snapshot"] = ativador_global.snapshot_partida(partida)
        return resposta

    def _estrategista_comprar_loja(self, payload):
        partida = self._obj(payload)
        ok, motivo = ativador_global.comprar_carta_loja(partida, payload.get("player_id"), payload.get("indice_loja", -1))
        return self._resposta_acao(ok, motivo, partida if ok else None)

    def _estrategista_roletar(self, payload):
        partida = self._obj(payload)
        ok, motivo = ativador_global.roletar_loja(partida, payload.get("player_id"))
        return self._resposta_acao(ok, motivo, partida if ok else None)

    def _estrategista_vender_banco(self, payload):
        partida = self._obj(payload)
        ok, motivo = ativador_global.vender_do_banco(partida, payload.get("player_id"), payload.get("indice_banco", -1))
        return self._resposta_acao(ok, motivo, partida if ok else None)

    def _estrategista_posicionar_banco(self, payload):
        partida = self._obj(payload)
        ok, motivo = ativador_global.posicionar_do_banco(
            partida,
            payload.get("player_id"),
            payload.get("indice_banco", -1),
            payload.get("q", 0),
            payload.get("r", 0),
        )
        return self._resposta_acao(ok, motivo, partida if ok else None)

    def _estrategista_alocar_sinergia(self, payload):
        partida = self._obj(payload)
        ok, motivo = ativador_global.alocar_cartas_sinergia(
            partida,
            payload.get("player_id"),
            payload.get("card_uids", []),
            alvo_grupo_id=payload.get("alvo_grupo_id"),
        )
        return self._resposta_acao(ok, motivo, partida if ok else None)

    def _estrategista_desbloquear_slot(self, payload):
        partida = self._obj(payload)
        ok, motivo = ativador_global.desbloquear_slot_mapa(partida, payload.get("player_id"), payload.get("slot_id", -1))
        return self._resposta_acao(ok, motivo, partida if ok else None)

    def _estrategista_banco_para_mapa(self, payload):
        partida = self._obj(payload)
        ok, motivo = ativador_global.mover_banco_para_mapa(
            partida,
            payload.get("player_id"),
            payload.get("indice_banco", -1),
            payload.get("slot_id", -1),
        )
        return self._resposta_acao(ok, motivo, partida if ok else None)

    def _estrategista_mapa_para_banco(self, payload):
        partida = self._obj(payload)
        ok, motivo = ativador_global.mover_mapa_para_banco(partida, payload.get("player_id"), payload.get("slot_id", -1))
        return self._resposta_acao(ok, motivo, partida if ok else None)

    def _estrategista_mapa_para_mapa(self, payload):
        partida = self._obj(payload)
        ok, motivo = ativador_global.mover_mapa_para_mapa(
            partida,
            payload.get("player_id"),
            payload.get("slot_origem_id", -1),
            payload.get("slot_destino_id", -1),
        )
        return self._resposta_acao(ok, motivo, partida if ok else None)

    def _estrategista_registrar_fim_batalha(self, payload):
        partida = self._obj(payload)
        ok, motivo = ativador_global.registrar_fim_batalha(partida, payload.get("player_id"))
        return self._resposta_acao(ok, motivo, partida if ok else None)


api_json_global = APIJsonSimulada()
