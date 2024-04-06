import socket
import tkinter as tk
import threading
from protocol import OrlikoskiProtocol
import os
from datetime import datetime

# Configurações do cliente
SERVER_HOST = '127.0.0.1'  # Endereço IP do servidor
SERVER_PORT = 12345        # Porta do servidor
FILE_REQUEST = 'OBTER filesToSend/arquivoTeste.pdf'  # Exemplo de requisição de arquivo

# Criação do socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Instanciando o protocolo
protocolo = OrlikoskiProtocol()

def sendRequest():
    global client_socket  # Use a variável global para acessar o socket definido fora da função

    # Envia requisição para o servidor
    client_socket.sendto(FILE_REQUEST.encode(), (SERVER_HOST, SERVER_PORT))
    print('Requisição enviada para o servidor.')
    if(not thread_receive.is_alive()):
        thread_receive.start()


def receiveResponse():
    global client_socket  # Use a variável global para acessar o socket definido fora da função

    # Recebe o nome do arquivo a partir da solicitação
    nome_arquivo = FILE_REQUEST.split(" ")[1].split("/")[-1]
    nome_arquivo = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{nome_arquivo}"

    # Verifica se o diretório existe, se não existir, cria-o
    if not os.path.exists("filesReceived"):
        os.makedirs("filesReceived")

    # Caminho completo para salvar o arquivo recebido
    caminho_arquivo = f"filesReceived/{nome_arquivo}"

    with open(caminho_arquivo, 'wb') as file:
        while True:
            pacote, server_address = client_socket.recvfrom(1024)
            if len(pacote) == 0:
                print('Recebida mensagem de finalização do servidor.')
                break  # Encerra o loop se o tamanho do pacote for zero (final da transmissão)
            
            # Escreve os dados recebidos no arquivo
            file.write(pacote)

            # Atualiza a label com o número de bytes recebidos
            num_bytes = len(pacote)
            status_label.configure(text=f"Status: Recebidos {num_bytes} bytes.")

    print(f'Arquivo recebido salvo em: {caminho_arquivo}')

    # Fechar o socket no final
    client_socket.close()

# Iniciar thread para receber respostas do servidor
thread_receive = threading.Thread(target=receiveResponse)
thread_receive.daemon = True

janela = tk.Tk()
janela.title("Enviar Request")

# Função a ser chamada quando o botão for clicado
botao_enviar = tk.Button(janela, text="Enviar Request", command=sendRequest)
botao_enviar.pack()

# Label para exibir o status da transação
status_label = tk.Label(janela, text="")
status_label.pack()

# Iniciando o loop principal da interface gráfica
janela.mainloop()
