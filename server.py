import socket
import os
from protocol import OrlikoskiProtocol

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 12345        # Porta para comunicação (maior que 1024)
BUFFER_SIZE = 1024  # Tamanho do buffer para leitura do arquivo

# Criação do socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print('Servidor UDP iniciado.')

protocolo = OrlikoskiProtocol()

while True:
    # Recebe dados do cliente
    try:
        data, client_address = server_socket.recvfrom(1024)
    except ConnectionResetError:
        print('Erro: Conexão com o cliente foi interrompida inesperadamente.')
        continue

    print('Requisição de arquivo recebida do cliente:', data.decode())

    # Processa a requisição usando o protocolo definido
    resposta = protocolo.processar_requisicao(data.decode())

    # Verifica se a requisição foi processada com sucesso
    if not resposta.startswith("Erro"):
        nome_arquivo = resposta
        # Verifica se o arquivo existe
        if os.path.exists(nome_arquivo):
            # Abre o arquivo e envia os dados em pacotes para o cliente
            with open(nome_arquivo, 'rb') as file:
                dados_arquivo = file.read()
                tamanho_total = len(dados_arquivo)
                tamanho_enviado = 0
                indice_pacote = 0
                num_pacotes_enviados = 0  # Inicializa o contador de pacotes enviados
                while tamanho_enviado < tamanho_total:
                    inicio = indice_pacote * BUFFER_SIZE
                    fim = min((indice_pacote + 1) * BUFFER_SIZE, tamanho_total)
                    pacote = dados_arquivo[inicio:fim]
                    server_socket.sendto(pacote, client_address)
                    tamanho_enviado += len(pacote)
                    indice_pacote += 1
                    num_pacotes_enviados += 1  # Incrementa o contador de pacotes enviados
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

# Fechar o socket
server_socket.close()
