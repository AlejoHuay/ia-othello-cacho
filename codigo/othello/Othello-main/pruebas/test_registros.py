"""6.1. Estructura del Torneo; 22. Formato de Datos: prueba de integración temporal."""
import argparse
import csv
import json
from pathlib import Path
import tempfile
import unittest
from torneo import ejecutar,leer_partidas,COLUMNAS
from analizar import analizar
from verificar_registros import verificar

class Registros(unittest.TestCase):
    def test_partidas_exportacion_reanudacion(self):
        with tempfile.TemporaryDirectory() as d:
            raiz=Path(d);args=argparse.Namespace(salida=str(raiz/'original'),profundidades=[1],
                agentes=None,aperturas=1,plies=8,semilla=10,max_partidas=2,max_segundos=0)
            ejecutar(args)
            self.assertEqual(verificar(args.salida),2)
            fuentes={p.name:p.read_bytes() for p in Path(args.salida).glob('partida_*.json')}
            ejecutar(args)
            self.assertEqual(fuentes,{p.name:p.read_bytes() for p in Path(args.salida).glob('partida_*.json')})
            r=analizar(args.salida,raiz/'analisis')
            self.assertEqual(r['ejecutadas'],2)
            self.assertEqual(r['comparaciones'][0]['n_bloques'],1)
            self.assertIsNone(r['comparaciones'][0]['ic_bootstrap_diferencia'])
            with (raiz/'analisis/resultados_othello.csv').open(encoding='utf-8',newline='') as f:
                csvr=csv.reader(f);self.assertEqual(next(csvr),COLUMNAS);self.assertEqual(len(list(csvr)),2)
            with (raiz/'analisis/movimientos_othello.csv').open(encoding='utf-8',newline='') as f:
                self.assertGreater(len(list(csv.DictReader(f))),80)
            p=next(Path(args.salida).glob('partida_*.json'));data=json.loads(p.read_text(encoding='utf-8'))
            data['fila']['diferencia_fichas']+=1;p.write_text(json.dumps(data),encoding='utf-8')
            with self.assertRaises(AssertionError):verificar(args.salida)
