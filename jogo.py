class Jogo:
    
    def __init__(self, id):
        self.id = id
        self.navios = []
        self.campo = [[0 for x in range(10)] for y in range(10)]
        self.tiros = []
        self.naviosAbatidos = []
        self.partesAbatidas = 0


    def verificarTiro(self, linha, coluna):
        if(self.campo[linha][coluna] == 1):
            self.partesAbatidas += 1            
            return True
        else:
            return False

    def posicionarNavio(self, linha, coluna, direcao, tamanho):
        if(direcao == 'h'):
            if(coluna + tamanho > 9):
                return False
            while tamanho > 0:
                if self.campo[linha][coluna] == 1:
                    return False
                self.campo[linha][coluna] = 1
                tamanho = tamanho - 1
                coluna = coluna + 1
        else:
            if(linha + tamanho > 9):
                return False
            while tamanho > 0:
                if self.campo[linha][coluna] == 1:
                    return False
                self.campo[linha][coluna] = 1
                linha = linha + 1
                tamanho = tamanho - 1
        return True