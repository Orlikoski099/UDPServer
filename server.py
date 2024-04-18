import socket
import os
import threading
import hashlib
import time

from protocol import OrlikoskiProtocol

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 12345        # Porta para comunicação (maior que 1024)
BUFFER_SIZE = 32768  # Tamanho do buffer para leitura do arquivo
DATA_MAX_SIZE = BUFFER_SIZE - 32  # Tamanho máximo dos dados no pacote (descontando o espaço para o checksum)

# Variável global para armazenar o número do último ACK recebido
last_ack_received = -1
actual_ack = -1
ack_lock = threading.Lock()

# Função para calcular o checksum de uma string
def calcular_checksum(data):
    checksum = hashlib.sha256(data).digest()
    return checksum

# Função para enviar um pacote para o cliente
def enviar_pacote(data, client_socket, client_address):
    client_socket.sendto(data, client_address)

# Função para processar cada requisição em uma thread separada
def handle_request(data, client_address):
    protocolo = OrlikoskiProtocol()
    resposta = protocolo.processar_requisicao(data.decode())

    # Verifica se a requisição foi processada com sucesso
    if resposta is not None and not resposta.startswith("Erro"):
        nome_arquivo = resposta
        # Verifica se o arquivo existe
        if os.path.exists(nome_arquivo):
            # Abre o arquivo e envia os dados em pacotes para o cliente
            with open(nome_arquivo, 'rb') as file:
                seq_num = 0
                while True:
                    # Lê os dados do arquivo com o tamanho máximo DATA_MAX_SIZE
                    dados = file.read(DATA_MAX_SIZE)
                    # Verifica se chegou ao final do arquivo
                    if not dados:
                        break
                    # Calcula o checksum apenas para os dados do pacote atual
                    checksum = calcular_checksum(dados)
                    # Concatena o checksum com os dados
                    pacote = checksum + dados
                    # Envia o pacote para o cliente
                    enviar_pacote(pacote, server_socket, client_address)
                    # Aguarda o ACK correspondente ao pacote enviado
                    if not esperar_ack():
                        print(f'Erro: ACK {seq_num} não recebido. Reenviando o pacote...')
                        enviar_pacote(pacote, server_socket, client_address)  # Reenvia o pacote
                    seq_num += 1
                # Enviar um pacote vazio para indicar o final do arquivo
                enviar_pacote(b'', server_socket, client_address)
                print(f'Dados do arquivo {nome_arquivo} enviados de volta para o cliente.')
        else:
            # Se o arquivo não existir, envia uma mensagem de erro para o cliente
            mensagem_erro = 'Arquivo não encontrado'
            enviar_pacote(mensagem_erro.encode(), server_socket, client_address)
            print('Mensagem de arquivo não encontrado enviada para o cliente.')
    elif resposta is not None:
        enviar_pacote(resposta.encode(), server_socket, client_address)
        print('Mensagem de erro enviada para o cliente.')
    

# Função para esperar o ACK do cliente
def esperar_ack(timeout=5):
    global last_ack_received
    print(f'Last ack = {last_ack_received}')
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if actual_ack > last_ack_received:
                last_ack_received = actual_ack
                return True
        except socket.timeout:
            pass
    return False

# Criação do socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print('Servidor UDP iniciado.')

while True:
    # Recebe dados do cliente
    try:
        data, client_address = server_socket.recvfrom(1024)
    except ConnectionResetError:
        # print('Erro: Conexão com o cliente foi interrompida inesperadamente.')
        continue

    print('Requisição de arquivo recebida do cliente:', data.decode())


    if (data.decode().startswith('ACK')):
        actual_ack = int(data.decode().split(" ")[1])
        pass
    else:
        # Cria e inicia uma nova thread para processar a requisição
        thread = threading.Thread(target=handle_request, args=(data, client_address))
        thread.start()

# Fechar o socket
server_socket.close()
