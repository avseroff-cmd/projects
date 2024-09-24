import pygame
from sys import exit
from random import randint, choice

FONT = "data/font/Pixeltype.ttf"
SKY  = "data/graphics/Sky.png"
GROUND = "data/graphics/ground.png"
SNAIL = "data/graphics/snail"
FLY = "data/graphics/Fly"
PLAYER = "data/graphics/Player"
SOUND = "data/audio"

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_walk_1 = pygame.image.load(PLAYER + '/player_walk_1.png').convert_alpha()
        player_walk_2 = pygame.image.load(PLAYER + '/player_walk_2.png').convert_alpha()
        self.player_walk = [player_walk_1,player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load(PLAYER + '/jump.png').convert_alpha()
        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom = (100,300))
        self.gravity = 0
        self.jump_sound = pygame.mixer.Sound(SOUND + '/jump.mp3')
        self.jump_sound.set_volume(0.2)
    
    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.gravity = -21
            self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def animation_state(self):
        if self.rect.bottom < 300:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]
            

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self,type):
        super().__init__()
        
        if type == 'fly':
            fly_1 = pygame.image.load(FLY + '/Fly1.png').convert_alpha()
            fly_2 = pygame.image.load(FLY + '/Fly2.png').convert_alpha()
            self.frames = [fly_1,fly_2]
            y_pos = 210
        else:
            snail_1 = pygame.image.load(SNAIL + '/snail1.png').convert_alpha()
            snail_2 = pygame.image.load(SNAIL + '/snail2.png').convert_alpha()
            self.frames = [snail_1,snail_2]
            y_pos = 300

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom = (randint(900,1100), y_pos))

    def animation_state(self):
        self.animation_index += 0.2
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]
    
    def update(self):
        self.animation_state()
        self.rect.x -= 7
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

def collisions():
    if pygame.sprite.spritecollide(player.sprite,obstacle_group,False):
        obstacle_group.empty()
        return False
    else:
        return True

def display_score():
    current_time = pygame.time.get_ticks() - start_time
    score_surface = score_font.render(f'Score: {current_time//1000}', False, (64, 64, 64))
    score_rect = score_surface.get_rect(center = (400,50))
    screen.blit(score_surface, score_rect)
    return current_time

pygame.init()
screen = pygame.display.set_mode((800,400))
pygame.display.set_caption('Run Fucker Run')
clock = pygame.time.Clock()
score_font = pygame.font.Font(FONT,50)
end_font2 = pygame.font.Font(FONT,50)
end_font = pygame.font.Font(FONT,200)
game_active = True
start_time = 0
score = 0
bg_music = pygame.mixer.Sound(SOUND + '/music.wav')
bg_music.set_volume(0.3)
bg_music.play(loops = -1)

# Groups
player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()

# BackGround
sky_surface = pygame.image.load(SKY).convert()
ground_surface = pygame.image.load(GROUND).convert()

# End screen
end_surface = end_font.render('Game Over', False, (64,64,64))
end_rect = end_surface.get_rect(center = (400,200))
end_surface2 = end_font2.render('Press Spase', False, (64,64,64))
end_rect2 = end_surface2.get_rect(center = (400,270))

# Timers
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer,900)

snail_animation_timer = pygame.USEREVENT + 2
pygame.time.set_timer(snail_animation_timer,500)

fly_animation_timer = pygame.USEREVENT + 2
pygame.time.set_timer(fly_animation_timer,200)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if game_active == False:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                start_time = pygame.time.get_ticks()

        if game_active:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(['fly','snail','snail','snail'])))

    if game_active:
        screen.blit(sky_surface,(0,0))
        screen.blit(ground_surface,(0,300))
        score = display_score()

        # Player
        player.draw(screen)
        player.update()

        obstacle_group.draw(screen)
        obstacle_group.update()

        # Collision
        game_active = collisions()

    else:
        screen.fill('Black')
        screen.blit(end_surface,end_rect)
        screen.blit(end_surface2,end_rect2)
        score_message = score_font.render(f'Score: {score//1000}', False, (64, 64, 64))
        score_message_rect = score_message.get_rect(center = (400,50))
        screen.blit(score_message,score_message_rect)

    pygame.display.update()
    clock.tick(60)