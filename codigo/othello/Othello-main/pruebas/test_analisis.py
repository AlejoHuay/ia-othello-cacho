"""13. Métodos Estadísticos Requeridos: casos sintéticos, ajenos al torneo."""
import unittest
from analizar import resumen

class Bloques(unittest.TestCase):
    def test_colores_no_se_cuentan_como_bloques_independientes(self):
        partidas=[]
        for apertura,diferencias in enumerate(((6,-2),(8,2),(-4,-6))):
            for color,diferencia in enumerate(diferencias,1):
                negras_menos_blancas=diferencia*(1 if color==1 else -1)
                ganador='fija' if diferencia>0 else 'etapas'
                partidas.append(dict(apertura_id=apertura,color_a=color,
                    fila=dict(agente_a='fija',agente_b='etapas',profundidad_a=4,
                              diferencia_fichas=diferencia,ganador=ganador),
                    movimientos=[dict(agente=a,tiempo_s=1.,nodos_evaluados=1) for a in ('fija','etapas')],
                    posiciones=[dict(ply=20,evaluaciones=dict(fija=negras_menos_blancas))],
                    negras=32+negras_menos_blancas//2,blancas=32-negras_menos_blancas//2))
        r=resumen(partidas);t=r['comparaciones'][0]
        self.assertEqual(t['n_bloques'],3)
        self.assertEqual((t['bloques_ganados'],t['bloques_perdidos'],t['bloques_empatados']),(1,1,1))
        self.assertEqual(t['p_binomial'],1.)
        self.assertAlmostEqual(t['diferencia_media_bloques'],2/3)
        self.assertIsNotNone(t['ic_bootstrap_diferencia'])
        self.assertEqual(r['correlaciones'][0]['n_bloques'],3)
        self.assertAlmostEqual(r['correlaciones'][0]['pearson']['r'],1.)
        self.assertAlmostEqual(r['correlaciones'][0]['spearman']['r'],1.)
        self.assertFalse(r['chi_cuadrado']['aplicable'])
        global_fija=next(x for x in r['tabla_global'] if x['agente']=='fija')
        self.assertEqual(global_fija['partidas'],6)
        self.assertEqual(global_fija['victorias'],3)
        self.assertEqual(global_fija['puntos'],3)
        self.assertAlmostEqual(global_fija['diferencia_media'],2/3)

        # Una partida completa sin su color complementario es descriptiva, no otro bloque.
        import copy
        incompleta=copy.deepcopy(partidas[0]);incompleta['apertura_id']=99
        r_sin_pareja=resumen(partidas+[incompleta])
        self.assertEqual(r_sin_pareja['comparaciones'],r['comparaciones'])
        self.assertEqual(r_sin_pareja['correlaciones'],r['correlaciones'])
        self.assertEqual(r_sin_pareja['tabla_global'][0]['partidas'],7)
