from jogo import Jogo
import socket
from threading import Thread
import pickle

HOST= "localhost"
PORT = 12397

#-----------------Servidor---------------
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
#-----------------Servidor---------------
    print("\033[32mServidor iniciado\033[m")
    print("Aguardando jogadores...")

    #Variáveis do jogo
    jogadorUm = 1
    jogadorDois = 2
    socket = 0
    addr = 1
    jogador = 2
    ip = 0
    porta = 1
    totalNavios = 3
    tamanhoResposta = 4096
    acertosNecessarios = 13

    jogadores = {} #dicionário de jogadores

    msgEspera = "Aguardando outro jogador..."
    msgInicio = "\033[33m~~~ B A T A L H A   N A V A L ~~~\033[m"

    msgEsperaNavios = "Aguardando outro jogador posicionar seus navios"
    msgNaviosPosicionados = 'Navios posicionados, iniciando partida'


    def esperaConexao(idJogador):
        socket_jogador, addr_jogador = s.accept()
        jogadores[idJogador] = (socket_jogador, addr_jogador, Jogo(idJogador))
        enviarMensagemParaJogador(idJogador, msgEspera)
        print('Conectado a: ' + jogadores[idJogador][addr][ip] + ': ' + str(jogadores[idJogador][addr][porta]))

    def posicionandoNavios(idJogador):
        while len(jogadores[idJogador][jogador].navios) < totalNavios:
            b = jogadores[idJogador][socket].recv(tamanhoResposta)
            linha, coluna, navio = pickle.loads(b)
            posicaoValida = jogadores[idJogador][jogador].posicionarNavio(linha, coluna, navio.orientacao, navio.tamanho)
            if posicaoValida:
                jogadores[idJogador][jogador].navios.append(navio)

            enviarMensagemParaJogador(idJogador, posicaoValida)
        
        enviarMensagemParaJogador(idJogador, msgEsperaNavios)
        print("Jogador " + str(idJogador) + " posicionou os navios.")

    def enviarMsgParaTodos(mensagem):
        if type(mensagem) is str:
            for j in jogadores.values():
                j[socket].send(mensagem.encode('utf-8'))
        else:
            for j in jogadores.values():
                msgBytes = pickle.dumps(mensagem)
                j[socket].send(msgBytes)

    def enviarMensagemParaJogador(idJogador, mensagem):
        if type(mensagem) is str:
            jogadores[idJogador][socket].send(mensagem.encode('utf-8'))
        else:
            msgBytes = pickle.dumps(mensagem)
            jogadores[idJogador][socket].send(msgBytes)

    def executarRodada(idJogadorVez, idJogadorEsperando):
        enviarMensagemParaJogador(idJogadorVez, True)
        enviarMensagemParaJogador(idJogadorEsperando, False)
        envioJogador = jogadores[idJogadorVez][socket].recv(tamanhoResposta)
        linha, coluna = pickle.loads(envioJogador)
        acertou = jogadores[idJogadorEsperando][jogador].verificarTiro(linha, coluna)
        if acertou:
            enviarMsgParaTodos((True, linha, coluna))
        else:
            enviarMsgParaTodos((False, linha, coluna))

    def esperaJogadores(idJogador):
        envioJogador = jogadores[idJogador][socket].recv(tamanhoResposta)

    esperaConexao(jogadorUm)
    esperaConexao(jogadorDois)

    print("Preparando para iniciar a partida...")

    enviarMsgParaTodos(msgInicio)

    t1 = Thread(target=posicionandoNavios, args=(jogadorUm,))
    t2 = Thread(target=posicionandoNavios, args=(jogadorDois,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print(msgNaviosPosicionados)
    enviarMsgParaTodos(msgNaviosPosicionados)

    turno = jogadorUm
    envioJogador = None

    while True:
        if turno == jogadorUm:
            executarRodada(jogadorUm, jogadorDois)
            turno = jogadorDois
        else:
            executarRodada(jogadorDois, jogadorUm)
            turno = jogadorUm

        #verificar se há vencedor
        if jogadores[jogadorUm][jogador].partesAbatidas == acertosNecessarios:
            print("Finalizado")
            mensagemJogadorUm = (True, False)
            mensagemJogadorDois = (True, True)
            
            enviarMensagemParaJogador(jogadorUm, mensagemJogadorUm)
            enviarMensagemParaJogador(jogadorDois, mensagemJogadorDois)
            break

        elif jogadores[jogadorDois][jogador].partesAbatidas == acertosNecessarios:
            print("Finalizado")
            mensagemJogadorUm = (True, True)
            mensagemJogadorDois = (True, False)
            
            enviarMensagemParaJogador(jogadorUm, mensagemJogadorUm)
            enviarMensagemParaJogador(jogadorDois, mensagemJogadorDois)
            break
        else:
            enviarMsgParaTodos((False, False))

            t1 = Thread(target=esperaJogadores, args=(jogadorUm,))
            t2 = Thread(target=esperaJogadores, args=(jogadorDois,))

            t1.start()
            t2.start()

            t1.join()
            t2.join()

    jogadores[jogadorUm][socket].close()
    jogadores[jogadorDois][socket].close()