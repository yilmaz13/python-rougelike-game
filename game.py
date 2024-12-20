import pgzrun
from pgzero.actor import Actor
from pygame.rect import Rect
from enum import Enum

# Game Constants
WIDTH = 1920
HEIGHT = 1080

# Player Constants

MOVEMENT_SPEED = 5
ANIMATION_SPEED = 0.1
JUMP_POWER = 17 
ANIMATION_FRAME_RATE = 1/60
SHOOT_COOLDOWN_FRAME = 90
PLAYER_SPAWN_POS = (800, 650)

#Bullet Constants

BULLET_SPEED = 7

class Character:
    def __init__(self, x, y, sprite_prefix):
        self.actor = Actor(f'{sprite_prefix}_stand')
        self.actor.pos = (x, y)
        self.velocity_y = 0
        self.is_jumping = False
        self.animation_timer = 0
        self.frame = 0
        self.facing = 1
        self.rect = self.actor._rect
        self.ANIMATION_SPEED = ANIMATION_SPEED
       
        self.IDLE = [f'{sprite_prefix}_stand', f'{sprite_prefix}_stand']
        self.WALKRIGHT = [f'{sprite_prefix}_right_walk1', f'{sprite_prefix}_right_walk2']
        self.WALKLEFT = [f'{sprite_prefix}_left_walk1', f'{sprite_prefix}_left_walk2']
        self.JUMP = f'{sprite_prefix}_jump'

    def move(self, deltaX, deltaY):
        self.actor.x += deltaX
        self.actor.y += deltaY

    def draw(self):
        self.actor.draw()
    
    def set_trasnform_top(self, top):
        self.actor.top = top

    def set_trasnform_bottom(self, bottom):
        self.actor.bottom = bottom
    
    def set_direction(self, direction):
        self.facing = direction

    def animate_walk(self):      
        if self.animation_timer >= self.ANIMATION_SPEED:
            if self.facing == 1:
                self.frame = (self.frame + 1) % len(self.WALKRIGHT)
                self.actor.image = self.WALKRIGHT[self.frame]
            elif self.facing == -1:
                self.frame = (self.frame + 1) % len(self.WALKLEFT)
                self.actor.image = self.WALKLEFT[self.frame]           
            self.animation_timer = 0

    def animate_idle(self):
        if self.animation_timer >= self.ANIMATION_SPEED:
            self.frame = (self.frame + 1) % len(self.IDLE)
            self.actor.image = self.IDLE[self.frame]
            self.animation_timer = 0

class Bunny(Character):
    def __init__(self, x, y):
        super().__init__(x, y, 'bunny1')
        self.bullets = []
        self.shoot_cooldown = 0
        self.actor.x = x
        self.actor.y = y

    def shoot(self):
        if self.shoot_cooldown <= 0:
            game.play_shoot_sound()

            bullet = Bullet(self.actor.x, self.actor.y, self.facing)
            self.bullets.append(bullet)
            self.shoot_cooldown = SHOOT_COOLDOWN_FRAME
    
    def update(self):
        if game.game_state == GameState.GAMEPLAY:
            game.bunny.animation_timer += 1/60

            if self.shoot_cooldown > 0:
               self.shoot_cooldown -= 1  
            for bullet in self.bullets:
               bullet.update()
               if bullet.actor.x > WIDTH or bullet.actor.x < 0:
                   self.bullets.remove(bullet)
                   
               for enemy in game.enemyList:                
                  if bullet.check_collision(enemy):                                
                    self.bullets.remove(bullet)     
                    index = game.enemyList.index(enemy)                             
                    del game.enemyList[index]

               if len(game.enemyList) == 0:
                    game.game_win()        

class Enemy(Character):
    patrolX1 = 0
    patrolX2 = 0
    patrolY1 = 0
    patrolY2 = 0

    def __init__(self, x, y):
        super().__init__(x, y, 'enemy')       
    
    def update(self):
        self.animation_timer += 1/60
        self.animate_walk()

    def set_partol_position(self, patrolX1,patrolY1, patrolX2, patrolY2):
        self.patrolX1 = patrolX1
        self.patrolX2 = patrolX2
        self.patrolY1 = patrolY1
        self.patrolY2 = patrolY2

        self.partol()

    def partol(self):
        animate(self.actor, pos=(self.patrolX2, self.patrolY2), duration=3, tween='linear', on_finished=self.partol_back)
        self.facing = 1

    def partol_back(self):
        animate(self.actor, pos=(self.patrolX1, self.patrolY1), duration=3, tween='linear', on_finished=self.partol)    
        self.facing = -1

class Bullet:
    def __init__(self, x, y, direction):
        self.image = [ 'carrot_left',  'carrot_right']
        self.actor = Actor('carrot_left')
        self.actor.pos = (x, y)
        self.direction = direction
        self.speed = BULLET_SPEED
        self.active = True

        if direction == 1:
            self.actor.image = self.image[1] 
        else:
            self.actor.image = self.image[0]
    
    def update(self):
        self.actor.x += self.speed * self.direction
        
    def draw(self):
        if self.active:
            self.actor.draw()
            
    def check_collision(self, enemy):
        if self.active and self.actor.colliderect(enemy.actor):
            self.active = False
            return True
        return False
    
class GameState(Enum):
            MAINMENU = 1
            GAMEPLAY = 2
            GAMEWIN = 3
            GAMEOVER = 4
        
class GameController:
    def __init__(self):
        self.is_acitve_sound = True
        self.enemyList = []
        self.grounds = []
        self.bunny = None
        self.game_state = GameState.MAINMENU          
       
        self.spawnButtons()       
        self.main_menu()     

    def spawn_level(self):
        self.spawn_characters()       
        self.set_environment()

    def spawn_characters(self):
        self.bunny = Bunny(PLAYER_SPAWN_POS[0], PLAYER_SPAWN_POS[1])  

        self.enemy1 = Enemy(600, 300)
        self.enemy1.set_partol_position(600, 300, 950, 300)  

        self.enemy2 = Enemy(100, 300)      
        self.enemy2.set_partol_position(50, 300, 350, 300)  

        self.enemyList.append(self.enemy1)
        self.enemyList.append(self.enemy2)
    
    def set_environment(self):
        self.bg = Actor('bg_layer2', (0, 0))
        self.bg._rect.left = 0

        self.grounds = [
            Actor('ground_grass', pos=(1500, 700)),
            Actor('ground_grass', pos=(200, 700)),
            Actor('ground_grass', pos=(850, 800)),
            Actor('ground_grass', pos=(800, 450)),
            Actor('ground_grass', pos=(200, 450))
        ]
    
    def spawnButtons(self):
        self.start_img = Actor('playbutton3', pos=(WIDTH / 2, HEIGHT / 2))
        self.restart_img = Actor('playbutton3', pos=(WIDTH / 2, HEIGHT / 2))
        self.exit_img = Actor('exitbutton', pos=(WIDTH / 2, HEIGHT / 2 + 100))
        self.sound_on_img = Actor('sound_on.png', pos=(100, 100))
        self.sound_off_img = Actor('sound_off.png', pos=(100, 100))

    def clear_level(self):     
        for enemy in self.enemyList:
            del enemy
        
        if self.grounds is not None:  
          for ground in self.grounds:
              del ground
        
        if self.bunny is not None:  
         for bullet in self.bunny.bullets:
             del bullet        
         del self.bunny    
        
        self.enemyList.clear()
        self.grounds.clear()
        
    def play_game(self):
        self.game_state = GameState.GAMEPLAY   
        self.clear_level()   
        self.spawn_level()
        music.stop()
        music.play('game_theme')

    def game_over(self):
        self.game_state = GameState.GAMEOVER    
       # self.delete_level()
        music.stop()

    def game_win(self):
        self.game_state = GameState.GAMEWIN
      #  self.delete_level()
        music.stop()
        music.play('game_win_theme')        

    def main_menu(self):
        self.game_state = GameState.MAINMENU
        music.stop()
        music.play('main_theme') 
    
    def stop_sound(self):
        music.set_volume(0)
        game.is_acitve_sound = False
    
    def acitve_sound(self):
        music.set_volume(1)
        game.is_acitve_sound = True

    def play_click_sound(self):
        if game.is_acitve_sound:
            sounds.click.play()
    
    def play_jump_sound(self):
        if game.is_acitve_sound:
            sounds.jump.play()

    def play_shoot_sound(self):
        if game.is_acitve_sound:
            sounds.shoot.play()

game = GameController()

def update():
    if game.game_state == GameState.GAMEPLAY:
        game_update()

def game_update():
    for enemy in game.enemyList:
        enemy.update()
   
    game.bunny.update()

    bunny_delta_x = 0
    bunny_delta_y = 0

    if game.game_state == GameState.GAMEPLAY:
      if keyboard.left:
          bunny_delta_x = -MOVEMENT_SPEED
          game.bunny.animate_walk()
          game.bunny.set_direction(-1)
      elif keyboard.right:       
          bunny_delta_x = MOVEMENT_SPEED
          game.bunny.animate_walk()
          game.bunny.set_direction(1)
      else:
          game.bunny.animate_idle()

      if keyboard.F:
          game.bunny.shoot()
     
      if keyboard.space and not game.bunny.is_jumping:
          game.play_jump_sound()    
          bunny_delta_y = -JUMP_POWER
          game.bunny.velocity_y -= JUMP_POWER
          game.bunny.is_jumping = True
          game.bunny.actor.image = game.bunny.JUMP      
     
      game.bunny.velocity_y += 0.5
      bunny_delta_y += 0.5
     
      for gorund in game.grounds:   
          if gorund.colliderect(game.bunny.rect.x + bunny_delta_x, game.bunny.rect.y - 5,
                                game.bunny.rect.width, game.bunny.rect.height):
             bunny_delta_x = 0
          if gorund.colliderect(game.bunny.rect.x, game.bunny.rect.y + bunny_delta_y, 
                                game.bunny.rect.width, game.bunny.rect.height):
              if game.bunny.velocity_y >= 0:
                  if gorund.top - game.bunny.rect.top > 0:
                      game.bunny.set_trasnform_bottom(gorund.top)
                      game.bunny.velocity_y = 0                 
                      game.bunny.is_jumping = False
                  #   print('hit the ground')
              if game.bunny.velocity_y < 0:
                  if gorund.top - game.bunny.rect.top <= 0:
                      game.bunny.set_trasnform_top(gorund.bottom)                     
                      game.bunny.velocity_y = 0    
                  #   print('bumped their head')

      game.bunny.move(bunny_delta_x, bunny_delta_y + game.bunny.velocity_y)
     
      for enemy in game.enemyList:
          if enemy.actor.colliderect(game.bunny.rect):
              game.game_over()   
     
      if game.bunny.rect.y > HEIGHT:
          game.game_over()

def draw():
    screen.clear()   

    if game.game_state == GameState.MAINMENU:
        game.start_img.draw()
        game.exit_img.draw()

        if game.is_acitve_sound:         
            game.sound_on_img.draw()
        else:           
            game.sound_off_img.draw()   

        screen.draw.text('Press F for shoot!', pos=(WIDTH / 2 - 150, HEIGHT / 2 - 150),
                          color = (255,255,255), fontsize = 50)
        screen.draw.text('Press Space for jump!', pos=(WIDTH / 2 -150, HEIGHT / 2 - 100),
                          color = (255,255,255), fontsize = 50)        
       
    if game.game_state == GameState.GAMEPLAY:          
        game.bg.draw() 
        game.bunny.draw()
        for enemy in game.enemyList:
            enemy.draw()       
        for gorund in game.grounds:
            gorund.draw()
        for bullet in game.bunny.bullets:
            bullet.draw()

    if game.game_state == GameState.GAMEOVER:
        screen.draw.text('Game Over!', pos=(WIDTH / 2 - 150, HEIGHT / 2 - 200),
                          color = (255,255,255), fontsize = 100)
        game.restart_img.draw()
        game.exit_img.draw()

    if game.game_state == GameState.GAMEWIN:
        screen.draw.text('You Win!', pos=(WIDTH / 2 - 150, HEIGHT / 2 - 200), 
                         color = (255,255,255), fontsize = 100)
        game.restart_img.draw()
        game.exit_img.draw()
   
def on_mouse_down(pos):
    if  game.game_state == GameState.GAMEOVER or game.game_state == GameState.GAMEWIN:
        if game.restart_img.collidepoint(pos):
            print('Restart button clicked')
            game.play_click_sound()           
            game.play_game()
        if game.exit_img.collidepoint(pos):
            print('Exit button clicked')
            game.play_click_sound()
            exit()       
    if game.game_state == GameState.MAINMENU:
        if game.start_img.collidepoint(pos):
            print('Start button clicked')
            game.play_click_sound()            
            game.play_game()
        if game.exit_img.collidepoint(pos):
            print('Exit button clicked')
            game.play_click_sound()
            exit()       
        if game.sound_on_img.collidepoint(pos):
            if game.is_acitve_sound:
                print('Start button clicked')
                game.stop_sound()
            else:
                print('Start button clicked')
                game.acitve_sound()

pgzrun.go()