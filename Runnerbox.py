import pgzero
import math
import random
from pygame import Rect

# constantes do game

WIDTH = 800
HEIGHT = 600

TITULO = "Runnerbox"
NEW_GAME = "INICIAR JOGO"
SOUND_ON = "SOM: LIGADO"
SOUND_OFF = "SOM: DESLIGADO"
EXIT = "SAIR"
GAME_OVER_TEXT = "GAME OVER"
LEVEL_COMPLETE_TEXT = "NÍVEL COMPLETO!"
SCORE_TEXT = "Bandeiras Coletadas: {}"
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

def tecla_pressionada(tecla):
    global heroi
    
    if game_estado == JOGANDO:
        if tecla in (teclas.esquerda, teclas.direita):

            heroi.estado = 'correndo'

def tecla_solta(tecla):
    global mouse
    mouse = pos

def mouse_movimento(pos):
    global mouse
    mouse = pos

def mouse_clicado(pos):
    global game_estado, som_ligado, heroi, inimigos, bandeiras_coletadas

    if game_estado == MENU:
        if iniciar_botao_rect.collidepoint(pos):
            game_estado = JOGANDO
            bandeiras_coletadas = 0
            bandeira.coletada = False
            bandeira.image = 'bandeira_off'
            if som_ligado:
                try:
                    sons.iniciar.play()
                except:
                    pass
        elif som_botao_rect.collidepoint(pos):
            som_ligado = not som_ligado
        elif sair_botao_rect.collidepoint(pos):
            exit()
    elif game_estado == GAME_OVER or game_estado == LEVEL_COMPLETO:
        heroi.x = 100
        heroi.y = 300
        heroi.velocidade_y = 0
        heroi.no_chao = False
        heroi.direcao = 1
        heroi.estado = 'parado'

        inimigos.clear()
        for i in range(4):
            inimigo = Actor('inimigo_parado_1')
            inimigo.x = 300 + i * 200

            if i == 0:
                inimigo.y = HEIGHT - 150 - inimigo.height / 2
            elif i == 1:
                inimigo.y = 350 - inimigo.height / 2
            elif i == 2:
                inimigo.y = 250 - inimigo.height / 2
            elif i == 3:
                inimigo.y = 150 - inimigo.height / 2
                inimigo.x = 250  # Colocar o último inimigo perto da bandeira

            inimigo.direcao = -1
            inimigo.animacao_frame = 0
            inimigo.animacao_velocidade = 0.1
            inimigo.estado = 'parado'
            inimigo.patrulha_inicio = inimigo.x - 50
            inimigo.patrulha_fim = inimigo.x + 50
            inimigos.append(inimigo)

        # Reiniciar bandeira
        bandeira.coletada = 0
        bandeira.coletada = False
        bandeira.image = 'bandeira_off'

        # Retornar ao menu
        game_estado = MENU

def exibir_menu():
    screen.clear()
    screen.fill((50, 50, 100)) # Fundo azul

    # Carregar título
    screen.exibir_texto(TITULO, center=(WIDTH // 2, HEIGHT // 4), fontsize=64, color="white")

    # Exibir botões
    if iniciar_botao_rect.collidepoint(mouse):
        screen.draw.filled_rect(iniciar_botao_rect, (100, 200, 100))
    else:
        screen.draw.filled_rect(iniciar_botao_rect, (0, 150, 0)) # verde escuro
        screen.exibir_texto(NEW_GAME, center=iniciar_botao_rect.center, fontsize=36, color="white")

    if som_botao_rect.collidepoint(mouse):
        screen.draw.filled_rect(som_botao_rect, (100, 200, 100))
    else:
        screen.exibir_texto(som_botao_rect, (0, 0, 150)) # azul escuro
        som_texto = SOUND_ON if som_ligado else SOUND_OFF
        screen.exibir_texto(som_texto, center=som_botao_rect.center, fontsize=36, color="white")

    if sair_botao_rect.collidepoint(mouse):
        screen.draw.filled_rect(sair_botao_rect, (200, 100, 100))
    else:
        screen.draw.filled_rect(sair_botao_rect, (150, 0, 0)) # vermelho escuro
        screen.exibir_texto(EXIT, center=sair_botao_rect.center, fontsize=36, color="white")