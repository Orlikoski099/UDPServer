class OrlikoskiProtocol:
    def __init__(self):
        pass

    def processar_requisicao(self, mensagem):
        # Verifica se a mensagem está no formato correto de requisição
        if mensagem.startswith("OBTER "):
            nome_arquivo = mensagem.split(" ")[1]
            return nome_arquivo
        elif mensagem.startswith("ACK "):
            # Processa a mensagem de ACK recebida
            # Extrai o número do pacote recebido do ACK
            numero_pacote = mensagem.split(" ")[1]
            # Aqui você pode adicionar a lógica para lidar com o ACK recebido, se necessário
            return f"ACK {numero_pacote}"
        else:
            return "Erro: Formato de requisição inválido."

    def processar_resposta_arquivo(self, dados_arquivo):
        # Verifica se os dados do arquivo foram recebidos
        if not dados_arquivo:
            return "Erro: Dados do arquivo não recebidos."

        # Retorna os dados do arquivo para o servidor
        return dados_arquivo

    def processar_confirmacao(self, mensagem):
        # Processar a mensagem de confirmação (se necessário)
        return mensagem

    def processar_erro(self, mensagem):
        # Processar a mensagem de erro (se necessário)
        return mensagem
