"""
Agente IA mejorado para el Cacho (Parte III de la práctica EC02).

Mejoras respecto a AgenteCachoIA (programa base):
  1. Perspectiva correcta: el valor de cada acción se calcula siempre desde el
     punto de vista del jugador que decide (el base evaluaba los nodos tras
     'anotar' desde la perspectiva del rival y por eso prefería anotar 0).
  2. Profundidad adaptativa: Expectiminimax (nodos MAX + AZAR) hasta el FINAL
     DEL TURNO; la profundidad = tiradas restantes (3, 2, 1 o 0). Elimina la
     miopía de altura=1: la IA "ve" que al final del turno debe anotar.
  3. Memoización (tabla de transposición) de nodos MAX (mano, tiradas),
     nodos AZAR (reserva, tiradas) y hojas (categoría, puntos).
  4. Poda:
       a) ramas equivalentes: re-tirar índices distintos que conservan el mismo
          multiconjunto de dados genera el mismo subárbol (31 -> <=31 únicas);
       b) poda Star1 (Ballard, 1983) en nodos AZAR con cota superior de las hojas.
  5. Métricas por decisión (tiempo, nodos, evaluaciones, cortes) para el torneo.

La función de evaluación es intercambiable (FuncionEvaluacionMejorada o
FuncionEvaluacionBase) para aislar el aporte de la búsqueda y de la función.
"""
from collections import Counter
from time import perf_counter

from AgenteCacho import AgenteCacho, CATEGORIAS, puntuar, normalizar
from AgenteCachoIA import AgenteCachoIA
from funcion_evaluacion import (FuncionEvaluacionMejorada, ESTADOS, IDX_ESTADO,
                                RESERVAS, IDX_RESERVA, RESERVAS_DE,
                                resultados_reserva, N_DADOS)

_INF = float('inf')

# Resultados de cada reserva ordenados por probabilidad descendente (mejor poda)
_RESULTADOS_ORD = [tuple(sorted(resultados_reserva(r), key=lambda x: -x[1]))
                   for r in RESERVAS]
# Sin poda de equivalentes: las 31 máscaras de re-tirada, con repeticiones
_RESERVAS_TODAS = [[IDX_RESERVA[normalizar([e[i] for i in range(N_DADOS) if m & (1 << i)])]
                    for m in range(2 ** N_DADOS - 1)] for e in ESTADOS]


def indices_a_tirar(dados, reserva):
    """Convierte la reserva (multiconjunto a conservar) en índices a re-tirar."""
    pendiente = Counter(reserva)
    tirar = []
    for i, d in enumerate(dados):
        if pendiente[d] > 0:
            pendiente[d] -= 1
        else:
            tirar.append(i)
    return frozenset(tirar)


class AgenteCachoMejorado(AgenteCacho):

    def __init__(self, nombre="IA mejorada", evaluador=None, profundidad=None,
                 usar_memo=True, usar_poda=True):
        """
        profundidad: None => adaptativa (hasta el final del turno).
                     k    => máximo k niveles de AZAR; al cortar se evalúa la
                             mano en curso con la función (característica f3).
        """
        AgenteCacho.__init__(self, nombre=nombre, altura=1)
        self.evaluador = evaluador or FuncionEvaluacionMejorada()
        self.profundidad = profundidad
        self.usar_memo = usar_memo
        self.usar_poda = usar_poda
        self.metricas = []              # una entrada por decisión
        self.ultima_valoracion = {}     # acción -> valor (análisis de decisiones)

    # ============================================================
    # DECISIÓN
    # ============================================================

    def elegir_accion(self, estado):
        t = estado.tablero
        j = estado.jugador
        o = 1 - j
        self._p_j, self._p_o = t['puntajes'][j], t['puntajes'][o]
        self._libres_j = [c for c in CATEGORIAS if c not in t['usadas'][j]]
        self._libres_o = [c for c in CATEGORIAS if c not in t['usadas'][o]]
        self._memo_max, self._memo_azar, self._memo_hoja = {}, {}, {}
        self._memo_cota = {}            # (reserva, r) -> cota superior conocida
        self._n_max = self._n_azar = self._n_eval = self._cortes = 0
        evals_antes = self.evaluador.llamadas
        star1 = self.usar_poda and self.profundidad is None
        self._cota = (self.evaluador.cota_superior_anotar(
            self._p_j, self._p_o, self._libres_j, self._libres_o) if star1 else None)

        inicio = perf_counter()
        dados = normalizar(t['dados'])
        i = IDX_ESTADO[dados]
        r = t['tiradas_restantes']
        valores = {}
        mejor_v, mejor_a = -_INF, None

        # Nodo raíz MAX: anotar (hojas) ...
        for c in self._libres_j:
            v = self._hoja(c, puntuar(c, dados))
            valores[('anotar', c)] = v
            if v > mejor_v:
                mejor_v, mejor_a = v, ('anotar', c)
        # ... o re-tirar (nodos AZAR)
        if r > 0:
            for k in self._reservas(i):
                v = self._azar(k, r, 1, mejor_v)
                accion = ('tirar', indices_a_tirar(t['dados'], RESERVAS[k]))
                valores[accion] = v
                if v > mejor_v:
                    mejor_v, mejor_a = v, accion

        self.ultima_valoracion = valores
        self.metricas.append({
            'tiempo': perf_counter() - inicio,
            'nodos_max': self._n_max + 1,
            'nodos_azar': self._n_azar,
            'evaluaciones': self.evaluador.llamadas - evals_antes,
            'cortes': self._cortes,
            'tiradas_restantes': r,
            'ronda': len(CATEGORIAS) - len(self._libres_j),
            'accion': mejor_a[0],
            'valor': mejor_v,
        })
        return mejor_a

    def programa(self):
        self.set_acciones([])
        accion = self.elegir_accion(self.estado)
        if accion is not None:
            self.set_acciones(accion)

    # ============================================================
    # EXPECTIMINIMAX DEL TURNO (MAX + AZAR)
    # ============================================================

    def _reservas(self, i):
        return RESERVAS_DE[i] if self.usar_poda else _RESERVAS_TODAS[i]

    def _hoja(self, c, pts):
        """Valor tras anotar `pts` en `c`: el turno pasa al rival con mano nueva."""
        clave = (c, pts)
        if self.usar_memo and clave in self._memo_hoja:
            return self._memo_hoja[clave]
        self._n_eval += 1
        resto = [x for x in self._libres_j if x != c]
        mueve_j = not self._libres_o and bool(resto)
        v = self.evaluador.evaluar(self._p_j + pts, self._p_o, resto,
                                   self._libres_o, mueve_j)
        if self.usar_memo:
            self._memo_hoja[clave] = v
        return v

    def _max(self, i, r, nivel):
        """Nodo MAX: mano ESTADOS[i] con r tiradas restantes. Devuelve valor exacto."""
        clave = (i, r)
        if self.usar_memo and clave in self._memo_max:
            return self._memo_max[clave]
        self._n_max += 1
        dados = ESTADOS[i]
        mejor = -_INF
        for c in self._libres_j:
            mejor = max(mejor, self._hoja(c, puntuar(c, dados)))
        if r > 0:
            if self.profundidad is not None and nivel >= self.profundidad:
                # Corte de profundidad: estimar el valor de seguir tirando
                mejor = max(mejor, self.evaluador.evaluar(
                    self._p_j, self._p_o, self._libres_j, self._libres_o,
                    True, dados, r))
            else:
                for k in self._reservas(i):
                    mejor = max(mejor, self._azar(k, r, nivel + 1, mejor))
        if self.usar_memo:
            self._memo_max[clave] = mejor
        return mejor

    def _azar(self, k, r, nivel, umbral):
        """
        Nodo AZAR: se conserva RESERVAS[k] y se re-tira el resto.
        Si la poda Star1 está activa y el valor no puede superar `umbral`,
        devuelve una cota superior <= umbral (no se memoiza: no es exacta).
        """
        clave = (k, r)
        if self.usar_memo:
            if clave in self._memo_azar:
                return self._memo_azar[clave]
            cota = self._memo_cota.get(clave)
            if cota is not None and cota <= umbral:
                return cota                       # ya se sabe que no supera el umbral
        self._n_azar += 1
        acumulado, restante = 0.0, 1.0
        for i, p in _RESULTADOS_ORD[k]:
            acumulado += p * self._max(i, r - 1, nivel)
            restante -= p
            if self._cota is not None and acumulado + restante * self._cota <= umbral:
                self._cortes += 1
                cota = acumulado + max(restante, 0.0) * self._cota
                if self.usar_memo:
                    self._memo_cota[clave] = cota
                return cota
        if self.usar_memo:
            self._memo_azar[clave] = acumulado
        return acumulado


class AgenteCachoBase(AgenteCachoIA):
    """
    Agente del programa base SIN cambios de lógica; solo agrega métricas
    (tiempo y número de evaluaciones por decisión) para el torneo.
    """

    def __init__(self, nombre="IA base", altura=1):
        AgenteCachoIA.__init__(self, nombre=nombre, altura=altura)
        self.metricas = []
        self._evals = 0

    def funcion_evaluacion(self, estado):
        self._evals += 1
        return AgenteCachoIA.funcion_evaluacion(self, estado)

    def elegir_accion(self, estado):
        self._evals = 0
        inicio = perf_counter()
        accion = AgenteCachoIA.elegir_accion(self, estado)
        self.metricas.append({
            'tiempo': perf_counter() - inicio,
            'evaluaciones': self._evals,
            'tiradas_restantes': estado.tablero['tiradas_restantes'],
            'ronda': len(estado.tablero['usadas'][estado.jugador]),
            'accion': accion[0] if accion else None,
        })
        return accion
