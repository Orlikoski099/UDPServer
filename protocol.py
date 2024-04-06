class OrlikoskiProtocol:
    def __init__(self):
        pass

    def processar_requisicao(self, mensagem):
        # Verifica se a mensagem está no formato correto
        if not mensagem.startswith("OBTER "):
            print('Ta fazendo merda, guerreiro')
            return "Erro: Formato de requisição inválido."

        # Obtém o nome do arquivo da requisição (incluindo a barra)
        arquivo_requisitado = mensagem.split(" ")[1]

        # Retorna a resposta para ser enviada de volta ao cliente
        return arquivo_requisitado

        ...

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
