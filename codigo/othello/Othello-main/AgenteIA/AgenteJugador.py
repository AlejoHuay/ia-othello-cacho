"""Gu?a: 2. Objetivos de Aprendizaje (O2); 6.1. Estructura del Torneo.
B?squeda del docente extendida con Minimax, pases y m?tricas expl?citas.
"""
from AgenteIA.Agente import Agente
from collections import namedtuple
from functools import wraps
import time

ElEstado = namedtuple('ElEstado', 'jugador, get_utilidad, tablero, movidas')

class AgenteJugador(Agente):
    def __init__(self, altura=4):
        Agente.__init__(self)
        if isinstance(altura, bool) or not isinstance(altura, int) or altura < 1:
            raise ValueError("altura debe ser un entero positivo")
        self.estado = None
        self.altura = altura
        self.tecnica = "podaalfabeta"
        self.metricas = {}
        self.ultimo_valor = None

    def jugadas(self, estado):
        raise NotImplementedError

    def get_utilidad(self, estado, jugador):
        raise NotImplementedError

    def testTerminal(self, estado):
        return not estado.movidas

    def getResultado(self, estado, m):
        raise NotImplementedError

    def funcion_evaluacion(self, estado):
        raise NotImplementedError

    def _buscar(self, estado, podar):
        # Una unidad de profundidad = una ficha colocada; el pase consume cero.
        self.estado = estado
        jugador = estado.jugador
        self.metricas = dict(nodos_visitados=1, nodos_evaluados=0,
                             hojas_terminales=0, cortes=0, pases=0)

        def valor(e, alpha, beta, profundidad):
            self.metricas['nodos_visitados'] += 1
            if self.testTerminal(e):
                self.metricas['nodos_evaluados'] += 1
                self.metricas['hojas_terminales'] += 1
                return self.get_utilidad(e, jugador)
            if profundidad >= self.altura:
                self.metricas['nodos_evaluados'] += 1
                return self.funcion_evaluacion(e)
            if not self.jugadas(e):
                self.metricas['pases'] += 1
                return valor(self.getResultado(e, None), alpha, beta, profundidad)
            if e.jugador == jugador:
                return max_value(e, alpha, beta, profundidad)
            return min_value(e, alpha, beta, profundidad)

        def siguiente(e, accion, alpha, beta, profundidad):
            hijo = self.getResultado(e, accion)
            if hijo.jugador == e.jugador and hijo.movidas:
                self.metricas['pases'] += 1
            return valor(hijo, alpha, beta, profundidad + 1)

        def max_value(e, alpha, beta, profundidad):
            v = -float('inf')
            for accion in self.jugadas(e):
                v = max(v, siguiente(e, accion, alpha, beta, profundidad))
                if podar and v >= beta:
                    self.metricas['cortes'] += 1
                    return v
                if podar:
                    alpha = max(alpha, v)
            return v

        def min_value(e, alpha, beta, profundidad):
            v = float('inf')
            for accion in self.jugadas(e):
                v = min(v, siguiente(e, accion, alpha, beta, profundidad))
                if podar and v <= alpha:
                    self.metricas['cortes'] += 1
                    return v
                if podar:
                    beta = min(beta, v)
            return v

        mejor_score = -float('inf')
        mejor_accion = None
        for accion in self.jugadas(estado):
            alpha = mejor_score if podar else -float('inf')
            v = siguiente(estado, accion, alpha, float('inf'), 0)
            if v > mejor_score:
                mejor_score, mejor_accion = v, accion
        if mejor_accion is None:
            # La ra?z sin acciones comunica un pase, nunca una colocaci?n ficticia.
            self.ultimo_valor = None
        else:
            self.ultimo_valor = float(mejor_score)
        return mejor_accion

    def podaAlphaBeta_eval(self, estado):
        return self._buscar(estado, True)

    def minimax_eval(self, estado):
        return self._buscar(estado, False)

    def mide_tiempo(funcion):
        @wraps(funcion)
        def funcion_medida(self, *args, **kwargs):
            inicio = time.perf_counter()
            resultado = funcion(self, *args, **kwargs)
            segundos = time.perf_counter() - inicio
            self.metricas['tiempo_s'] = segundos
            self.metricas['nodos_por_segundo'] = self.metricas['nodos_evaluados'] / segundos if segundos else 0.0
            return resultado
        return funcion_medida

    @mide_tiempo
    def programa(self):
        if self.estado is None:
            raise ValueError("Asignar estado antes de ejecutar programa")
        if self.tecnica not in ("minimax", "podaalfabeta"):
            raise ValueError("T?cnica desconocida")
        buscar = self.minimax_eval if self.tecnica == "minimax" else self.podaAlphaBeta_eval
        self.set_acciones(buscar(self.estado))
