"""
Pruebas de la mitad 'función de evaluación + agente' del Cacho.
Ejecutar desde codigo/cacho/Cacho:   python -m unittest discover -s pruebas -v
"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AgenteCacho import CATEGORIAS, puntuar, normalizar            # noqa: E402
from AgenteIA.AgenteJugador import ElEstado                          # noqa: E402
import funcion_evaluacion as fe                                       # noqa: E402
from agente_ia import AgenteCachoMejorado, AgenteCachoBase, indices_a_tirar  # noqa: E402
from simulador import jugar_partida, vista_para                       # noqa: E402


def estado(dados, tiradas=3, p=(0, 0), usadas=(set(), set()), jugador=0):
    t = {'dados': normalizar(dados), 'tiradas_restantes': tiradas,
         'puntajes': list(p), 'usadas': [set(usadas[0]), set(usadas[1])], 'ronda': 0}
    return ElEstado(jugador=jugador, get_utilidad=0, tablero=t, movidas=None)


class TestTablas(unittest.TestCase):

    def test_distribuciones_suman_uno(self):
        self.assertAlmostEqual(fe.P_INICIAL.sum(), 1.0)
        self.assertTrue(abs(fe.MATRIZ_T.sum(axis=1) - 1).max() < 1e-12)
        self.assertEqual(len(fe.ESTADOS), 252)
        self.assertEqual(len(fe.RESERVAS), 210)

    def test_valor_esperado_balas_formula_cerrada(self):
        # Apuntando a 'k' con 4 tiradas: E = k * 5 * (1 - (5/6)^4)
        for k in range(1, 7):
            self.assertAlmostEqual(fe.MU[str(k)], k * 5 * (1 - (5 / 6) ** 4), places=6)

    def test_probabilidad_grande(self):
        # P(grande en <=4 tiradas) conocida ~ 0.100 (Yahtzee, cadena de Markov)
        self.assertAlmostEqual(fe.MU['grande'] / 50, 0.1003, delta=0.002)

    def test_valor_dinamico_sin_tiradas_es_puntaje(self):
        for c in CATEGORIAS:
            for e in random.Random(0).sample(fe.ESTADOS, 30):
                self.assertEqual(fe.valor_esperado_dinamico(c, e, 0), puntuar(c, e))

    def test_valor_dinamico_monotono_en_tiradas(self):
        for c in CATEGORIAS:
            v = fe.TABLA_VE[c]
            for r in range(1, 4):
                self.assertTrue((v[r] >= v[r - 1] - 1e-12).all())


class TestFuncionEvaluacion(unittest.TestCase):

    def test_perspectiva_simetrica(self):
        f = fe.FuncionEvaluacionMejorada()
        e = estado((2, 2, 3, 5, 6), 2, p=(30, 12), usadas=({'1', 'full'}, {'6'}))
        self.assertAlmostEqual(f(e, 0), -f(e, 1), places=9)    # suma cero
        e1 = ElEstado(1, 0, e.tablero, None)                     # ahora mueve el rival
        self.assertAlmostEqual(f(e1, 0), -f(e1, 1), places=9)

    def test_mas_puntos_es_mejor(self):
        f = fe.FuncionEvaluacionMejorada()
        a = estado((1, 2, 3, 4, 6), 0, p=(40, 20))
        b = estado((1, 2, 3, 4, 6), 0, p=(10, 20))
        self.assertGreater(f(a, 0), f(b, 0))

    def test_base_replica_ecuacion_1(self):
        f = fe.FuncionEvaluacionBase(alfa=0.6)
        e = estado((1, 1, 1, 1, 1), 3, p=(10, 4), usadas=({'grande'}, set()))
        fut0 = sum(fe._VE_ESTATICO[c] for c in CATEGORIAS if c != 'grande')
        fut1 = sum(fe._VE_ESTATICO[c] for c in CATEGORIAS)
        self.assertAlmostEqual(f(e, 0), (10 + .6 * fut0) - (4 + .6 * fut1))

    def test_cota_superior_es_valida(self):
        f = fe.FuncionEvaluacionMejorada()
        libres_j, libres_o = ['3', 'full', 'grande'], ['1', 'poker']
        cota = f.cota_superior_anotar(20, 25, libres_j, libres_o)
        for c in libres_j:
            for pts in range(0, fe.PUNTAJE_MAXIMO[c] + 1):
                resto = [x for x in libres_j if x != c]
                self.assertLessEqual(f.evaluar(20 + pts, 25, resto, libres_o, False), cota + 1e-9)


class TestAgente(unittest.TestCase):

    def test_indices_a_tirar(self):
        self.assertEqual(indices_a_tirar((2, 3, 3, 5, 6), (3, 3)), frozenset({0, 3, 4}))
        self.assertEqual(indices_a_tirar((1, 1, 1, 1, 1), ()), frozenset(range(5)))

    def test_sin_tiradas_debe_anotar(self):
        ia = AgenteCachoMejorado()
        a = ia.elegir_accion(estado((1, 2, 4, 5, 6), 0))
        self.assertEqual(a[0], 'anotar')

    def test_anota_grande_si_lo_tiene(self):
        ia = AgenteCachoMejorado()
        self.assertEqual(ia.elegir_accion(estado((4, 4, 4, 4, 4), 3)), ('anotar', 'grande'))

    def test_no_desperdicia_puntos_como_el_base(self):
        # Con full servido y 0 tiradas: la IA mejorada anota 'full'
        ia = AgenteCachoMejorado()
        self.assertEqual(ia.elegir_accion(estado((2, 2, 5, 5, 5), 0)), ('anotar', 'full'))

    def test_juega_igual_como_jugador_1(self):
        ia = AgenteCachoMejorado()
        e0 = estado((2, 3, 3, 5, 6), 2, p=(15, 9), usadas=({'1'}, {'2', '6'}))
        t = e0.tablero
        e1 = ElEstado(1, 0, {**t, 'puntajes': t['puntajes'][::-1],
                             'usadas': t['usadas'][::-1]}, None)
        self.assertEqual(ia.elegir_accion(e0), ia.elegir_accion(e1))

    def test_memo_y_poda_no_cambian_la_decision(self):
        rng = random.Random(5)
        for _ in range(15):
            e = estado([rng.randint(1, 6) for _ in range(5)], rng.randint(0, 3),
                       p=(rng.randint(0, 60), rng.randint(0, 60)),
                       usadas=(set(rng.sample(CATEGORIAS, rng.randint(0, 8))), set()))
            ref = AgenteCachoMejorado(usar_memo=True, usar_poda=False)
            rap = AgenteCachoMejorado(usar_memo=True, usar_poda=True)
            self.assertEqual(ref.elegir_accion(e), rap.elegir_accion(e))
            self.assertAlmostEqual(ref.metricas[-1]['valor'], rap.metricas[-1]['valor'])

    def test_memo_reduce_evaluaciones(self):
        e = estado((2, 3, 3, 5, 6), 3)
        sin = AgenteCachoMejorado(profundidad=1, usar_memo=False, usar_poda=False)
        con = AgenteCachoMejorado(profundidad=1, usar_memo=True, usar_poda=True)
        self.assertEqual(sin.elegir_accion(e), con.elegir_accion(e))
        self.assertLess(con.metricas[-1]['evaluaciones'], sin.metricas[-1]['evaluaciones'])


class TestSimulador(unittest.TestCase):

    def test_partida_completa_y_reproducible(self):
        r1 = jugar_partida(AgenteCachoMejorado(), AgenteCachoBase(), semilla=11)
        r2 = jugar_partida(AgenteCachoMejorado(), AgenteCachoBase(), semilla=11)
        self.assertEqual(r1['puntajes'], r2['puntajes'])
        self.assertEqual(r1['errores'], [0, 0])
        anot = [d for d in r1['decisiones'] if d['tipo'] == 'anotar']
        self.assertEqual(len(anot), 2 * len(CATEGORIAS))

    def test_vista_espejada(self):
        t = {'dados': (1, 2, 3, 4, 5), 'tiradas_restantes': 1, 'puntajes': [5, 9],
             'usadas': [{'1'}, {'2'}], 'ronda': 2}
        v = vista_para(t, 1)
        self.assertEqual(v.jugador, 0)
        self.assertEqual(v.tablero['puntajes'], [9, 5])
        self.assertEqual(v.tablero['usadas'], [{'2'}, {'1'}])


if __name__ == '__main__':
    unittest.main()
