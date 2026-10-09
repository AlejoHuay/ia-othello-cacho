"""2. Objetivos de Aprendizaje, O2; 6. Descripción de la Competencia.
Cliente automático compatible con el protocolo del docente; interfaz opcional.
"""
import argparse
import queue
import threading
import time
import numpy as np
from cliente_base import ClienteBase
from AgenteIA.AgenteJugador import ElEstado
from AgentesEspecificos.AgenteOthello import AgenteOthello

class ClienteAgente(ClienteBase):
    def __init__(self, host='localhost', port=5555, altura=4, evaluacion='fija', tecnica='podaalfabeta'):
        super().__init__(host,port)
        self.agente = AgenteOthello(altura,evaluacion,tecnica)
        self.pendientes = queue.Queue()
        self.on_message_received = self.recibir_estado
        self.firma_enviada = None

    def recibir_estado(self,message):
        if message.get('type') in ('game_start','game_update'):
            if message['type']=='game_start':
                self.firma_enviada=None
            self.pendientes.put(message['game_state'])

    def decidir(self,estado):
        if estado['game_over'] or estado['current_player'] != self.player_color:
            return
        tablero=np.array(estado['board'],dtype=int)
        firma=(tablero.tobytes(),estado['current_player'])
        if firma==self.firma_enviada:
            return
        self.agente.estado=ElEstado(self.player_color,0,tablero,[tuple(m) for m in estado['valid_moves']])
        self.agente.programa()
        movida=self.agente.get_acciones()
        if movida is not None and self.connected and not self.waiting_for_opponent:
            if self.send_move(*movida):
                self.firma_enviada=firma

    def trabajar(self):
        while self.connected:
            try:
                estado=self.pendientes.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                self.decidir(estado)
            except Exception as exc:
                self.disconnect(str(exc))

    def run(self,grafica=False):
        if not self.connect():
            return
        worker=threading.Thread(target=self.trabajar,daemon=True)
        worker.start()
        ui=None
        if grafica:
            from interfaz_grafica import InterfazJuego
            ui=InterfazJuego()
        try:
            while self.connected:
                if ui:
                    if not ui.run_event_loop():
                        break
                    if self.waiting_for_opponent:
                        ui.draw_waiting_screen(self.connection_status,str(self.player_color or ''))
                    else:
                        ui.draw_game_state(self.game_state,self.player_color)
                    ui.clock.tick(30)
                else:
                    if self.game_state and self.game_state['game_over']:
                        break
                    time.sleep(0.05)
        except KeyboardInterrupt:
            pass
        finally:
            self.disconnect('Cliente finalizado')
            if ui:
                ui.quit()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host',default='localhost')
    p.add_argument('--port',type=int,default=5555)
    p.add_argument('--profundidad',type=int,default=4)
    p.add_argument('--evaluacion',choices=['fija','etapas','docente'],default='fija')
    p.add_argument('--tecnica',choices=['minimax','podaalfabeta'],default='podaalfabeta')
    p.add_argument('--grafica',action='store_true')
    a=p.parse_args()
    ClienteAgente(a.host,a.port,a.profundidad,a.evaluacion,a.tecnica).run(a.grafica)
