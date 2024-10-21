import pygame
from pygame.locals import *
from sys import exit
import os
from random import randrange, choice
import sys

pygame.init()
pygame.mixer.init()

if getattr(sys, 'frozen', False):
    diretorio_principal = sys._MEIPASS
else:
    diretorio_principal = os.path.dirname(__file__)

diretorio_imagens = os.path.join(diretorio_principal, 'Dino')
diretorio_sons = os.path.join(diretorio_principal, 'Musicas')

largura = 640
altura = 480
PRETO = (0,0,0)
BRANCO = (255,255,255)
VERMELHO = (255,0,0)
VERDE = (0,255,0)
AZUL = (0,0,255)
CINZA = (105,105,105)

tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Dino Game')

# Carrega a spritesheet
sprite_sheet = pygame.image.load(os.path.join(diretorio_imagens, 'Spritesheet.png')).convert_alpha()


som_colisao = pygame.mixer.Sound(os.path.join(diretorio_sons, 'death_sound.wav'))
som_colisao.set_volume(1)

som_pontuacao = pygame.mixer.Sound(os.path.join(diretorio_sons, 'score_sound.wav'))
som_pontuacao.set_volume(1)

colidiu = False

escolha_obstaculo = choice([0,1])

pontos = 0
velocidade_jogo = 10
meteoro = None


def exibe_mensagem(msg, tamanho, cor):
    fonte = pygame.font.SysFont('comicsansms', tamanho,  True, False)
    mensagem = f'{msg}' 
    texto_formatado = fonte.render(mensagem, True, cor)
    return texto_formatado

def reiniciar_jogo():
    global pontos, velocidade_jogo, colidiu, escolha_obstaculo, meteoro, meteoro_ativo, tempo_vermelho
    pontos = 0
    velocidade_jogo = 10
    colidiu = False
    dino.rect.y = altura - 64 - 96//2
    dino.pulo = False
    dino_voador.rect.x = largura
    cacto.rect.x = largura
    escolha_obstaculo = choice([0,1])
    meteoro = None 
    meteoro_ativo = False  
    tempo_vermelho = -1

class Lua(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((9 * 32, 0), (32, 32)) 
        self.image = pygame.transform.scale(self.image, (32 * 3, 32 * 3))
        self.rect = self.image.get_rect()
        self.rect.x = largura  # A lua começa fora da tela, à direita
        self.rect.y = 50
        self.movendo = False  # Indica se a lua está se movendo

    def iniciar_movimento(self, duracao_cinza):
        self.rect.x = largura  # Reseta a posição da lua
        self.movendo = True  # Ativa o movimento da lua
        self.velocidade_lua = (largura / duracao_cinza) * 1.1  # Define a velocidade da lua com base na duração

    def update(self, tempo_cinza, duracao_cinza):
        if tempo_cinza > 0 and self.movendo:
            self.rect.x -= self.velocidade_lua
            if self.rect.x + self.rect.width < 0:
                self.movendo = False
                self.rect.x = largura  # Reseta a posição para a próxima vez que ela aparecer
        else:
            self.movendo = False  


class Meteoro(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((8 * 32, 0), (32, 32)) 
        self.image = pygame.transform.scale(self.image, (32 * 3, 32 * 3))
        self.rect = self.image.get_rect()
        self.rect.x = largura 
        self.rect.y = 0 

    def update(self):
        self.rect.x -= 5  

        if self.rect.y + self.rect.height < altura - 32:
            self.rect.y += 5
        else:
            self.kill()

        if self.rect.x < -self.rect.width:  
            self.kill() 


class Dino(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.som_pulo = pygame.mixer.Sound(os.path.join(diretorio_sons, 'jump_sound.wav'))
        self.som_pulo.set_volume(1)
        self.imagens_dinossauro = []
        for i in range(3):
            #                                   X Y   alt_larg
            img = sprite_sheet.subsurface((i * 32,0), (32,32))
            img = pygame.transform.scale(img, (32*3, 32*3))
            self.imagens_dinossauro.append(img)
        
        self.index_lista = 0
        self.image = self.imagens_dinossauro[0]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.pos_y_inicial = altura - 64 - 96//2
        self.rect.center = (100,altura - 64)
        self.pulo = False

    def pular(self):
        self.pulo = True
        self.som_pulo.play()    

    
    def update(self):
        if self.pulo == True:
            if self.rect.y <= 200:
                self.pulo = False
            self.rect.y -= 20
        else:
            if self.rect.y < self.pos_y_inicial:
                self.rect.y += 20
            else:
                self.rect.y = self.pos_y_inicial 


        if self.index_lista > 2:
            self.index_lista = 0
        self.index_lista += 0.25
        self.image = self.imagens_dinossauro[int(self.index_lista)]

class Nuvens(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((7*32, 0), (32,32))
        self.image= pygame.transform.scale(self.image, (32*3, 32*3))
        self.rect = self.image.get_rect()
        self.rect.y = randrange(50, 200, 50)
        self.rect.x = largura - randrange(30, 300, 90)

    def update(self):
        if self.rect.topright[0] < 0:
            self.rect.x = largura
            self.rect.y = randrange(50, 200, 50)
        self.rect.x -= 10

class Chao(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((6*32, 0), (32,32))
        self.image= pygame.transform.scale(self.image, (32*4, 32*2))
        self.rect = self.image.get_rect()
        self.rect.y = altura - 64
        self.rect.x = pos_x * 64

    def update(self):
        if self.rect.topright[0] < 0:
            self.rect.x = largura
        self.rect.x -= velocidade_jogo

    
class Cacto(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((5*32, 0), (32,32))
        self.image= pygame.transform.scale(self.image, (32*2, 32*2))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.escolha = escolha_obstaculo
        self.rect.center = (largura, altura - 64)
    def update(self):
        if self.escolha == 0:
            if self.rect.topright[0] < 0:
                self.rect.x = largura
            self.rect.x -= velocidade_jogo

class DinoVoador(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.imagens_dinossauro = []
        for i in range(3,5):
            img = sprite_sheet.subsurface((i*32, 0), (32, 32))
            img = pygame.transform.scale(img, (32*3, 32*3))
            self.imagens_dinossauro.append(img)

        self.index_lista = 0
        self.image = self.imagens_dinossauro[self.index_lista]
        self.mask = pygame.mask.from_surface(self.image)
        self.escolha = escolha_obstaculo
        self.rect = self.image.get_rect()
        self.rect.center = (largura, 390)
        self.rect.x = largura
    
    def update(self):
        if self.escolha == 1:
            if self.rect.topright[0] < 0:
                self.rect.x = largura
            self.rect.x -= velocidade_jogo

            if self.index_lista > 1:
                self.index_lista = 0
            self.index_lista += 0.25
            self.image = self.imagens_dinossauro[int(self.index_lista)]



todas_as_sprites = pygame.sprite.Group()
dino = Dino()
todas_as_sprites.add(dino)


for i in range(4):
    nuvem = Nuvens()
    todas_as_sprites.add(nuvem)

for i in range(largura*2//64):
    chao = Chao(i)
    todas_as_sprites.add(chao)

cacto = Cacto()
todas_as_sprites.add(cacto)

dino_voador = DinoVoador()
todas_as_sprites.add(dino_voador)


grupo_obstaculos = pygame.sprite.Group()
grupo_obstaculos.add(cacto)
grupo_obstaculos.add(dino_voador)

nuvem = Nuvens()
todas_as_sprites.add(nuvem)


meteoro = None 
meteoro_ativo = False  
tempo_vermelho = -1

tempo_cinza = 0  
duracao_cinza = 200


lua = Lua()

relogio = pygame.time.Clock()

while True:
    relogio.tick(30)

    if tempo_cinza > 0:  
        tela.fill(CINZA)
        lua.update(tempo_cinza, duracao_cinza)  # Passar ambos os argumentos
        tela.blit(lua.image, lua.rect)  
        tempo_cinza -= 1  
    elif meteoro_ativo and (pontos - tempo_vermelho) <= 50:
        tela.fill((VERMELHO))  
    else:
        tela.fill((BRANCO))  

    for event in pygame.event.get():
        if event.type == QUIT: 
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE and colidiu == False:
                if dino.rect.y != dino.pos_y_inicial:
                    pass
                else:
                    dino.pular()
            if event.key == K_r and colidiu == True:
                reiniciar_jogo()

    colisoes =pygame.sprite.spritecollide(dino, grupo_obstaculos, False, pygame.sprite.collide_mask)
 
    todas_as_sprites.draw(tela)
    
    if cacto.rect.topright[0] <= 0 or dino_voador.rect.topright[0] <= 0:
        escolha_obstaculo = choice([0,1])
        cacto.rect.x = largura
        dino_voador.rect.x = largura
        cacto.escolha = escolha_obstaculo
        dino_voador.escolha = escolha_obstaculo

    if colisoes and colidiu == False:
        som_colisao.play()
        colidiu = True

    if colidiu == True:
        if pontos % 100 == 0:
            pontos += 1
        game_over = exibe_mensagem('GAME OVER', 40, (PRETO))
        tela.blit(game_over,(largura//2, altura//2))
        restart = exibe_mensagem('Pressione R para reiniciar',20, (PRETO))
        tela.blit(restart, (largura//2, (altura//2)+ 60))


    else:
        pontos += 0.5
        ponto_inteiro = int(pontos)
        texto_pontos = exibe_mensagem(ponto_inteiro, 40, (PRETO))
        todas_as_sprites.update()
        

    if pontos % 100 == 0:
        som_pontuacao.play()
        if velocidade_jogo >= 40:
            velocidade_jogo += 0
        else:
            velocidade_jogo += 1

    if pontos >= 5000 and not meteoro_ativo:  
        meteoro = Meteoro()  
        todas_as_sprites.add(meteoro)
        meteoro_ativo = True  
        tempo_vermelho = pontos  

    
    if pontos % 700 == 0 and tempo_cinza <= 0:
        lua.iniciar_movimento(duracao_cinza)  
        tempo_cinza = duracao_cinza  

          


    tela.blit(texto_pontos, (520, 30))

    pygame.display.flip()