import pygame
import random
import os
import sys
import math  # Added for boss movement patterns

# Initialize pygame
pygame.init()
pygame.mixer.init()  # For sound effects

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60
SCROLL_SPEED = 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Impact")
clock = pygame.time.Clock()

# Load assets
def create_player_ship():
    # Create a blue triangular player ship
    image = pygame.Surface((40, 20), pygame.SRCALPHA)
    color = (30, 144, 255)  # Dodger blue
    
    # Draw a triangular ship shape
    points = [(0, 10), (30, 0), (30, 20), (0, 10)]
    pygame.draw.polygon(image, color, points)
    
    # Add some details
    pygame.draw.line(image, (100, 180, 255), (10, 10), (25, 10), 2)
    pygame.draw.line(image, (100, 180, 255), (25, 5), (35, 5), 2)
    pygame.draw.line(image, (100, 180, 255), (25, 15), (35, 15), 2)
    
    return image

def create_enemy_ship(enemy_type):
    if enemy_type == 1:  # Basic enemy
        image = pygame.Surface((30, 15), pygame.SRCALPHA)
        color = (255, 100, 100)  # Light red
        # Draw a simple enemy shape
        pygame.draw.rect(image, color, (0, 0, 20, 15))
        pygame.draw.polygon(image, color, [(20, 0), (30, 7), (20, 15)])
        return image
        
    elif enemy_type == 2:  # Advanced enemy
        image = pygame.Surface((35, 20), pygame.SRCALPHA)
        color = (255, 165, 0)  # Orange
        # Draw a more complex enemy shape
        pygame.draw.rect(image, color, (5, 0, 25, 20))
        pygame.draw.polygon(image, color, [(0, 10), (5, 0), (5, 20)])
        pygame.draw.polygon(image, color, [(30, 0), (35, 10), (30, 20)])
        return image
        
    elif enemy_type == 3:  # Elite enemy
        image = pygame.Surface((40, 25), pygame.SRCALPHA)
        color = (148, 0, 211)  # Purple
        # Draw an elite enemy shape
        pygame.draw.rect(image, color, (10, 5, 20, 15))
        pygame.draw.polygon(image, color, [(0, 12), (10, 5), (10, 20)])
        pygame.draw.polygon(image, color, [(30, 5), (40, 12), (30, 20)])
        pygame.draw.rect(image, color, (15, 0, 10, 5))
        return image
        
    else:  # Boss
        image = pygame.Surface((80, 50), pygame.SRCALPHA)
        color = (178, 34, 34)  # Firebrick red
        # Draw a large boss shape
        pygame.draw.rect(image, color, (20, 10, 40, 30))
        pygame.draw.polygon(image, color, [(0, 25), (20, 10), (20, 40)])
        pygame.draw.polygon(image, color, [(60, 10), (80, 25), (60, 40)])
        pygame.draw.rect(image, color, (30, 0, 20, 10))
        pygame.draw.rect(image, color, (25, 40, 30, 10))
        
        # Add some details
        pygame.draw.circle(image, (255, 255, 0), (40, 25), 8)
        pygame.draw.circle(image, (255, 0, 0), (40, 25), 4)
        
        return image

def create_bullet(is_player=True):
    if is_player:
        image = pygame.Surface((15, 5), pygame.SRCALPHA)
        color = (0, 255, 0)  # Green
        pygame.draw.rect(image, color, (0, 0, 10, 5))
        pygame.draw.polygon(image, color, [(10, 0), (15, 2.5), (10, 5)])
    else:
        image = pygame.Surface((15, 5), pygame.SRCALPHA)
        color = (255, 0, 0)  # Red
        pygame.draw.rect(image, color, (5, 0, 10, 5))
        pygame.draw.polygon(image, color, [(0, 2.5), (5, 0), (5, 5)])
    
    return image

def create_powerup(powerup_type):
    image = pygame.Surface((20, 20), pygame.SRCALPHA)
    
    if powerup_type == 'shield':
        color = (0, 0, 255)  # Blue
        pygame.draw.circle(image, color, (10, 10), 10)
        pygame.draw.circle(image, (100, 100, 255), (10, 10), 6)
        pygame.draw.circle(image, (200, 200, 255), (10, 10), 3)
    elif powerup_type == 'power':
        color = (0, 255, 0)  # Green
        pygame.draw.circle(image, color, (10, 10), 10)
        points = [(10, 0), (13, 7), (20, 10), (13, 13), (10, 20), (7, 13), (0, 10), (7, 7)]
        pygame.draw.polygon(image, (200, 255, 200), points)
    else:  # life
        color = (255, 0, 0)  # Red
        pygame.draw.circle(image, color, (10, 10), 10)
        pygame.draw.circle(image, (255, 200, 200), (10, 10), 5)
    
    return image

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = create_player_ship()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH / 4
        self.rect.bottom = SCREEN_HEIGHT / 2
        self.speedy = 0
        self.speedx = 0
        self.lives = 3
        self.score = 0
        self.shoot_delay = 250  # milliseconds
        self.last_shot = pygame.time.get_ticks()
        self.power_level = 1
        self.power_timer = 0
        self.shield = 0
        self.invincible = False
        self.invincible_timer = 0
        self.flicker_counter = 0

    def update(self):
        # Movement
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        
        # Keep player on screen
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0
            
        # Power-up timeout
        if self.power_level > 1 and pygame.time.get_ticks() > self.power_timer:
            self.power_level = 1
            
        # Shield timeout
        if self.shield > 0 and pygame.time.get_ticks() > self.shield:
            self.shield = 0
            
        # Invincibility timeout
        if self.invincible and pygame.time.get_ticks() > self.invincible_timer:
            self.invincible = False
            
        # Visual effect for invincibility (flicker)
        if self.invincible:
            self.flicker_counter += 1
            if self.flicker_counter % 6 < 3:  # Flicker every few frames
                self.image.set_alpha(100)  # Semi-transparent
            else:
                self.image.set_alpha(255)  # Fully visible
        else:
            self.image.set_alpha(255)  # Ensure fully visible when not invincible

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.right, self.rect.centery)
            all_sprites.add(bullet)
            bullets.add(bullet)
            # Play shooting sound
            # shoot_sound.play()
            
            # Additional bullets for power-ups
            if self.power_level >= 2:
                bullet1 = Bullet(self.rect.right, self.rect.centery - 10)
                bullet2 = Bullet(self.rect.right, self.rect.centery + 10)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                
            if self.power_level >= 3:
                bullet3 = Bullet(self.rect.right, self.rect.centery - 20)
                bullet4 = Bullet(self.rect.right, self.rect.centery + 20)
                all_sprites.add(bullet3)
                all_sprites.add(bullet4)
                bullets.add(bullet3)
                bullets.add(bullet4)

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type=1):
        pygame.sprite.Sprite.__init__(self)
        self.enemy_type = enemy_type
        self.image = create_enemy_ship(enemy_type)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randrange(0, 100)
        self.rect.y = random.randrange(50, SCREEN_HEIGHT - 50)
        
        # Different properties based on enemy type
        if enemy_type == 1:  # Basic enemy
            self.speedx = random.randrange(3, 6) * -1
            self.shoot_chance = 0.005
            self.health = 1
            self.score_value = 10
        elif enemy_type == 2:  # Advanced enemy
            self.speedx = random.randrange(2, 5) * -1
            self.shoot_chance = 0.01
            self.health = 2
            self.score_value = 20
        elif enemy_type == 3:  # Elite enemy
            self.speedx = random.randrange(1, 4) * -1
            self.shoot_chance = 0.015
            self.health = 3
            self.score_value = 30
        else:  # Boss (type 4)
            self.speedx = -1
            self.shoot_chance = 0.03
            self.health = 20
            self.score_value = 200
            self.movement_pattern = 'sine'
            self.pattern_offset = 0
            self.original_y = self.rect.y

    def update(self):
        self.rect.x += self.speedx
        
        # Special movement patterns for boss
        if self.enemy_type == 4:
            if self.movement_pattern == 'sine':
                self.pattern_offset += 0.05
                self.rect.y = self.original_y + math.sin(self.pattern_offset) * 100
                
                # Occasionally change direction
                if random.random() < 0.005:
                    self.speedx = random.choice([-1, -0.5, 0, 0.5, 1])
                    
                # Keep boss on screen
                if self.rect.right < SCREEN_WIDTH * 0.6:
                    self.speedx = 1
                if self.rect.left > SCREEN_WIDTH - 100:
                    self.speedx = -1
            
            # Boss special attack - multiple bullets
            if random.random() < self.shoot_chance:
                self.enemy_shoot(3)
        else:
            # Remove if off screen
            if self.rect.right < 0:
                self.kill()
            
            # Random shooting for regular enemies
            if random.random() < self.shoot_chance:
                self.enemy_shoot()
    
    def enemy_shoot(self, bullet_count=1):
        if bullet_count == 1:
            enemy_bullet = EnemyBullet(self.rect.left, self.rect.centery)
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)
        else:
            # Multiple bullets (for boss)
            spread = 30  # degrees
            for i in range(bullet_count):
                angle = -spread/2 + (spread/(bullet_count-1)) * i if bullet_count > 1 else 0
                enemy_bullet = EnemyBullet(self.rect.left, self.rect.centery, angle)
                all_sprites.add(enemy_bullet)
                enemy_bullets.add(enemy_bullet)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = create_bullet(True)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.centery = y
        self.speedx = 10

    def update(self):
        self.rect.x += self.speedx
        # Remove if off screen
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

# Enemy Bullet class
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0):
        pygame.sprite.Sprite.__init__(self)
        self.image = create_bullet(False)
        self.rect = self.image.get_rect()
        self.rect.right = x
        self.rect.centery = y
        self.speedx = -8
        self.speedy = 0
        
        # Apply angle if provided (for boss spread shots)
        if angle != 0:
            self.speedx = -8 * math.cos(math.radians(angle))
            self.speedy = 8 * math.sin(math.radians(angle))
            # Rotate the bullet image
            self.image = pygame.transform.rotate(self.image, angle)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # Remove if off screen
        if self.rect.right < 0 or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

# Power-up class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'power', 'life'])
        self.image = create_powerup(self.type)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randrange(0, 100)
        self.rect.y = random.randrange(50, SCREEN_HEIGHT - 50)
        self.speedx = -3

    def update(self):
        self.rect.x += self.speedx
        # Remove if off screen
        if self.rect.right < 0:
            self.kill()

# Background class for parallax scrolling
class Background:
    def __init__(self):
        self.bgimage = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.bgimage.fill(BLACK)
        
        # Add some stars
        for i in range(100):
            x = random.randrange(0, SCREEN_WIDTH)
            y = random.randrange(0, SCREEN_HEIGHT)
            pygame.draw.circle(self.bgimage, WHITE, (x, y), 1)
            
        self.rectBGimg = self.bgimage.get_rect()
        self.bgY1 = 0
        self.bgX1 = 0
        self.bgY2 = 0
        self.bgX2 = self.rectBGimg.width
        self.moving_speed = SCROLL_SPEED

    def update(self):
        self.bgX1 -= self.moving_speed
        self.bgX2 -= self.moving_speed
        if self.bgX1 <= -self.rectBGimg.width:
            self.bgX1 = self.rectBGimg.width
        if self.bgX2 <= -self.rectBGimg.width:
            self.bgX2 = self.rectBGimg.width

    def render(self):
        screen.blit(self.bgimage, (self.bgX1, self.bgY1))
        screen.blit(self.bgimage, (self.bgX2, self.bgY2))

# Game state management
class Game:
    def __init__(self):
        self.level = 1
        self.score = 0
        self.game_over = False
        self.paused = False
        self.spawn_timer = 0
        self.spawn_delay = 1000  # milliseconds
        self.level_enemies_killed = 0
        self.enemies_to_kill = 15  # Enemies to kill before boss appears
        self.boss_spawned = False
        self.boss_defeated = False
        self.level_complete = False
        self.level_complete_timer = 0
        self.font = pygame.font.Font(None, 36)
        
    def spawn_enemy(self):
        # Don't spawn regular enemies if boss is present or level is complete
        if self.boss_spawned or self.level_complete:
            return
            
        now = pygame.time.get_ticks()
        if now - self.spawn_timer > self.spawn_delay:
            self.spawn_timer = now
            
            # Determine enemy type based on level and randomness
            if self.level == 1:
                enemy_type = 1
            elif self.level == 2:
                enemy_type = random.choices([1, 2], weights=[0.7, 0.3])[0]
            elif self.level == 3:
                enemy_type = random.choices([1, 2, 3], weights=[0.5, 0.3, 0.2])[0]
            else:
                enemy_type = random.choices([1, 2, 3], weights=[0.3, 0.4, 0.3])[0]
                
            enemy = Enemy(enemy_type)
            all_sprites.add(enemy)
            enemies.add(enemy)
            
    def spawn_boss(self):
        if not self.boss_spawned and self.level_enemies_killed >= self.enemies_to_kill:
            self.boss_spawned = True
            boss = Enemy(4)  # Type 4 is boss
            all_sprites.add(boss)
            enemies.add(boss)
            # Boss warning message could be displayed here
            
    def spawn_powerup(self):
        if random.random() < 0.002:  # 0.2% chance per frame
            powerup = PowerUp()
            all_sprites.add(powerup)
            powerups.add(powerup)
            
    def check_level_progression(self):
        # Check if boss is defeated
        if self.boss_spawned and not self.boss_defeated and len([e for e in enemies if e.enemy_type == 4]) == 0:
            self.boss_defeated = True
            self.level_complete = True
            self.level_complete_timer = pygame.time.get_ticks()
            
        # Move to next level after delay
        if self.level_complete and pygame.time.get_ticks() - self.level_complete_timer > 3000:
            self.level += 1
            self.level_enemies_killed = 0
            self.boss_spawned = False
            self.boss_defeated = False
            self.level_complete = False
            self.enemies_to_kill = 15 + (self.level * 5)  # More enemies per level
            self.spawn_delay = max(200, 1000 - (self.level * 100))  # Faster spawns at higher levels
            
    def draw_ui(self):
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Draw lives
        lives_text = self.font.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(lives_text, (10, 50))
        
        # Draw level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH - 150, 10))
        
        # Draw enemy counter
        if not self.boss_spawned:
            enemy_counter = self.font.render(f"Enemies: {self.level_enemies_killed}/{self.enemies_to_kill}", True, WHITE)
            screen.blit(enemy_counter, (SCREEN_WIDTH - 250, 50))
        else:
            # Draw boss health if boss is present
            bosses = [e for e in enemies if e.enemy_type == 4]
            if bosses:
                boss = bosses[0]
                boss_health = self.font.render(f"Boss Health: {boss.health}/20", True, RED)
                screen.blit(boss_health, (SCREEN_WIDTH - 250, 50))
        
        # Draw shield indicator if active
        if player.shield > 0:
            shield_text = self.font.render("SHIELD ACTIVE", True, BLUE)
            screen.blit(shield_text, (SCREEN_WIDTH // 2 - shield_text.get_width() // 2, 10))
            
        # Draw invincibility indicator if active
        if player.invincible:
            invincible_text = self.font.render("INVINCIBLE", True, (255, 215, 0))  # Gold color
            screen.blit(invincible_text, (SCREEN_WIDTH // 2 - invincible_text.get_width() // 2, 50))
            
        # Draw level complete message
        if self.level_complete:
            level_complete_text = self.font.render(f"LEVEL {self.level} COMPLETE!", True, GREEN)
            screen.blit(level_complete_text, (SCREEN_WIDTH // 2 - level_complete_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
    def show_game_over(self):
        screen.fill(BLACK)
        game_over_text = self.font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Reached Level: {self.level}", True, WHITE)
        restart_text = self.font.render("Press R to restart", True, WHITE)
        
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 75))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 25))
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, SCREEN_HEIGHT // 2 + 25))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 75))
        
    def reset(self):
        global all_sprites, player, enemies, bullets, enemy_bullets, powerups
        
        # Reset game state
        self.level = 1
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.level_enemies_killed = 0
        self.enemies_to_kill = 15
        self.boss_spawned = False
        self.boss_defeated = False
        self.level_complete = False
        
        # Clear all sprite groups
        all_sprites = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        
        # Create new player
        player = Player()
        all_sprites.add(player)

# Initialize sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Create background
background = Background()

# Create game controller
game = Game()

# Game loop
running = True
while running:
    # Keep loop running at the right speed
    clock.tick(FPS)
    
    # Process input (events)
    for event in pygame.event.get():
        # Check for closing window
        if event.type == pygame.QUIT:
            running = False
        
        # Keydown events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if game.game_over and event.key == pygame.K_r:
                game.reset()
            if not game.game_over:
                if event.key == pygame.K_UP:
                    player.speedy = -5
                if event.key == pygame.K_DOWN:
                    player.speedy = 5
                if event.key == pygame.K_LEFT:
                    player.speedx = -5
                if event.key == pygame.K_RIGHT:
                    player.speedx = 5
                if event.key == pygame.K_SPACE:
                    player.shoot()
                if event.key == pygame.K_p:
                    game.paused = not game.paused
        
        # Keyup events
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP and player.speedy < 0:
                player.speedy = 0
            if event.key == pygame.K_DOWN and player.speedy > 0:
                player.speedy = 0
            if event.key == pygame.K_LEFT and player.speedx < 0:
                player.speedx = 0
            if event.key == pygame.K_RIGHT and player.speedx > 0:
                player.speedx = 0
    
    # Skip update if game over or paused
    if game.game_over:
        game.show_game_over()
        pygame.display.flip()
        continue
        
    if game.paused:
        pause_text = game.font.render("PAUSED", True, WHITE)
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        continue
    
    # Update
    background.update()
    all_sprites.update()
    
    # Spawn enemies and power-ups
    game.spawn_enemy()
    game.spawn_powerup()
    game.check_level_progression()
    
    # Check for bullet-enemy collisions
    hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
    for enemy, bullet_list in hits.items():
        enemy.health -= len(bullet_list)
        if enemy.health <= 0:
            game.score += enemy.score_value
            game.level_enemies_killed += 1
            enemy.kill()
            # Explosion effect would go here
    
    # Check for player-enemy collisions
    if player.shield == 0:  # Only check collisions if shield is not active
        hits = pygame.sprite.spritecollide(player, enemies, False)  # Changed to False to not automatically destroy enemies
        if hits and not player.invincible:
            player.lives -= 1
            player.invincible = True
            player.invincible_timer = pygame.time.get_ticks() + 1500  # 1.5 seconds of invincibility
            
            # Only destroy non-boss enemies on collision
            for hit in hits:
                if hit.enemy_type != 4:  # If not a boss
                    hit.kill()
                    
            if player.lives <= 0:
                game.game_over = True
            # Explosion effect would go here
    
    # Check for player-enemy bullet collisions
    if player.shield == 0:  # Only check collisions if shield is not active
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        if hits and not player.invincible:
            player.lives -= 1
            player.invincible = True
            player.invincible_timer = pygame.time.get_ticks() + 1500  # 1.5 seconds of invincibility
            if player.lives <= 0:
                game.game_over = True
            # Explosion effect would go here
    
    # Check for player-powerup collisions
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield = pygame.time.get_ticks() + 5000  # 5 seconds of shield
        elif hit.type == 'power':
            player.power_level = min(player.power_level + 1, 3)
            player.power_timer = pygame.time.get_ticks() + 10000  # 10 seconds
        elif hit.type == 'life':
            player.lives += 1
    
    # Spawn boss when enough enemies are killed
    game.spawn_boss()
    
    # Draw / render
    background.render()
    all_sprites.draw(screen)
    game.draw_ui()
    
    # Flip the display
    pygame.display.flip()

pygame.quit()
sys.exit()
