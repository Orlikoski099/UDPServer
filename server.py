import socket
import os
from protocol import OrlikoskiProtocol
import threading
import hashlib

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 12345        # Porta para comunicação (maior que 1024)
BUFFER_SIZE = 1024  # Tamanho do buffer para leitura do arquivo

# Função para calcular o checksum de uma string
def calcular_checksum(data):
    checksum = hashlib.sha256(data).digest()
    return checksum

# Função para dividir os dados em pacotes de tamanho máximo BUFFER_SIZE
def divide_em_pacotes(data):
    num_pacotes = len(data) // BUFFER_SIZE + 1
    pacotes = []
    for i in range(num_pacotes):
        inicio = i * BUFFER_SIZE
        fim = min((i + 1) * BUFFER_SIZE, len(data))
        pacotes.append(data[inicio:fim])
    return pacotes

# Função para processar cada requisição em uma thread separada
def handle_request(data, client_address):
    protocolo = OrlikoskiProtocol()
    resposta = protocolo.processar_requisicao(data.decode())

    # Verifica se a requisição foi processada com sucesso
    if not resposta.startswith("Erro"):
        nome_arquivo = resposta
        # Verifica se o arquivo existe
        if os.path.exists(nome_arquivo):
            # Abre o arquivo e envia os dados em pacotes para o cliente
            with open(nome_arquivo, 'rb') as file:
                dados_arquivo = file.read()
                checksum = calcular_checksum(dados_arquivo)
                pacotes = divide_em_pacotes(checksum + dados_arquivo)
                num_pacotes_enviados = 0  # Inicializa o contador de pacotes enviados
                for pacote in pacotes:
                    server_socket.sendto(pacote, client_address)
                    num_pacotes_enviados += 1
                # Enviar um pacote vazio para indicar o final do arquivo
                server_socket.sendto(b'', client_address)
                print(f'Dados do arquivo {nome_arquivo} enviados de volta para o cliente. Total de pacotes enviados: {num_pacotes_enviados}')
        else:
            # Se o arquivo não existir, envia uma mensagem de erro para o cliente
            mensagem_erro = 'Arquivo não encontrado'
            server_socket.sendto(mensagem_erro.encode(), client_address)
            print('Mensagem de erro enviada para o cliente.')
    else:
        # Se houver um erro na requisição, envia a mensagem de erro para o cliente
        server_socket.sendto(resposta.encode(), client_address)
        print('Mensagem de erro enviada para o cliente.')

# Criação do socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print('Servidor UDP iniciado.')

while True:
    # Recebe dados do cliente
    try:
        data, client_address = server_socket.recvfrom(1024)
    except ConnectionResetError:
        print('Erro: Conexão com o cliente foi interrompida inesperadamente.')
        continue

    print('Requisição de arquivo recebida do cliente:', data.decode())

    # Cria e inicia uma nova thread para processar a requisição
    thread = threading.Thread(target=handle_request, args=(data, client_address))
    thread.start()

# Fechar o socket
server_socket.close()
