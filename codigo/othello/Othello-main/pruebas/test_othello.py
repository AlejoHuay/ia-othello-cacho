"""3.1. Reglas Fundamentales; 19. Distribución de Puntos (criterios 1,2,7)."""
import contextlib
import io
import random
import unittest
import numpy as np
from AgenteIA.AgenteJugador import ElEstado
from AgentesEspecificos.AgenteOthello import AgenteOthello
from TableroOthello import TableroOthello
from servidor import GameServer
from evaluador import evaluar, componentes, VERSIONES
from torneo import aperturas, estado_apertura

class Reglas(unittest.TestCase):
    def setUp(self):
        self.a=AgenteOthello(4)
        self.e=TableroOthello(verbose=False).juegoActual

    def test_inicio_y_copia(self):
        self.assertEqual(self.e.jugador,1)
        self.assertEqual(self.e.movidas,[(2,3),(3,2),(4,5),(5,4)])
        copia=self.e.tablero.copy()
        nuevo=self.a.getResultado(self.e,(2,3))
        self.assertEqual(np.count_nonzero(nuevo.tablero==1),4)
        self.assertEqual(np.count_nonzero(nuevo.tablero==2),1)
        np.testing.assert_array_equal(self.e.tablero,copia)
        self.assertFalse(np.shares_memory(self.e.tablero,nuevo.tablero))

    def test_ocho_direcciones(self):
        b=np.zeros((8,8),dtype=int)
        for dr,dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            b[3+dr,3+dc]=2; b[3+2*dr,3+2*dc]=1
        e=ElEstado(1,0,b,self.a._get_valid_moves(b,1))
        r=self.a.getResultado(e,(3,3))
        self.assertEqual(np.count_nonzero(r.tablero==2),0)
        self.assertEqual(np.count_nonzero(r.tablero==1),17)

    def test_pase_y_final(self):
        b=np.ones((8,8),dtype=int);b[0,0]=0;b[0,1]=2
        e=ElEstado(2,0,b,[])
        self.assertFalse(self.a.testTerminal(e))
        p=self.a.getResultado(e,None)
        self.assertEqual(p.jugador,1)
        self.assertIn((0,0),p.movidas)
        fin=self.a.getResultado(p,(0,0))
        self.assertTrue(self.a.testTerminal(fin))
        self.assertGreater(self.a.get_utilidad(fin,1),100)
        self.assertLess(self.a.get_utilidad(fin,2),-100)
        b=np.ones((8,8),dtype=int);b[0,0]=0
        self.assertTrue(self.a.testTerminal(ElEstado(1,0,b,[])))
        b=np.ones((8,8),dtype=int);b[:4,:]=2
        self.assertEqual(self.a.get_utilidad(ElEstado(1,0,b,[]),1),0)

    def test_terminal_domina_esquinas(self):
        b=np.ones((8,8),dtype=int)
        for m in [(0,0),(0,7),(7,0),(7,7)]: b[m]=2
        e=ElEstado(1,0,b,[])
        self.assertGreater(self.a.get_utilidad(e,1),100)

    def test_ilegales_servidor(self):
        with contextlib.redirect_stdout(io.StringIO()): s=GameServer()
        for row,col in [(-1,0),(8,0),(0,8),('0',1),(True,0),(0,0)]:
            self.assertFalse(s.make_move(row,col,1)[0])
        self.assertFalse(s.make_move(2,3,2)[0])

    def test_partidas_completas(self):
        rng=random.Random(17); pases=0
        for _ in range(20):
            e=self.e
            with contextlib.redirect_stdout(io.StringIO()): s=GameServer()
            while e.movidas:
                m=rng.choice(e.movidas)
                old=e
                e=self.a.getResultado(e,m)
                self.assertEqual(np.count_nonzero(e.tablero),np.count_nonzero(old.tablero)+1)
                self.assertTrue(s.make_move(*m,old.jugador)[0])
                np.testing.assert_array_equal(s.board,e.tablero)
                self.assertEqual(s.current_player,e.jugador)
                pases+=int(bool(e.movidas) and old.jugador==e.jugador)
            self.assertTrue(s.game_over)
            self.assertTrue(self.a.testTerminal(e))
        self.assertGreater(pases,0)

    def test_entorno_despacha_por_turno(self):
        class Espia(AgenteOthello):
            def programa(self): self.llamado=True; self.set_acciones(self.estado.movidas[0])
        t=TableroOthello(verbose=False);a=Espia();b=Espia();a.llamado=b.llamado=False
        t.insertar(a);t.insertar(b)
        t.juegoActual=self.a.getResultado(t.juegoActual,(2,3))
        with contextlib.redirect_stdout(io.StringIO()): t.evolucionar()
        self.assertFalse(a.llamado);self.assertTrue(b.llamado)

class Busqueda(unittest.TestCase):
    setUp = Reglas.setUp
    def test_minimax_alphabeta_y_pases(self):
        rng=random.Random(21);estados=[self.e];e=self.e
        while e.movidas:
            anterior=e;e=self.a.getResultado(e,rng.choice(e.movidas))
            if (e.movidas and e.jugador==anterior.jugador) or np.count_nonzero(e.tablero) in (58,60):
                estados.append(e)
        for estado in estados:
            resultados=[]
            for tecnica in ('minimax','podaalfabeta'):
                a=AgenteOthello(4,tecnica=tecnica);a.estado=estado
                copia=estado.tablero.copy();a.programa()
                np.testing.assert_array_equal(estado.tablero,copia)
                resultados.append((a.get_acciones(),a.ultimo_valor,a.metricas['nodos_evaluados']))
            self.assertEqual(resultados[0][:2],resultados[1][:2])
            self.assertLessEqual(resultados[1][2],resultados[0][2])

    def test_referencia_independiente_turnos(self):
        # Oráculo exhaustivo: el operador depende del turno, no de la paridad de nivel.
        rng=random.Random(93);e=self.e
        while np.count_nonzero(e.tablero)<58 and e.movidas:
            e=self.a.getResultado(e,rng.choice(e.movidas))
        root=e.jugador
        def valor(s):
            if self.a.testTerminal(s): return self.a.get_utilidad(s,root)
            if not s.movidas: return valor(self.a.getResultado(s,None))
            vals=[valor(self.a.getResultado(s,m)) for m in s.movidas]
            return (max if s.jugador==root else min)(vals)
        esperado=valor(e)
        a=AgenteOthello(8);a.estado=e;a.programa()
        self.assertEqual(a.ultimo_valor,esperado)

    def test_heuristicas_acotadas_antisimetria(self):
        rng=random.Random(11);e=self.e
        while e.movidas:
            for version in VERSIONES:
                x=evaluar(e.tablero,1,version,self.a._get_valid_moves)
                y=evaluar(e.tablero,2,version,self.a._get_valid_moves)
                self.assertAlmostEqual(x,-y)
                self.assertLessEqual(abs(x),100+1e-12)
            e=self.a.getResultado(e,rng.choice(e.movidas))

    def test_aperturas_reproducibles(self):
        aa=aperturas(13,20261008)
        self.assertEqual(aa,aperturas(13,20261008))
        for a in aa:
            self.assertEqual(np.count_nonzero(estado_apertura(a).tablero),12)

if __name__=='__main__': unittest.main()
