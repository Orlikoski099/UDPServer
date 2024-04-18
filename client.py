import tkinter as tk
import threading
import socket
import os
from datetime import datetime
import hashlib
import time

class ClientGUI:
    def __init__(self, master, client_id):
        self.master = master
        self.client_id = client_id

        # Configurações do cliente
        self.SERVER_HOST = '127.0.0.1'  # Endereço IP do servidor
        self.SERVER_PORT = 12345        # Porta do servidor
        self.FILE_REQUEST = ''          # Requisição de arquivo inicialmente vazia
        self.FILE_NAME = f'arquivo_{client_id}'
        self.client_socket = None       # Inicializa o socket do cliente como None

        # Entrada de texto para o nome do arquivo
        self.entry_arquivo = tk.Entry(master)
        self.entry_arquivo.pack()

        # Botão para enviar a requisição
        self.botao_enviar = tk.Button(master, text=f"Enviar Request Cliente {self.client_id}", command=self.send_request)
        self.botao_enviar.pack()

        # Label para exibir o status da transação
        self.status_label = tk.Label(master, text=f"Status Cliente {self.client_id}:")
        self.status_label.pack()

        # Iniciar thread para receber respostas do servidor
        self.thread_receive = threading.Thread(target=self.receive_response)
        self.thread_receive.daemon = True

    def send_request(self):
        # Obtém o nome do arquivo da entrada de texto
        self.FILE_REQUEST = f'OBTER filesToSend/{self.entry_arquivo.get()}'

        # Cria o socket UDP apenas se não estiver criado
        if self.client_socket is None:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Envia requisição para o servidor
        self.client_socket.sendto(self.FILE_REQUEST.encode(), (self.SERVER_HOST, self.SERVER_PORT))
        print(f'Requisição enviada para o servidor pelo Cliente {self.client_id}.')
        
        # Inicia a thread de recebimento apenas se não estiver ativa
        if not self.thread_receive.is_alive():
            self.thread_receive.start()

    # Função para enviar o ACK para o servidor
    def enviar_ack(self, seq_num, server_address):
        ack = f'ACK {seq_num}'.encode()
        self.client_socket.sendto(ack, server_address)

    
    # Função para calcular o checksum de uma string
    def calcular_checksum(data):
        checksum = hashlib.sha256(data).digest()
        return checksum

    def receive_response(self):
        # Recebe o nome do arquivo a partir da solicitação
        nome_arquivo = self.FILE_NAME

        # Extrai a extensão do arquivo solicitado na requisição
        extensao = self.FILE_REQUEST.split(".")[-1]
        nome_arquivo = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{self.client_id}_{nome_arquivo}.{extensao}"

        # Verifica se o diretório existe, se não existir, cria-o
        if not os.path.exists("filesReceived"):
            os.makedirs("filesReceived")

        # Caminho completo para salvar o arquivo recebido
        caminho_arquivo = f"filesReceived/{nome_arquivo}"
        num_bytes = 0

        with open(caminho_arquivo, 'wb') as file:
            seq_num = 0
            while True:
                try:
                    pacote, server_address = self.client_socket.recvfrom(32768)
                except ConnectionResetError:
                    print('Erro: Conexão com o servidor foi interrompida inesperadamente.')
                    break
                
                if len(pacote) == 0:
                    print('Recebida mensagem de finalização do servidor.')
                    break  # Encerra o loop se o tamanho do pacote for zero (final da transmissão)
                
                # Divide o pacote em checksum e dados
                checksum_recebido = pacote[:32]
                dados = pacote[32:]
                
                # Calcula o checksum apenas para os dados
                checksum_calculado = calcular_checksum(dados)
                
                # Verifica se o checksum recebido coincide com o calculado
                if checksum_recebido == checksum_calculado:
                    # Escreve os dados recebidos no arquivo
                    file.write(dados)
                    num_bytes += len(dados)  # Atualiza a quantidade total de bytes recebidos

                    # Envia o ACK para o servidor
                    self.enviar_ack(seq_num, server_address)
                    seq_num += 1
                else:
                    print('Erro: Checksum incorreto. Dados corrompidos. Descartando pacote.')

        self.status_label.configure(text=f"Status Cliente {self.client_id}: Recebidos {num_bytes/1024} Kbytes.")
        print(f'Arquivo recebido salvo em: {caminho_arquivo}')

        # Fecha o socket após receber todos os pacotes
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None

# Função para calcular o checksum de uma string
def calcular_checksum(data):
    checksum = hashlib.sha256(data).digest()
    return checksum

if __name__ == "__main__":
    janela = tk.Tk()
    janela.title("Gerenciador de Clientes")

    # Criar três instâncias de ClientGUI como exemplo
    clients = []
    for i in range(1, 8):
        clients.append(ClientGUI(janela, i))

    # Iniciando o loop principal da interface gráfica
    janela.mainloop()
