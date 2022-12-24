import pygame, os, random, csv, button, sys
from pygame import mixer
from score import ScoreInput

mixer.init()
pygame.init()


#screen
screen_width = 800
screen_hight = int(screen_width * 0.8)
screen = pygame.display.set_mode((screen_width,screen_hight))
pygame.display.set_caption('KIRBY ADVENTURE')
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define game variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = screen_hight // ROWS
TILE_TYPES = 20
MAX_LEVELS = 4
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False


#define player action variables
moving_left = False
moving_right = False
shoot = False


#music and sounds
jump_fx = pygame.mixer.Sound('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\music/audio_jump.wav')
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\music/audio_shoot.wav')
shot_fx.set_volume(0.5)


#load images
#button images
start_img = pygame.image.load('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\button/newgame_btn.png').convert_alpha()
exit_img = pygame.image.load('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\button/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\button/restart_btn.png').convert_alpha()
scoreboard_img = pygame.image.load('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\button/scoreboard_btn.png').convert_alpha()
home_img = pygame.image.load('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\button/home_btn.png').convert_alpha()

pine1_img = pygame.image.load('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\background/mountain.png').convert_alpha()
sky_img = pygame.image.load('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\background/sky_cloud.png').convert_alpha()
mainmenu_img = pygame.image.load('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\background/mainmenu_bg.jpg').convert_alpha()

#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\tile/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
#bullet
bullet_img = pygame.image.load('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\bullet/0.png').convert_alpha()
#pick up boxes
health_box_img = pygame.image.load('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\item/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\item/ammo_box.png').convert_alpha()
item_boxes = {
    'Health'    : health_box_img,
    'Ammo'      : ammo_box_img,
}


#define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

#define font
font = pygame.font.SysFont('Futura', 30)
font_title = pygame.font.SysFont('Showcard Gothic',50)
font_endgame = pygame.font.SysFont('Futura', 60)
font_ingame = pygame.font.SysFont('Showcard Gothic',20)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_mainmenu():
    screen.blit(mainmenu_img,(0,0))

def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, screen_hight - mountain_img.get_height() - 250))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, screen_hight - pine1_img.get_height() - 80))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, screen_hight - pine2_img.get_height()))


#function to reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    #create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data



class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.temp_score = 0

        #load all images for the players
        animation_types = ['idle', 'walk', 'jump', 'death']
        for animation in animation_types:
            #reset temporary list of images
            temp_list = []
            #count number of file in the folder
            number_of_frame = len(os.listdir(f'C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\{animation}'))
            for i in range(number_of_frame):
                playerImg = pygame.image.load(f'C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\{animation}/{i}.png').convert_alpha()
                playerImg = pygame.transform.scale(playerImg, (int(playerImg.get_width() * scale), int(playerImg.get_height() * scale)))
                temp_list.append(playerImg)
            self.animation_list.append(temp_list)  
        self.playerImg = self.animation_list[self.action][self.frame_index]
        self.rect = self.playerImg.get_rect()
        self.rect.center = (x , y)
        self.width = self.playerImg.get_width()
        self.height = self.playerImg.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        #reset movement variables
        screen_scroll = 0
        dx = 0 #ตำแหน่งในแกน x
        dy = 0 #ตำแหน่งในแกน y
        
        #movement if pressed moving left of right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        #jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -12
            self.jump = False
            self.in_air = True

        #apply garvity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #check for collision
        for tile in world.obstacle_list:
            #check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            #check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        #check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
        
        #check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        #check if fallen off the map
        if self.rect.bottom > screen_hight:
            self.health = 0

        #check if going off the edges of the screen
        if self.rect.left + dx < 0 or self.rect.right + dx > screen_width:
            dx = 0

        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        #update scroll based on player position
        if (self.rect.right > screen_width - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - screen_width) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
            self.rect.x -= dx
            screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            #reduce ammo
            self.ammo -= 1
            shot_fx.play()

    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 75
        #update image depending on current frame
        self.playerImg = self.animation_list[self.action][self.frame_index]
        #chack if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation setting
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)


    def draw(self):
        screen.blit(pygame.transform.flip(self.playerImg, self.flip, False) , self.rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        #ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        self.isDeath = False
        

        #load all images for the enemys
        animationEnemy_types = ['enemyidle', 'enemywalk', 'enemyjump', 'enemydeath']
        for animation in animationEnemy_types:
            #reset temporary list of images
            temp_list = []
            #count number of file in the folder
            number_of_frame = len(os.listdir(f'C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\{animation}'))
            for i in range(number_of_frame):
                enemyImg = pygame.image.load(f'C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\ProjectGameDoc\\{animation}/{i}.png').convert_alpha()
                enemyImg = pygame.transform.scale(enemyImg, (int(enemyImg.get_width() * scale), int(enemyImg.get_height() * scale)))
                temp_list.append(enemyImg)
            self.animation_list.append(temp_list)  
        self.enemyImg = self.animation_list[self.action][self.frame_index]
        self.rect = self.enemyImg.get_rect()
        self.rect.center = (x , y)
        self.width = self.enemyImg.get_width()
        self.height = self.enemyImg.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        #reset moving variables
        dx = 0 #ตำแหน่งในแกน x
        dy = 0 #ตำแหน่งในแกน y
        
        #movement if pressed moving left of right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1


        #apply garvity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #check for collision
        for tile in world.obstacle_list:
            #check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                #if ai has hit a wall then make it turn arround
                self.direction *= -1
                self.move_counter = 0
            #check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            #reduce ammo
            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)#0: idle
                self.idling = True
                self.idling_counter = 50
            #check if the ai in near the player
            if self.vision.colliderect(player.rect):
                #stop running and face the player
                self.update_action(0)#0: idle
                #shoot
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)#1: run
                    self.move_counter += 1
                    #update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        #scroll
        self.rect.x += screen_scroll


    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 75
        #update image depending on current frame
        self.enemyImg = self.animation_list[self.action][self.frame_index]
        #chack if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        #if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        #check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            #update the animation setting
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        global score
        if self.health <= 0 and self.isDeath == False :
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)
            score += 10
            self.isDeath = True


    def draw(self):
        screen.blit(pygame.transform.flip(self.enemyImg, self.flip, False) , self.rect)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        #iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:#create player
                        global player
                        global health_bar
                        player = Player(x * TILE_SIZE, y * TILE_SIZE, 1.7, 5, 20)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:#create enemies
                        enemy = Enemy(x * TILE_SIZE, y * TILE_SIZE, 1.25, 1, 5)
                        enemy_group.add(enemy)
                        enemyList.append(enemy)
                    elif tile == 17:#create ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:#create health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:#create exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        return player, health_bar


    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


    def update(self):
        #scroll
        self.rect.x += screen_scroll
        #check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            #check what kind of box it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 20
            #delete the item box
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #update with new health
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        #check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()
        #check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 50
                    player.temp_score += 25
                    self.kill()


class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction ==1:#whole screen fade
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, screen_width // 2,screen_hight))
            pygame.draw.rect(screen, self.colour, (screen_width // 2 + self.fade_counter , 0, screen_width, screen_hight))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, screen_width, screen_hight // 2))
            pygame.draw.rect(screen, self.colour, (0, screen_hight // 2 +self.fade_counter, screen_width, screen_hight))
        if self.direction == 2:#vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0, 0, screen_width, 0 + self.fade_counter))
        if self.fade_counter >= screen_width:
            fade_complete = True
        return fade_complete

def draw_score():
    text_score = font_ingame.render("SCORE : " + str(score + player.temp_score), True, (255, 255, 255))
    screen.blit(text_score, (10,70))

def draw_name():
    screen.fill('WHITE')
    
    text_name = font_title.render("INPUT YOUR NAME", True, (0, 0, 0))
    screen.blit(text_name, (screen_hight//2 - text_name.get_width()//2 + 85, 50))
    
    text_surface = font_title.render(player_name, True, (0, 0, 0))
    pygame.draw.rect(screen, 'WHITE', pygame.Rect(screen_width//2 - text_surface.get_width()//2-5, screen_width//2 - text_surface.get_height()//2-5, text_surface.get_width()+10, text_surface.get_height()+5),  2)
    screen.blit(text_surface,(screen_width//2 - text_surface.get_width()//2, screen_hight//2 - text_surface.get_height()//2))

def draw_menu():
    
    text_name = font_title.render("KIRBY ADVENTURE", True, (0, 0, 0))
    screen.blit(text_name, (screen_width//2 - text_name.get_width()//2, 100))
    
    text_surface = font.render("65010549 Nirada Aromsakaree", True, (204, 0, 204))
    screen.blit(text_surface,(screen_width - text_surface.get_width()-495, screen_hight - text_surface.get_height()-10)) 

sctxt =open("scorebar.txt",'r')
pltxt =open("player.txt",'r')
scin =sctxt.read()
plin =pltxt.read()
            
scorex =""
scorelist =[]
scindex =-1

playerx=""
playerlist =[]
plindex =-1

for x in scin:
    scindex +=1
    scorex += x
    if x =='\n' or scindex == len(scin)-1:
        scorelist.append(scorex)
        scorex= ""

for x in plin:
    plindex +=1
    playerx += x
    if x =='\n' or plindex == len(plin)-1:
        playerlist.append(playerx)
        playerx= ""
sctxt.close()
pltxt.close()   
tran = True   

class Scoreboard():
    
    def read (self):
        sctxt = open("scorebar.txt",'r')
        pltxt = open("player.txt",'r')
        scin = sctxt.read()
        plin = pltxt.read()
            
        scorex =""
        scorelist =[]
        scindex =-1

        playerx=""
        playerlist =[]
        plindex =-1

        for x in scin:
            scindex +=1
            scorex += x
            if x =='\n' or scindex == len(scin)-1:
                scorelist.append(scorex)
                scorex= ""

        for x in plin:
            plindex +=1
            playerx += x
            if x =='\n' or plindex == len(plin)-1:
                playerlist.append(playerx)
                playerx= ""

        self.playername_first = ScoreInput(screen,"1. "+playerlist[0],(255,102,178),175,150,3)
        self.playername_second = ScoreInput(screen,"2. "+playerlist[1],(255,102,178),175,230,3)
        self.playername_third = ScoreInput(screen,"3. "+playerlist[2],(255,102,178),175,310,3)
        self.playername_fourth = ScoreInput(screen,"4. "+playerlist[3],(255,102,178),175,390,3)
        self.playername_fifth = ScoreInput(screen,"5. "+playerlist[4],(255,102,178),175,470,3)
        
        self.score_first = ScoreInput(screen,scorelist[0],(255,102,178),500,150,3)
        self.score_second = ScoreInput(screen,scorelist[1],(255,102,178),500,230,3)
        self.score_third = ScoreInput(screen,scorelist[2],(255,102,178),500,310,3)
        self.score_fourth = ScoreInput(screen,scorelist[3],(255,102,178),500,390,3)
        self.score_fifth = ScoreInput(screen,scorelist[4],(255,102,178),500,470,3)

        sctxt.close()
        pltxt.close()
    
    def display_score(self):
        self.read()
        draw_mainmenu()
        text_scoreboard = font_title.render("SCOREBOARD", True, (255,102,178))
        screen.blit(text_scoreboard, (screen_hight//2 - text_scoreboard.get_width()//2 + 85, 50))
        self.playername_first.draw()
        self.playername_second.draw()
        self.playername_third.draw()
        self.playername_fourth.draw()
        self.playername_fifth.draw()
        self.score_first.draw()
        self.score_second.draw()
        self.score_third.draw()
        self.score_fourth.draw()
        self.score_fifth.draw()
    
    def run(self):
        screen.fill('WHITE')
        self.display_score()

#creat screen fades
intro_fade = ScreenFade(1, WHITE, 4)
death_fade = ScreenFade(2, RED, 4)

#create buttons
start_button = button.Button(screen_width // 2 - 115, screen_hight // 2 - 80, start_img, 1.5)
scoreboard_button =  button.Button(screen_width // 2 - 115, screen_hight // 2, scoreboard_img, 1.5)
exit_button = button.Button(screen_width // 2 - 115, screen_hight // 2 + 80, exit_img, 1.5)
restart_button = button.Button(screen_width // 2 - 115, screen_hight // 2 +80, restart_img, 1.5)
home_button = button.Button(screen_width -490, screen_hight // 2+250, home_img, 1)
home_button1 = button.Button(screen_width //  2 - 96, screen_hight // 2 + 75, home_img, 1.5)
home_button2 = button.Button(screen_width //  2 - 96, screen_hight // 2 + 75, home_img, 1.5)


#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
enemyList = []



#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#load in level data and create world
with open(f'C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\level/level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

player_name = ''
player_name_confirm = False
pause = False
start_game = False
scoreboard_show = False
scoreboard = Scoreboard()
score = 0


run = True
while run:
    
    clock.tick(FPS)
    if start_game == False:
        #draw menu
        draw_mainmenu()
        draw_menu()
        #add buttons
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
        if scoreboard_button.draw(screen):
            scoreboard_show = True

        if scoreboard_show == True:
            scoreboard.run()
            if home_button.draw(screen):
                scoreboard_show = False

    
    else:
        
        if player_name_confirm:
            #update background
            draw_bg()
            #draw world map
            world.draw()
            #show player health
            health_bar.draw(player.health)
            draw_score()
            #show ammo
            draw_text('AMMO: ', font_ingame, WHITE, 10, 45)
            for x in range(player.ammo):
                screen.blit(bullet_img, (90 + (x * 10), 48))


            player.update()
            player.draw()

            for enemy in enemyList:
                enemy.ai()
                enemy.update()
                enemy.draw()

            #update and draw groups
            bullet_group.update()
            item_box_group.update()
            decoration_group.update()
            water_group.update()
            exit_group.update()
            bullet_group.draw(screen)
            item_box_group.draw(screen)
            decoration_group.draw(screen)
            water_group.draw(screen)
            exit_group.draw(screen)

            #show intro
            if start_intro == True:
                if intro_fade.fade():
                    start_intro = False
                    intro_fade.fade_counter = 0

            #update player actions
            if player.alive:
                #shoot bullets
                if shoot:
                    player.shoot()
                if player.in_air:
                    player.update_action(2)#2: jump
                elif moving_left or moving_right:
                    player.update_action(1)#1: run
                else:
                    player.update_action(0)#0: idle
                screen_scroll, level_complete = player.move(moving_left, moving_right)
                bg_scroll -= screen_scroll
                #check if player has completed the level
                if level_complete:
                    start_intro = True
                    score += player.temp_score
                    level += 1
                    bg_scroll = 0
                    world_data = reset_level()
                    if level <= MAX_LEVELS:
                        #load in level data and create world
                        with open(f'C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\level/level{level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data) 
            
                    if level > MAX_LEVELS:
                            start_game = False
                            for x in range(len(scorelist)) :
                                if score >= int(scorelist[x]) and tran == True :
                                    scorelist.insert(x,str(score)+'\n')
                                    scorelist.pop(len(scorelist)-1)
                                    playerlist.insert(x,player_name+'\n')
                                    playerlist.pop(len(playerlist)-1)
                                    tran = False
                            plsend = ""
                            scsend = ""
                            for i in playerlist:
                                plsend += i
                            for i in scorelist:
                                scsend += i
                                
                            sctxt = open("scorebar.txt",'w') 
                            pltxt = open("player.txt",'w')
                            sctxt.write(scsend)
                            pltxt.write(plsend)
                            sctxt.close()
                            pltxt.close()
                            score_board_show = True
                            if home_button.draw(screen):
                                score_board_show = False
            else:
                screen_scroll = 0
                if death_fade.fade():
                    draw_text('GAME OVER ', font_title, WHITE, 260, 200)
                    draw_text('YOUR SCORE : ' +str(score), font_title, WHITE, 220, 300)
                    if restart_button.draw(screen):
                        death_fade.fade_counter = 0
                        start_intro = True
                        bg_scroll = 0
                        world_data = reset_level()
                        #load in level data and create world
                        with open(f'C:\\Users\\morningnoon\\programming pt\\Year 1\\ProjectGameDev\\level/level{level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)
        else:
            draw_name()
            for event in pygame.event.get():
                if event.type == quit:
                   run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif len(player_name) <= 20 and event.key != pygame.K_RETURN:
                        player_name += event.unicode
                    if event.key == pygame.K_RETURN and len(player_name) >= 1:
                        player_name_confirm = True

    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False


        #keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False


    pygame.display.update()

pygame.quit()