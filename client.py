import pickle
import socket
from embarcacao import Embarcacao

HOST = 'localhost'
PORT = 12397

#---------Socket cliente----------
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as n:
    n.connect((HOST, PORT)) 
#---------------------------------


    #variáveis

    tiros = {}
    matriz = [[0 for x in range(10)] for y in range(10)]
    tamanhoResposta = 4096

    msgSuaVez = "Sua vez de jogar"
    msgTurnoOp = "Turno do oponente"

    embarcacoes = {0: Embarcacao('\033[37mPorta-Avião\033[m', 5, None), 1: Embarcacao('\033[32mNavio-Tanque\033[m', 4, None), 2: Embarcacao('\033[31mFragata\033[m', 4, None), 3: Embarcacao('Contra Torpedeiro', 3, None), 4: Embarcacao('Contra Torpedeiro', 3, None), 5: Embarcacao('Contra Torpedeiro', 3, None), 6: Embarcacao('Submarino', 2, None), 7: Embarcacao('Submarino', 2, None), 8: Embarcacao('Submarino', 2, None), 9: Embarcacao('Submarino', 2, None)}

    def tabuleiro():
        print("   ", " ".join([str(a) for a in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]))
        print("   ", "_".join(["_"] * 10))
        x = 0
        for linha in matriz:
            print(x, "|", ' '.join([str(a) for a in linha]))
            x+=1

    def validarEntrada(entrada):
        return entrada >= 0 and entrada <= 9

    def executarTiro():
        while True:
            linha = -1
            coluna = -1
            while True:
                try:
                    linha = int(input('Insira a linha que deseja atirar[0 - 9]: '))
                except ValueError:
                    linha = 99
                if validarEntrada(linha):
                    break
                else:
                    print("Tiro invalido entre com o valor novamente.")

            while True:
                try:
                    coluna = int(input('Insira a coluna da linha em que deseja atirar tiro[0 - 9]: '))
                except ValueError:
                    coluna = 99
                if validarEntrada(coluna):
                    break
                else:
                    print("Tiro invalido entre com o valor novamente")

            if linha in tiros.keys() and coluna in tiros[linha]:
                print("Você já atirou nessa posição! Tente novamente")
            else:
                if linha not in tiros.keys():
                    tiros[linha] = []
                tiros[linha] = tiros[linha] + [coluna]
                break
        return (linha, coluna)

    def validarTamanho(entrada, tamanho):
        return (entrada + tamanho) <= 9

    def posicionarEmbarcacao(embarcacao):
        print("A embarcação ", embarcacao.tipo, " de tamanho ", embarcacao.tamanho, " deve ser posicionada no tabuleiro")
        while True:
            embarcacao.orientacao = input("Escolha a orientação da embarcação Vertical(v), Horizontal(h): ")
            if embarcacao.orientacao in ['v', 'h']:
                break
            else:
                print('Entrada incorreta tente novamente.')
        while True:
            try:
                linha = int(input("Insira a linha em que deseja posicionar sua embarcação[0 - 9]: "))
            except ValueError:
                linha = 99
            if validarEntrada(linha) and (embarcacao.orientacao == 'h' or (embarcacao.orientacao == 'v' and validarTamanho(linha, embarcacao.tamanho))):
                break
            else:
                print('Entrada incorreta tente novamente.')
        while True:
            try:
                coluna = int(input("Insira a coluna em que deseja posicionar sua embarcação[0 - 9]: "))
            except ValueError:
                coluna = 99        
            if validarEntrada(coluna) and (embarcacao.orientacao == 'v' or (embarcacao.orientacao == 'h' and validarTamanho(coluna, embarcacao.tamanho))):
                break
            else:
                print('Entrada incorreta tente novamente.')
        return (linha, coluna, embarcacao)

    def ReceberEPrintarMensagem():
        msg = n.recv(tamanhoResposta)
        print(msg)
        print(msg.decode('utf-8', errors='replace'))

    ReceberEPrintarMensagem()
    ReceberEPrintarMensagem()

    for i in range(0, 3):
        while True:
            posicao = posicionarEmbarcacao(embarcacoes[i])
            b = pickle.dumps(posicao)
            n.send(b)
            resposta = n.recv(tamanhoResposta)
            posicaoValida = pickle.loads(resposta)
            if posicaoValida:
                break
            else:
                print('Há uma embarcação posicionado na posição: ' + '['+str(posicao[0])+']' + '[' +str(posicao[1])+']')
            
    ReceberEPrintarMensagem()
    ReceberEPrintarMensagem()

    while True:
        resposta = n.recv(tamanhoResposta)
        minhaVez = pickle.loads(resposta)    
        if minhaVez:
            print(msgSuaVez)
            tupla = executarTiro()
            envio = pickle.dumps(tupla)
            n.send(envio)
            resposta = n.recv(tamanhoResposta)
            acertou, linha, coluna = pickle.loads(resposta)
            if acertou:
                matriz[linha][coluna] = 'X'
                
                print("Você atingiu uma embarcação!")
            else:
                matriz[linha][coluna] = '~'
                
                print("Você acertou a água!")

            tabuleiro()
        else:
            print(msgTurnoOp)
            resposta = n.recv(tamanhoResposta)
            acertou, linha, coluna = pickle.loads(resposta)
            if acertou:
                print('O oponente acertou sua embarcação na posição: ' + str(linha) + ', ' + str(coluna))
            else:
                print('O opoente disparou na água na posição: ' + str(linha) + ', ' + str(coluna))

        resposta = n.recv(tamanhoResposta)    
        estadoJogo, ganhador = pickle.loads(resposta)

        if estadoJogo == True:
            if ganhador:
                print("Você ganhou, parabéns!")
                break
            else:
                print("Você perdeu!")
                break
        else:
            n.send("Continuar".encode('utf-8'))

    n.close()
