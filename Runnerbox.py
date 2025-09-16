import pgzero
import math
import random
from pygame import Rect

# constantes do game

WIDTH = 800
HEIGHT = 600

TITULO = "Runnerbox"
GRAVIDADE = 0.5
PULO = -12
VELOCIDADE = 5

# Estados do game
MENU = 0
JOGANDO = 1
GAME_OVER = 2
LEVEL_COMPLETO = 3

# Estado do som
SOM_LIGADO = True

# Estado do game
estado = MENU

# Posição do mouse
mouse = (0, 0)

# Pontuação
nivel_atual = 1
bandeiras_coletadas = 0

# Criar heroi
heroi = Actor('heroi_parado_1')
heroi.x = 100
heroi.y = 300
heroi.velocidade_y = 0
heroi.no_chao = False
heroi.direcao = 1  # 1 para direita, -1 para esquerda
heroi.animacao_frame = 0
heroi.animacao_velocidade = 0.2
heroi.estado = 'parado'  # 'parado', 'correndo', 'pulando'

# Criar plataformas
plataformas = [
    Rect(0, HEIGHT - 40, WIDTH, 40),  # Chão
    Rect(200, 450, 150, 20),  # Plataforma 1
    Rect(400, 350, 150, 20),  # Plataforma 2
    Rect(600, 250, 150, 20),  # Plataforma 3
    Rect(200, 150, 150, 20)   # Plataforma 4
]

# Criar bandeira
bandeira = Actor('bandeira_off')
bandeira.x = 275
bandeira.y = 130
bandeira.coletada = False

# Criar inimigos
inimigos = []
for i in range(4):
    inimigo = Actor('inimigo_parado_1')
    inimigo.x = 300 + i * 200

    # Posicionar inimigo em uma plataforma
    if i == 0:
        inimigo.y = HEIGHT - 150 - inimigo.height / 2
    elif i == 1:
        inimigo.y = 350 - inimigo.height / 2
    elif i == 2:
        inimigo.y = 250 - inimigo.height / 2
    elif i == 3:
        inimigo.y = 150 - inimigo.height / 2
        inimigo.x = 250  # Colocar o último inimigo perto da bandeira
    inimigo.direcao = -1  # Inimigo começa indo para a esquerda
    inimigo.animacao_frame = 0
    inimigo.animacao_velocidade = 0.1
    inimigo.estado = 'parado'  # 'parado', 'andando'
    inimigo.patrulha_inicio = inimigo.x - 50
    inimigo.patrulha_fim = inimigo.x + 50
    inimigo.acrescentar(inimigo)

    # Posições dos botões do menu
    iniciar_botao_rect = Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 40)
    som_botao_rect = Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 40)
    sair_botao_rect = Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 40)

def atualizar_heroi():
    global game_estado, som_ligado, bandeiras_coletadas

    if game_estado == MENU:
        # A posição do mouse é tratada no evento on_mouse_move
        pass

    elif game_estado == JOGANDO:
        atualizar_heroi()
        atualizar_inimigos()
        verificar_colisoes()
        verificar_bandeira_coletada()

    elif game_estado == LEVEL_COMPLETO:
        # A posição do mouse é tratada no evento on_mouse_move
        pass

def atualizar_heroi():
    global heroi

    # Lidar com movimento contínuo
    if keyboard.left:
        heroi.x -= VELOCIDADE
        heroi.direcao = -1
        if heroi.no_chao:
            heroi.estado = 'correndo'
    elif keyboard.right:
        heroi.x += VELOCIDADE
        heroi.direcao = 1
        if heroi.no_chao:
            heroi.estado = 'correndo'
    else:
        if heroi.no_chao:
            heroi.estado = 'parado'

    # Aplicar gravidade
    heroi.velocidade_y += GRAVIDADE
    heroi.y += heroi.velocidade_y

    # Verificar colisão com plataformas
    heroi.no_chao = False
    for plataforma in plataformas:
        if heroi.colidir(plataforma):
            if heroi.velocidade_y > 0 and heroi.y < plataforma.y:
                heroi.y = plataforma.y - heroi.height // 2
                heroi.velocidade_y = 0
                heroi.no_chao = True

    # Manter heroi dentro da tela
    if heroi.x < 0:
        heroi.x = 0
    elif heroi.x > WIDTH:
        heroi.x = WIDTH

    # Atualizar animações do heroi
    heroi.animacao_frame += heroi.animacao_velocidade
    if heroi.estado == 'parado':
        if heroi.animacao_frame >= 4:
            frame = int(heroi.animacao_frame) % 1 + 1
            heroi.image = f'heroi_parado_{frame}'
    elif heroi.estado == 'correndo':
        frame = int(heroi.animacao_frame) % 2 + 1
        heroi.image = f'heroi_correndo_{frame}'
    elif heroi.estado == 'pulando':
        heroi.image = 'heroi_pulando_1'

def atualizar_inimigos():
    global inimigos

    for inimigo in inimigos:
        # Comportamento de patrulha
        inimigo.x += VELOCIDADE * 0.5 * inimigo.direcao

        # Inverter direção nos limites da patrulha
        if inimigo.x <= inimigo.patrulha_inicio or inimigo.x >= inimigo.patrulha_fim:
            inimigo.direcao *= -1

        # Atualizar animações do inimigo
        inimigo.animacao_frame += inimigo.animacao_velocidade
        if inimigo.estado == "parado":
                frame = int(inimigo.animacao_frame) % 1 + 1
                inimigo.image = f'inimigo_parado_{frame}'
        elif inimigo.estado == "correndo":
                frame = int(inimigo.animacao_frame) % 2 + 1
                inimigo.image = f'inimigo_correndo_{frame}'


def verificar_colisoes():
    global game_estado

    # Verificar se o heroi colidiu com algum inimigo
    for inimigo in inimigos:
        if heroi.colidir(inimigo):
            distancia = ((heroi.x - inimigo.x) ** 2 + (heroi.y - inimigo.y) ** 2) ** 0.5
            if distancia < (heroi.x + inimigo.width / 2) * 0.9:
                if heroi.velocidade_y > 0 and heroi.y < inimigo.y:
                    # Herói pula sobre o inimigo
                    heroi.velocidade_y = PULO * 0.7
                    if SOM_LIGADO:
                        try:
                            sons.pulo.play()
                        except:
                            pass
                    # Remover inimigo derrotado
                    inimigos.remove(inimigo)
                else:
                    # Herói colidiu com o inimigo
                    game_estado = GAME_OVER
                    if SOM_LIGADO:
                        try:
                            sons.game_over.play()
                        except:
                            pass

def verificar_bandeira_coletada():
    global game_estado, bandeiras_coletadas

    # Verificar se o heroi coletou a bandeira
    if not bandeira.coletada and heroi.colidir(bandeira):
        distancia = ((heroi.x - bandeira.x) ** 2 + (heroi.y - bandeira.y) ** 2) ** 0.5
        if distancia < (heroi.x + bandeira.width / 2) * 0.7:
            bandeira.coletada = True
            bandeira.image = 'bandeira_vermelha_a'
            bandeiras_coletadas += 1

            if SOM_LIGADO:
                try:
                    sons.bandeira.play()
                except:
                    pass

            if bandeiras_coletadas >= 1:
                game_estado = LEVEL_COMPLETO
