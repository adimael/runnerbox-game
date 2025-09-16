# AlienHunter - um jogo de plataforma
#
# @author Adimael S.
# @version 1.0.0

import pgzero
from pgzero.actor import Actor
import math
import random
from pygame import Rect

# constantes do game

WIDTH = 800
HEIGHT = 600

TITLE = "AlienHunter Game"
NEW_GAME = "INICIAR JOGO"
SOUND_ON = "SOM: LIGADO"
SOUND_OFF = "SOM: DESLIGADO"
EXIT = "SAIR"
GAME_OVER_TEXT = "GAME OVER"
LEVEL_COMPLETE_TEXT = "NÍVEL COMPLETO!"
SCORE_TEXT = "Bandeiras Coletadas: {}"
GRAVITY = 0.5
JUMP_FORCE = -12
SPEED = 5

# Estados do game
MENU = 0
PLAYING = 1
GAME_OVER = 2
LEVEL_COMPLETE = 3

# Estado do som
SOUND_ON_STATE = True

# Estado do game
state = MENU

# Posição do mouse
mouse = (0, 0)

# Pontuação
current_level = 1
flags_collected = 0

# Criar heroi
hero = Actor('hero_idle_1')
hero.x = 100
hero.y = 300
hero.velocity_y = 0
hero.on_ground = False
hero.direction = 1  # 1 para direita, -1 para esquerda
hero.animation_frame = 0
hero.animation_speed = 0.2
hero.state = 'idle'  # 'idle', 'running', 'jumping'

# Criar plataformas
platforms = [
    Rect(0, HEIGHT - 40, WIDTH, 40),  # Chão
    Rect(200, 450, 150, 20),  # Plataforma 1
    Rect(400, 350, 150, 20),  # Plataforma 2
    Rect(600, 250, 150, 20),  # Plataforma 3
    Rect(200, 150, 150, 20)   # Plataforma 4
]

# Criar bandeira
flag = Actor('flag_off')
flag.x = 275
flag.y = 130
flag.collected = False

# Posições dos botões do menu
start_button_rect = Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 40)
sound_button_rect = Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 40)
exit_button_rect = Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 40)

# Criar inimigos
enemies = []
for i in range(4):
    enemy = Actor('enemy_idle_1')
    enemy.x = 300 + i * 200

    # Posicionar inimigo em uma plataforma
    if i == 0:
        enemy.y = HEIGHT - 150 - enemy.height / 2
    elif i == 1:
        enemy.y = 350 - enemy.height / 2
    elif i == 2:
        enemy.y = 250 - enemy.height / 2
    elif i == 3:
        enemy.y = 150 - enemy.height / 2
        enemy.x = 250  # Colocar o último inimigo perto da bandeira
    enemy.direction = -1  # Inimigo começa indo para a esquerda
    enemy.animation_frame = 0
    enemy.animation_speed = 0.1
    enemy.state = 'idle'  # 'idle', 'walking'
    enemy.patrol_start = enemy.x - 50
    enemy.patrol_end = enemy.x + 50
    enemies.append(enemy)

def update_game():
    global state, SOUND_ON_STATE, flags_collected

    if state == MENU:
        # A posição do mouse é tratada no evento on_mouse_move
        pass

    elif state == PLAYING:
        update_hero()
        update_enemies()
        check_collisions()
        check_flag_collected()

    elif state == LEVEL_COMPLETE:
        # A posição do mouse é tratada no evento on_mouse_move
        pass

def update_hero():
    global hero

    # Lidar com movimento contínuo
    if keyboard.left:
        hero.x -= SPEED
        hero.direction = -1
        if hero.on_ground:
            hero.state = 'running'
    elif keyboard.right:
        hero.x += SPEED
        hero.direction = 1
        if hero.on_ground:
            hero.state = 'running'
    else:
        if hero.on_ground:
            hero.state = 'idle'

    # Aplicar gravidade
    hero.velocity_y += GRAVITY
    hero.y += hero.velocity_y

    # Verificar colisão com plataformas
    hero.on_ground = False
    for platform in platforms:
        if hero.colliderect(platform):
            if hero.velocity_y > 0 and hero.y < platform.y:
                hero.y = platform.y - hero.height // 2
                hero.velocity_y = 0
                hero.on_ground = True

    # Manter heroi dentro da tela
    if hero.x < 0:
        hero.x = 0
    elif hero.x > WIDTH:
        hero.x = WIDTH

    # Atualizar animações do heroi
    hero.animation_frame += hero.animation_speed
    if hero.state == 'idle':
        # Only hero_idle_1 is available
        hero.image = 'hero_idle_1'
    elif hero.state == 'running':
        # Alternate between hero_run_1 and hero_run_2
        frame = int(hero.animation_frame) % 2 + 1
        hero.image = f'hero_run_{frame}'
    elif hero.state == 'jumping':
        hero.image = 'hero_jump_1'

def update_enemies():
    global enemies

    for enemy in enemies:
        # Comportamento de patrulha
        enemy.x += SPEED * 0.5 * enemy.direction

        # Inverter direção nos limites da patrulha
        if enemy.x <= enemy.patrol_start or enemy.x >= enemy.patrol_end:
            enemy.direction *= -1

        # Atualizar animações do inimigo
        enemy.animation_frame += enemy.animation_speed
        if enemy.state == "idle":
            # Alternate between enemy_idle_1 (only one available)
            enemy.image = 'enemy_idle_1'
        elif enemy.state == "walking":
            # Alternate between enemy_run_1 and enemy_run_2
            frame = int(enemy.animation_frame) % 2 + 1
            enemy.image = f'enemy_run_{frame}'


def check_collisions():
    global state

    # Verificar se o heroi colidiu com algum inimigo
    for enemy in enemies:
        if hero.colliderect(enemy):
            distance = ((hero.x - enemy.x) ** 2 + (hero.y - enemy.y) ** 2) ** 0.5
            if distance < (hero.width / 2 + enemy.width / 2) * 0.9:
                if hero.velocity_y > 0 and hero.y < enemy.y:
                    # Herói pula sobre o inimigo
                    hero.velocity_y = JUMP_FORCE * 0.7
                    if SOUND_ON_STATE:
                        try:
                            sounds.jump.play()
                        except:
                            pass
                    # Remover inimigo derrotado
                    enemies.remove(enemy)
                else:
                    # Herói colidiu com o inimigo
                    state = GAME_OVER
                    if SOUND_ON_STATE:
                        try:
                            sounds.hurt.play()
                        except:
                            pass

def check_flag_collected():
    global state, flags_collected

    # Verificar se o heroi coletou a bandeira
    if not flag.collected and hero.colliderect(flag):
        distance = ((hero.x - flag.x) ** 2 + (hero.y - flag.y) ** 2) ** 0.5
        if distance < (hero.width / 2 + flag.width / 2) * 0.7:
            flag.collected = True
            flag.image = 'flag_red_a'
            flags_collected += 1

            if SOUND_ON_STATE:
                try:
                    sounds.coin.play()
                except:
                    pass

            if flags_collected >= 1:
                state = LEVEL_COMPLETE

def on_key_down(key):
    global hero
    
    if state == PLAYING:
        # Handle jumping
        if key == keys.SPACE or key == keys.UP:
            if hero.on_ground:
                hero.velocity_y = JUMP_FORCE
                hero.on_ground = False
                hero.state = 'jumping'
                if SOUND_ON_STATE:
                    try:
                        sounds.jump.play()
                    except:
                        pass
        elif key in (keys.LEFT, keys.RIGHT):
            hero.state = 'running'

def on_mouse_move(pos):
    global mouse
    mouse = pos

def on_mouse_down(pos):
    global state, SOUND_ON_STATE, hero, enemies, flags_collected

    if state == MENU:
        if start_button_rect.collidepoint(pos):
            state = PLAYING
            flags_collected = 0
            flag.collected = False
            flag.image = 'flag_off'
        elif sound_button_rect.collidepoint(pos):
            SOUND_ON_STATE = not SOUND_ON_STATE
        elif exit_button_rect.collidepoint(pos):
            exit()
    elif state == GAME_OVER or state == LEVEL_COMPLETE:
        hero.x = 100
        hero.y = 300
        hero.velocity_y = 0
        hero.on_ground = False
        hero.direction = 1
        hero.state = 'idle'

        enemies.clear()
        for i in range(4):
            enemy = Actor('enemy_idle_1')
            enemy.x = 300 + i * 200

            if i == 0:
                enemy.y = HEIGHT - 150 - enemy.height / 2
            elif i == 1:
                enemy.y = 350 - enemy.height / 2
            elif i == 2:
                enemy.y = 250 - enemy.height / 2
            elif i == 3:
                enemy.y = 150 - enemy.height / 2
                enemy.x = 250  # Colocar o último inimigo perto da bandeira

            enemy.direction = -1
            enemy.animation_frame = 0
            enemy.animation_speed = 0.1
            enemy.state = 'idle'
            enemy.patrol_start = enemy.x - 50
            enemy.patrol_end = enemy.x + 50
            enemies.append(enemy)

        # Reiniciar bandeira
        flag.collected = False
        flag.image = 'flag_off'

        # Retornar ao menu
        state = MENU

def display_menu():
    screen.clear()
    screen.fill((50, 50, 100)) # Fundo azul

    # Carregar título
    screen.draw.text(TITLE, center=(WIDTH // 2, HEIGHT // 4), fontsize=64, color="white")

    # Exibir botões
    if start_button_rect.collidepoint(mouse):
        screen.draw.filled_rect(start_button_rect, (100, 200, 100))
    else:
        screen.draw.filled_rect(start_button_rect, (0, 150, 0)) # verde escuro
    screen.draw.text(NEW_GAME, center=start_button_rect.center, fontsize=36, color="white")

    if sound_button_rect.collidepoint(mouse):
        screen.draw.filled_rect(sound_button_rect, (100, 200, 100))
    else:
        screen.draw.filled_rect(sound_button_rect, (0, 0, 150)) # azul escuro
    sound_text = SOUND_ON if SOUND_ON_STATE else SOUND_OFF
    screen.draw.text(sound_text, center=sound_button_rect.center, fontsize=36, color="white")

    if exit_button_rect.collidepoint(mouse):
        screen.draw.filled_rect(exit_button_rect, (200, 100, 100))
    else:
        screen.draw.filled_rect(exit_button_rect, (150, 0, 0)) # vermelho escuro
    screen.draw.text(EXIT, center=exit_button_rect.center, fontsize=36, color="white")

def display_game():
    screen.clear()
    screen.fill((135, 206, 235))  # Fundo azul claro

    # Desenhar plataformas
    for platform in platforms:
        screen.draw.filled_rect(platform, (0, 255, 0))  # Verde

    # Desenhar bandeira
    flag.draw()

    # Desenhar heroi
    hero.draw()

    # Desenhar inimigos
    for enemy in enemies:
        enemy.draw()

    # Exibir pontuação
    screen.draw.text(SCORE_TEXT.format(flags_collected), topright=(WIDTH - 10, 10), fontsize=30, color="black")

def display_game_over():
    screen.clear()
    screen.fill((0, 0, 0))  # Fundo preto

    screen.draw.text(GAME_OVER_TEXT, center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="red")
    screen.draw.text("Clique para retornar ao menu", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=30, color="white")

def display_level_complete():
    screen.clear()
    screen.fill((0, 0, 0))  # Fundo preto

    screen.draw.text(LEVEL_COMPLETE_TEXT, center=(WIDTH // 2, HEIGHT // 2), fontsize=60, color="yellow")
    screen.draw.text("Parabéns! Você coletou a bandeira.", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=30, color="white")
    screen.draw.text("Clique para retornar ao menu", center=(WIDTH // 2, HEIGHT // 2 + 100), fontsize=30, color="white")

def draw():
    if state == MENU:
        display_menu()
    elif state == PLAYING:
        display_game()
    elif state == GAME_OVER:
        display_game_over()
    elif state == LEVEL_COMPLETE:
        display_level_complete()

def update():
    update_game()

# Executar o jogo