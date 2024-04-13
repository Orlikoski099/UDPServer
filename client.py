import tkinter as tk
import threading
import socket
import os
from datetime import datetime

class ClientGUI:
    def __init__(self, master, client_id):
        self.master = master
        self.client_id = client_id

        # Configurações do cliente
        self.SERVER_HOST = '127.0.0.1'  # Endereço IP do servidor
        self.SERVER_PORT = 12345        # Porta do servidor
        self.FILE_REQUEST = ''          # Requisição de arquivo inicialmente vazia
        self.FILE_NAME = f'arquivo_{client_id}'

        # Criação do socket UDP
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

        # Envia requisição para o servidor
        self.client_socket.sendto(self.FILE_REQUEST.encode(), (self.SERVER_HOST, self.SERVER_PORT))
        print(f'Requisição enviada para o servidor pelo Cliente {self.client_id}.')
        if not self.thread_receive.is_alive():
            self.thread_receive.start()

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
            while True:
                pacote, server_address = self.client_socket.recvfrom(1024)
                if len(pacote) == 0:
                    print('Recebida mensagem de finalização do servidor.')
                    break  # Encerra o loop se o tamanho do pacote for zero (final da transmissão)
                
                # Escreve os dados recebidos no arquivo
                file.write(pacote)

                # Atualiza a label com o número de bytes recebidos
                num_bytes += len(pacote)

        self.status_label.configure(text=f"Status Cliente {self.client_id}: Recebidos {num_bytes/1024} Kbytes.")
        print(f'Arquivo recebido salvo em: {caminho_arquivo}')

        # Fechar o socket no final
        self.client_socket.close()

if __name__ == "__main__":
    janela = tk.Tk()
    janela.title("Gerenciador de Clientes")

    # Criar três instâncias de ClientGUI como exemplo
    clients = []
    for i in range(1, 4):
        clients.append(ClientGUI(janela, i))

    # Iniciando o loop principal da interface gráfica
    janela.mainloop()
