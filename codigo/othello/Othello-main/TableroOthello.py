import numpy as np
from AgenteIA.Entorno import Entorno
from AgenteIA.AgenteJugador import ElEstado
from AgentesEspecificos.AgenteOthello import AgenteOthello

class TableroOthello(Entorno):

    def __init__(self, board_size=8, verbose=True):
        super().__init__()
        if board_size != 8:
            raise ValueError("La pr?ctica requiere un tablero 8x8")
        self.BOARD_SIZE = board_size
        self.verbose = verbose
        
        tablero_inicial = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        mid = self.BOARD_SIZE // 2
        tablero_inicial[mid - 1, mid - 1] = 2  # Blanco (Jugador 2)
        tablero_inicial[mid, mid] = 2
        tablero_inicial[mid - 1, mid] = 1      # Negro (Jugador 1)
        tablero_inicial[mid, mid - 1] = 1

        jugador_inicial = 1 # Negro empieza
        movidas_iniciales = self._get_valid_moves(tablero_inicial, jugador_inicial)

        self.juegoActual = ElEstado(
            jugador=jugador_inicial,
            tablero=tablero_inicial,
            movidas=movidas_iniciales,
            get_utilidad=0
        )
        if self.verbose:
            print("--- Tablero Inicial ---")
            self.mostrar_tablero(self.juegoActual.tablero)


    def get_percepciones(self, agente):
        agente.estado = self.juegoActual
        if agente.estado.movidas:
            agente.programa()
        else:
            # Si no hay movimientos, es el fin del juego
            for a in self.get_agentes():
                a.inhabilitar()

    def ejecutar(self, agente):
        jugador = self.juegoActual.jugador
        movida = agente.get_acciones()
        self.juegoActual = agente.getResultado(self.juegoActual, movida)
        
        nombre_jugador = "Negro (1)" if jugador == 1 else "Blanco (2)"
        print(f"\n--- Jugador {nombre_jugador} elige {movida} ---")
        self.mostrar_tablero(self.juegoActual.tablero)
        
        if agente.testTerminal(self.juegoActual):
            print("\n--- ¡JUEGO TERMINADO! ---")
            score_negro = np.sum(self.juegoActual.tablero == 1)
            score_blanco = np.sum(self.juegoActual.tablero == 2)
            print(f"Resultado Final: Negro (1): {score_negro} - Blanco (2): {score_blanco}")
            
            if score_negro > score_blanco:
                print("¡Gana el jugador Negro (1)!")
            elif score_blanco > score_negro:
                print("¡Gana el jugador Blanco (2)!")
            else:
                print("¡Es un empate!")

            for a in self.get_agentes():
                a.inhabilitar()

    def evolucionar(self):
        """3.1. Reglas Fundamentales: seleccionar por color, incluso tras un pase."""
        if len(self.get_agentes()) != 2:
            raise ValueError("Insertar exactamente dos agentes: negras y blancas")
        if not self.finalizar():
            agente = self.get_agentes()[self.juegoActual.jugador - 1]
            self.get_percepciones(agente)
            if agente.esta_habilitado():
                self.ejecutar(agente)

    def mostrar_tablero(self, tablero):
        """Muestra el tablero en formato de texto en la consola."""
        # Header de columnas
        print("  " + " ".join(map(str, range(self.BOARD_SIZE))))
        print(" +" + "--" * self.BOARD_SIZE)
        
        for i, row in enumerate(tablero):
            # Fila con números
            print(f"{i}|", end=" ")
            for cell in row:
                if cell == 1:
                    print("B", end=" ") # Black
                elif cell == 2:
                    print("W", end=" ") # White
                else:
                    print(".", end=" ") # Empty
            print()
        
        score_negro = np.sum(tablero == 1)
        score_blanco = np.sum(tablero == 2)
        print(f"Puntuación -> Negro (B): {score_negro} | Blanco (W): {score_blanco}")


    def _is_valid_move(self, board, player, row, col):
        return AgenteOthello(1)._is_valid_move(board, player, row, col)

    def _get_valid_moves(self, board, player):
        return AgenteOthello(1)._get_valid_moves(board, player)
