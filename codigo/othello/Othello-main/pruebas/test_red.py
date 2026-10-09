"""19. Distribución de Puntos, criterio 2: integración cliente-servidor local."""
import contextlib
import io
import socket
import threading
import time
import unittest
from servidor import GameServer
from cliente_agente import ClienteAgente

class Red(unittest.TestCase):
    def test_dos_agentes_red_y_tercer_cliente(self):
        with contextlib.redirect_stdout(io.StringIO()):
            server=GameServer('127.0.0.1',0)
            worker=threading.Thread(target=server.start,daemon=True);worker.start()
            clientes=[]
            try:
                limite=time.monotonic()+3
                while not server.running and time.monotonic()<limite:time.sleep(.01)
                self.assertTrue(server.running)
                puerto=server.server_socket.getsockname()[1]
                for version in ('fija','etapas'):
                    c=ClienteAgente('127.0.0.1',puerto,1,version)
                    self.assertTrue(c.connect());clientes.append(c)
                    threading.Thread(target=c.trabajar,daemon=True).start()
                limite=time.monotonic()+15
                while time.monotonic()<limite:
                    if all(c.game_state and c.game_state['game_over'] for c in clientes):break
                    time.sleep(.02)
                self.assertTrue(all(c.game_state and c.game_state['game_over'] for c in clientes))
                self.assertTrue(server.game_over)
                self.assertEqual(clientes[0].game_state['board'],clientes[1].game_state['board'])
                with socket.create_connection(('127.0.0.1',puerto),timeout=3) as tercero:
                    self.assertIn(b'Servidor completo',tercero.recv(4096))
                self.assertFalse(server.start_game_if_ready())
            finally:
                for c in clientes:c.disconnect('prueba terminada')
                server.stop();worker.join(timeout=3)
