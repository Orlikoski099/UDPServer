import tkinter as tk
import threading
import os

# Função para iniciar o servidor em uma thread separada
def start_server():
    global server_thread
    server_thread = threading.Thread(target=start_server_thread)
    server_thread.start()

# Função para desligar o servidor
def stop_server():
    os.system("taskkill /f /im python.exe")  # Substitua "python.exe" pelo nome do processo do servidor

# Função para iniciar um cliente
def start_client():
    client_thread = threading.Thread(target=start_client_thread)
    client_thread.start()

# Função para iniciar o servidor em um loop infinito (exemplo)
def start_server_thread():
    os.system("start cmd /k python server.py")  # Comando para iniciar o servidor

# Função para iniciar o cliente em um loop infinito (exemplo)
def start_client_thread():
    os.system("start cmd /k python client.py")  # Comando para iniciar o cliente

# Interface gráfica para o servidor e cliente
root = tk.Tk()
root.title("Controle do Servidor e Cliente")

# Botão para iniciar o servidor
start_server_button = tk.Button(root, text="Iniciar Servidor", command=start_server)
start_server_button.pack()

# Botão para parar o servidor
stop_server_button = tk.Button(root, text="Parar Servidor", command=stop_server)
stop_server_button.pack()

# Botão para iniciar um cliente
start_client_button = tk.Button(root, text="Iniciar Cliente", command=start_client)
start_client_button.pack()

# Iniciando o loop principal da interface gráfica
root.mainloop()
