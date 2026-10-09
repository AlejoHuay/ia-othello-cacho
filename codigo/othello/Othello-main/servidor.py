
import socket
import threading
import json
import numpy as np
import time
import traceback
from AgentesEspecificos.AgenteOthello import AgenteOthello
from AgenteIA.AgenteJugador import ElEstado


class GameServer:
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.client_info = []
        self.running = False
        self.lock = threading.RLock()
        self.send_lock = threading.Lock()
        self.game_started = False
        self.motor = AgenteOthello(1)
        self.reset_game()

    def reset_game(self):
        self.board = np.zeros((8, 8), dtype=int)
        mid = 4
        self.board[mid - 1][mid - 1] = 2
        self.board[mid][mid] = 2
        self.board[mid - 1][mid] = 1
        self.board[mid][mid - 1] = 1
        self.current_player = 1
        self.game_over = False
        self.winner = None
        print("🎮 Juego reiniciado")

    def get_valid_moves(self, player=None):
        return self.motor._get_valid_moves(self.board, self.current_player if player is None else player)

    def is_valid_move(self, row, col, player):
        if type(row) is not int or type(col) is not int or player not in (1, 2):
            return False
        return self.motor._is_valid_move(self.board, player, row, col)

    def make_move(self, row, col, player):
        # 3.1. Reglas Fundamentales: un único motor (el agente del docente).
        with self.lock:
            if self.game_over:
                return False, "El juego terminó"
            if player != self.current_player:
                return False, "No es tu turno"
            if not self.is_valid_move(row, col, player):
                return False, "Movimiento inválido"
            estado = ElEstado(player, 0, self.board, self.get_valid_moves())
            siguiente = self.motor.getResultado(estado, (row, col))
            self.board = siguiente.tablero
            self.current_player = siguiente.jugador
            self.game_over = self.motor.testTerminal(siguiente)
            if self.game_over:
                self.determine_winner()
            return True, "Movimiento exitoso"

    def determine_winner(self):
        black_count = np.sum(self.board == 1)
        white_count = np.sum(self.board == 2)
        if black_count > white_count:
            self.winner = 1
        elif white_count > black_count:
            self.winner = 2
        else:
            self.winner = 0

    def get_game_state(self):
        # CONVERTIR todos los valores numpy a tipos nativos de Python
        board_list = self.board.tolist()
        valid_moves = self.get_valid_moves()

        # Asegurarse de que los scores sean int nativos, no int64
        black_score = int(np.sum(self.board == 1))
        white_score = int(np.sum(self.board == 2))

        return {
            'board': board_list,
            'current_player': int(self.current_player),  # Convertir a int nativo
            'game_over': bool(self.game_over),  # Convertir a bool nativo
            'winner': int(self.winner) if self.winner is not None else None,
            'valid_moves': [(int(row), int(col)) for row, col in valid_moves],  # Convertir a int nativos
            'scores': {
                'black': black_score,
                'white': white_score
            }
        }

    def send_to_client(self, client_socket, message):
        try:
            # Función personalizada para serializar tipos numpy
            def numpy_serializer(obj):
                if isinstance(obj, (np.integer, np.int64, np.int32)):
                    return int(obj)
                elif isinstance(obj, (np.floating, np.float64, np.float32)):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, (np.bool_)):
                    return bool(obj)
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

            message_str = json.dumps(message, default=numpy_serializer) + '\n'
            with self.send_lock:
                client_socket.sendall(message_str.encode('utf-8'))
            print(f"📤 Enviado a cliente: {message['type']}")
            return True
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            traceback.print_exc()
            return False

    def broadcast_to_all(self, message):
        with self.lock:
            clients_to_remove = []
            for i, client_socket in enumerate(self.clients):
                if client_socket:
                    if not self.send_to_client(client_socket, message):
                        print(f"⚠️ Cliente {i} desconectado")
                        clients_to_remove.append(i)

            # Remover clientes desconectados
            for i in sorted(clients_to_remove, reverse=True):
                if i < len(self.clients):
                    self.clients[i] = None
                    self.client_info[i] = None

    def start_game_if_ready(self):
        """Inicia el juego si hay exactamente 2 jugadores conectados"""
        with self.lock:
            active_clients = [c for c in self.clients if c is not None]
            preparados = sum(bool(info and info.get('ready')) for info in self.client_info)
            if self.game_started or len(active_clients) != 2 or preparados != 2:
                return False
            self.reset_game()
            self.game_started = True

        print(f"🔍 Verificando jugadores: {len(active_clients)}/2 conectados")

        if len(active_clients) == 2:
            print("🎉 ¡Ambos jugadores conectados! Iniciando juego...")

            # Reiniciar el juego para empezar desde cero
            game_state = self.get_game_state()
            start_message = {
                'type': 'game_start',
                'game_state': game_state,
                'message': '¡El juego ha comenzado!'
            }

            print("📋 Estado del juego preparado para enviar:")
            print(f"   - Tablero: {len(game_state['board'])}x{len(game_state['board'][0])}")
            print(f"   - Jugador actual: {game_state['current_player']}")
            print(f"   - Movimientos válidos: {len(game_state['valid_moves'])}")
            print(f"   - Puntuación: Negro {game_state['scores']['black']}, Blanco {game_state['scores']['white']}")

            self.broadcast_to_all(start_message)
            print("✅ Mensaje de inicio enviado a ambos clientes")
            return True

        print(f"⚠️ No hay suficientes jugadores: {len(active_clients)}/2")
        return False

    def handle_client(self, client_socket, client_address, client_id):
        print(f"👤 Cliente {client_id} conectado desde {client_address}")

        try:
            # Asignar color al cliente (1 para el primero, 2 para el segundo)
            player_color = client_id + 1

            with self.lock:
                # Asegurarse de que las listas sean lo suficientemente grandes
                while len(self.clients) <= client_id:
                    self.clients.append(None)
                while len(self.client_info) <= client_id:
                    self.client_info.append(None)

                self.clients[client_id] = client_socket
                self.client_info[client_id] = {
                    'address': client_address,
                    'color': player_color,
                    'connected': True
                }

            print(
                f"✅ Cliente {client_id} registrado en lista. Total: {sum(1 for c in self.clients if c is not None)}/2")

            # Enviar mensaje de bienvenida
            welcome_msg = {
                'type': 'welcome',
                'player_color': int(player_color),  # Convertir a int nativo
                'message': f'Eres el jugador {"Negro" if player_color == 1 else "Blanco"}',
                'client_id': int(client_id)  # Convertir a int nativo
            }
            self.send_to_client(client_socket, welcome_msg)
            with self.lock:
                self.client_info[client_id]['ready'] = True

            # Pequeña pausa para asegurar que el cliente procesó la bienvenida
            time.sleep(0.3)

            # Verificar estado actual de conexiones
            with self.lock:
                active_count = sum(1 for c in self.clients if c is not None)

            print(f"📊 Estado actual: {active_count}/2 jugadores activos")

            if active_count == 2:
                print("🚀 Ambos jugadores conectados, iniciando juego...")
                # Pequeña pausa para asegurar que ambos clientes están listos
                time.sleep(0.5)
                self.start_game_if_ready()
            else:
                # Enviar mensaje de espera CON EL CONTADOR CORRECTO
                wait_msg = {
                    'type': 'waiting',
                    'message': f'Esperando oponente... ({active_count}/2 jugadores)'
                }
                self.send_to_client(client_socket, wait_msg)
                print(f"⏳ Cliente {client_id} en modo espera ({active_count}/2)")

            # Bucle principal para recibir mensajes
            buffer = ""
            while self.running:
                try:
                    data = client_socket.recv(4096).decode('utf-8')
                    if not data:
                        print(f"📭 Cliente {client_id} cerró la conexión")
                        break

                    buffer += data
                    while '\n' in buffer:
                        message_str, buffer = buffer.split('\n', 1)
                        if message_str.strip():
                            try:
                                message = json.loads(message_str)
                                print(f"📨 Mensaje de cliente {client_id}: {message['type']}")
                                self.process_client_message(client_socket, client_id, player_color, message)
                            except json.JSONDecodeError as e:
                                print(f"❌ JSON inválido de cliente {client_id}: {e}")

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"❌ Error recibiendo datos de cliente {client_id}: {e}")
                    break

        except Exception as e:
            print(f"❌ Error con cliente {client_id}: {e}")
            traceback.print_exc()
        finally:
            print(f"👋 Cliente {client_id} desconectado")
            with self.lock:
                self.game_started = False
                if client_id < len(self.clients):
                    self.clients[client_id] = None
                if client_id < len(self.client_info):
                    self.client_info[client_id] = {'connected': False}

            try:
                client_socket.close()
            except:
                pass

            # Notificar al otro jugador
            disconnect_msg = {
                'type': 'opponent_disconnected',
                'message': 'El oponente se ha desconectado'
            }
            if self.running:
                self.broadcast_to_all(disconnect_msg)

    def process_client_message(self, client_socket, client_id, player_color, message):
        msg_type = message.get('type')

        if msg_type == 'move' and self.game_started:
            row, col = message.get('row'), message.get('col')
            if row is not None and col is not None:
                print(f"🎯 Cliente {client_id} intenta mover a ({row}, {col})")
                with self.lock:
                    success, msg = self.make_move(row, col, player_color)
                    response = {'type': 'move_response', 'success': success, 'message': msg}
                    self.send_to_client(client_socket, response)
                    if success:
                        print("✅ Movimiento exitoso, actualizando juego...")
                        update_msg = {'type': 'game_update', 'game_state': self.get_game_state()}
                        self.broadcast_to_all(update_msg)

    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1)

            self.running = True
            print(f"🎮 Servidor Othello iniciado en {self.host}:{self.port}")
            print("📍 Esperando jugadores...")

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_socket.settimeout(1)

                    print(f"🔗 Nueva conexión de {client_address}")

                    with self.lock:
                        if sum(c is not None for c in self.clients) >= 2:
                            self.send_to_client(client_socket, {"type": "error", "message": "Servidor completo"})
                            client_socket.close()
                            continue
                        # Buscar slot vacío
                        slot_index = None
                        for i in range(len(self.clients)):
                            if self.clients[i] is None:
                                slot_index = i
                                break

                        # Si no hay slot vacío, crear uno nuevo
                        if slot_index is None:
                            slot_index = len(self.clients)
                            self.clients.append(None)
                            self.client_info.append(None)

                        print(f"🆔 Asignando slot {slot_index} al nuevo cliente")
                        self.clients[slot_index] = client_socket

                    # Iniciar hilo del cliente
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address, slot_index),
                        name=f"ClientThread-{slot_index}"
                    )
                    client_thread.daemon = True
                    client_thread.start()

                    print(
                        f"✅ Hilo del cliente {slot_index} iniciado. Total activos: {sum(1 for c in self.clients if c is not None)}/2")

                    # Esperar a que el cliente se registre completamente
                    time.sleep(0.5)

                    # Verificar si podemos iniciar el juego
                    print("🔄 Verificando estado después de nueva conexión...")
                    self.start_game_if_ready()

                except socket.timeout:
                    continue
                except KeyboardInterrupt:
                    print("\n🛑 Deteniendo servidor...")
                    self.running = False
                except Exception as e:
                    print(f"❌ Error aceptando conexión: {e}")

        except Exception as e:
            print(f"❌ Error del servidor: {e}")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for client in self.clients:
            if client:
                try:
                    client.close()
                except:
                    pass
        print("🛑 Servidor detenido")


if __name__ == "__main__":
    print("=== 🎮 SERVIDOR OTHELLO ===")
    host = input("🌐 Host [127.0.0.1]: ").strip() or '127.0.0.1'
    port_input = input("🔌 Puerto [5555]: ").strip()
    port = int(port_input) if port_input.isdigit() else 5555

    server = GameServer(host, port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n⏹️  Servidor interrumpido")
    except Exception as e:
        print(f"❌ Error: {e}")