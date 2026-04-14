# -*- coding: utf-8 -*-
import pygame
import random
import math

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

class StarField:
    def __init__(self):
        self.stars = []
        for i in range(100):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            speed = random.randint(1, 4)
            size = 1 if speed < 3 else 2
            self.stars.append([x, y, speed, size])
    
    def update(self):
        for star in self.stars:
            star[1] += star[2]
            if star[1] > SCREEN_HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, screen):
        for star in self.stars:
            brightness = 150 + star[2] * 25
            pygame.draw.circle(screen, (brightness, brightness, brightness), (star[0], star[1]), star[3])

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = pygame.Surface((40, 50), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 50
        self.speed = 5
        self.weapon_level = 1
        self.max_weapon_level = 3
        self.shoot_delay = 200
        self.last_shot = pygame.time.get_ticks()
        self.invincible = False
        self.invincible_time = 0
        self.draw_ship()
    
    def draw_ship(self):
        self.image.fill((0, 0, 0, 0))
        points = [
            (self.rect.width // 2, 0),
            (0, self.rect.height),
            (self.rect.width, self.rect.height)
        ]
        pygame.draw.polygon(self.image, WHITE, points)
        pygame.draw.polygon(self.image, CYAN, points, 2)
    
    def update(self):
        now = pygame.time.get_ticks()
        if self.invincible and now - self.invincible_time > 2000:
            self.invincible = False
        
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed
        
        self.rect.x += dx
        self.rect.y += dy
        
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 40:
            self.rect.top = 40
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        
        if keys[pygame.K_SPACE]:
            self.shoot()
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.weapon_level == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top, 0, -10, YELLOW)
                self.game.bullets.add(bullet)
                self.game.all_sprites.add(bullet)
            elif self.weapon_level == 2:
                bullet1 = Bullet(self.rect.centerx - 15, self.rect.top, 0, -10, YELLOW)
                bullet2 = Bullet(self.rect.centerx + 15, self.rect.top, 0, -10, YELLOW)
                self.game.bullets.add(bullet1, bullet2)
                self.game.all_sprites.add(bullet1, bullet2)
            elif self.weapon_level >= 3:
                bullet1 = Bullet(self.rect.centerx, self.rect.top, 0, -10, YELLOW)
                bullet2 = Bullet(self.rect.centerx - 15, self.rect.top, -1, -10, YELLOW)
                bullet3 = Bullet(self.rect.centerx + 15, self.rect.top, 1, -10, YELLOW)
                self.game.bullets.add(bullet1, bullet2, bullet3)
                self.game.all_sprites.add(bullet1, bullet2, bullet3)
    
    def get_hit(self):
        if not self.invincible:
            self.game.lives -= 1
            self.invincible = True
            self.invincible_time = pygame.time.get_ticks()
            if self.game.lives <= 0:
                self.game.game_over()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, color, is_enemy=False):
        super().__init__()
        self.color = color
        self.is_enemy = is_enemy
        self.image = pygame.Surface((6, 12), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, 6, 12))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.dx = dx
        self.dy = dy
    
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x=None, y=None):
        super().__init__()
        self.game = game
        self.size = random.randint(25, 40)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x if x is not None else random.randint(0, SCREEN_WIDTH - self.size)
        self.rect.y = y if y is not None else -self.size
        self.speedy = random.randint(2, 5)
        self.speedx = random.randint(-2, 2)
        self.hp = 1
        self.shoot_delay = random.randint(1000, 2000)
        self.last_shot = pygame.time.get_ticks()
        self.draw_enemy()
    
    def draw_enemy(self):
        self.image.fill((0, 0, 0, 0))
        points = [
            (self.rect.width // 2, self.rect.height),
            (0, 0),
            (self.rect.width, 0)
        ]
        pygame.draw.polygon(self.image, RED, points)
        pygame.draw.polygon(self.image, ORANGE, points, 2)
    
    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speedx *= -1
        
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            self.shoot()
        
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
    
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.bottom, 0, 6, ORANGE, True)
        self.game.enemy_bullets.add(bullet)
        self.game.all_sprites.add(bullet)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type='weapon'):
        super().__init__()
        self.power_type = power_type
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speedy = 3
        self.rotation = 0
        self.color = GREEN if power_type == 'weapon' else BLUE
        self.draw_powerup()
    
    def draw_powerup(self):
        self.image.fill((0, 0, 0, 0))
        center = (10, 10)
        points = []
        for i in range(4):
            angle = math.radians(self.rotation + i * 90)
            x = center[0] + 10 * math.cos(angle)
            y = center[1] + 10 * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(self.image, self.color, points)
    
    def update(self):
        self.rotation += 5
        self.draw_powerup()
        self.rect.y += self.speedy
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30
        self.expansion = 2
    
    def update(self):
        self.radius += self.expansion
        if self.radius > self.max_radius:
            self.kill()
    
    def draw(self, screen):
        alpha = 255 - int((self.radius / self.max_radius) * 255)
        color = (255, min(255, 100 + self.radius * 5), 0)
        surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, (*color, alpha), (self.radius, self.radius), self.radius)
        screen.blit(surface, (self.x - self.radius, self.y - self.radius))

class Boss(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.width = 150
        self.height = 100
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.top = -self.height
        self.target_y = 80
        self.speedy = 2
        self.speedx = 2
        self.max_hp = 100
        self.hp = self.max_hp
        self.entered = False
        self.shoot_pattern = 0
        self.shoot_delay = 500
        self.last_shot = pygame.time.get_ticks()
        self.draw_boss()
    
    def draw_boss(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, RED, (0, 0, self.width, self.height))
        pygame.draw.rect(self.image, ORANGE, (0, 0, self.width, self.height), 4)
        pygame.draw.rect(self.image, BLACK, (20, 30, 30, 20))
        pygame.draw.rect(self.image, BLACK, (100, 30, 30, 20))
        pygame.draw.rect(self.image, BLACK, (55, 60, 40, 30))
    
    def update(self):
        if not self.entered:
            if self.rect.top < self.target_y:
                self.rect.y += self.speedy
            else:
                self.entered = True
        else:
            self.rect.x += self.speedx
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.speedx *= -1
        
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay and self.entered:
            self.last_shot = now
            self.shoot()
    
    def shoot(self):
        self.shoot_pattern = (self.shoot_pattern + 1) % 2
        if self.shoot_pattern == 0:
            for i in range(-3, 4):
                angle = math.radians(i * 15 - 90)
                dx = math.cos(angle) * 5
                dy = math.sin(angle) * 5
                bullet = Bullet(self.rect.centerx, self.rect.bottom, dx, dy, RED, True)
                self.game.enemy_bullets.add(bullet)
                self.game.all_sprites.add(bullet)
        else:
            for i in range(3):
                bullet = Bullet(self.rect.centerx + i * 30 - 30, self.rect.bottom, 0, 7, ORANGE, True)
                self.game.enemy_bullets.add(bullet)
                self.game.all_sprites.add(bullet)

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("星际守护者")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('simhei', 28)
        self.large_font = pygame.font.SysFont('simhei', 64)
        self.running = True
        self.state = 'menu'
        self.init_game()
    
    def init_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.boss = None
        
        self.starfield = StarField()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        
        self.score = 0
        self.lives = 3
        self.bomb_count = 1
        self.max_bombs = 3
        self.enemy_spawn_delay = 1500
        self.last_enemy_spawn = pygame.time.get_ticks()
        self.flash = 0
        self.boss_spawned = False
    
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pygame.quit()
    
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if self.state == 'menu':
                    if event.key == pygame.K_RETURN:
                        self.state = 'playing'
                        self.init_game()
                elif self.state == 'playing':
                    if event.key == pygame.K_b:
                        self.use_bomb()
                elif self.state == 'gameover' or self.state == 'victory':
                    if event.key == pygame.K_RETURN:
                        self.state = 'menu'
    
    def update(self):
        if self.state == 'playing':
            self.starfield.update()
            self.all_sprites.update()
            self.explosions.update()
            
            self.spawn_enemies()
            self.check_collisions()
            
            if self.score >= 1000 and not self.boss_spawned:
                self.spawn_boss()
            
            if self.flash > 0:
                self.flash -= 1
    
    def spawn_enemies(self):
        if self.boss_spawned:
            return
        now = pygame.time.get_ticks()
        if now - self.last_enemy_spawn > self.enemy_spawn_delay:
            self.last_enemy_spawn = now
            enemy = Enemy(self)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            self.enemy_spawn_delay = max(500, 1500 - self.score // 100 * 50)
    
    def spawn_boss(self):
        self.boss_spawned = True
        self.boss = Boss(self)
        self.all_sprites.add(self.boss)
        for enemy in self.enemies:
            enemy.kill()
    
    def use_bomb(self):
        if self.bomb_count > 0:
            self.bomb_count -= 1
            self.flash = 30
            for bullet in self.enemy_bullets:
                bullet.kill()
            for enemy in self.enemies:
                self.create_explosion(enemy.rect.center)
                enemy.kill()
                self.score += 10
            if self.boss:
                self.boss.hp -= 30
                if self.boss.hp <= 0:
                    self.boss_defeated()
    
    def create_explosion(self, pos):
        explosion = Explosion(pos[0], pos[1])
        self.explosions.add(explosion)
    
    def check_collisions(self):
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy in hits:
            enemy.hp -= 1
            if enemy.hp <= 0:
                self.create_explosion(enemy.rect.center)
                enemy.kill()
                self.score += 10
                if random.random() < 0.3:
                    power_type = 'bomb' if random.random() < 0.2 else 'weapon'
                    powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, power_type)
                    self.powerups.add(powerup)
                    self.all_sprites.add(powerup)
        
        if self.boss:
            hits = pygame.sprite.spritecollide(self.boss, self.bullets, True)
            for hit in hits:
                self.boss.hp -= 1
                if self.boss.hp <= 0:
                    self.boss_defeated()
        
        if not self.player.invincible:
            hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
            for hit in hits:
                self.create_explosion(hit.rect.center)
                self.player.get_hit()
            
            hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
            for hit in hits:
                self.player.get_hit()
        
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in hits:
            if powerup.power_type == 'weapon':
                if self.player.weapon_level < self.player.max_weapon_level:
                    self.player.weapon_level += 1
                else:
                    self.score += 50
            elif powerup.power_type == 'bomb':
                if self.bomb_count < self.max_bombs:
                    self.bomb_count += 1
                else:
                    self.score += 50
    
    def boss_defeated(self):
        self.create_explosion(self.boss.rect.center)
        self.boss.kill()
        self.boss = None
        self.state = 'victory'
    
    def game_over(self):
        self.state = 'gameover'
    
    def draw(self):
        self.screen.fill(BLACK)
        self.starfield.draw(self.screen)
        
        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'playing':
            self.draw_game()
        elif self.state == 'gameover':
            self.draw_game()
            self.draw_gameover()
        elif self.state == 'victory':
            self.draw_game()
            self.draw_victory()
        
        pygame.display.flip()
    
    def draw_menu(self):
        title = self.large_font.render("星际守护者", True, CYAN)
        start = self.font.render("按 Enter 开始游戏", True, WHITE)
        controls = self.font.render("WASD/方向键移动 空格射击 B炸弹", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 250))
        self.screen.blit(start, (SCREEN_WIDTH//2 - start.get_width()//2, 400))
        self.screen.blit(controls, (SCREEN_WIDTH//2 - controls.get_width()//2, 500))
    
    def draw_game(self):
        self.all_sprites.draw(self.screen)
        for explosion in self.explosions:
            explosion.draw(self.screen)
        self.draw_ui()
        
        if self.flash > 0:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, self.flash * 8))
            self.screen.blit(flash_surface, (0, 0))
        
        if self.boss and self.boss.entered:
            self.draw_boss_health()
    
    def draw_ui(self):
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 5))
        
        x = 120
        for i in range(self.lives):
            points = [(x, 5), (x + 8, 15), (x + 16, 5), (x + 8, 10)]
            pygame.draw.polygon(self.screen, RED, points)
            x += 25
        
        bomb_text = self.font.render(f"炸弹: {self.bomb_count}", True, WHITE)
        self.screen.blit(bomb_text, (SCREEN_WIDTH - 100, 5))
    
    def draw_boss_health(self):
        bar_width = 300
        bar_height = 20
        x = SCREEN_WIDTH // 2 - bar_width // 2
        y = 40
        
        pygame.draw.rect(self.screen, BLACK, (x, y, bar_width, bar_height))
        hp_percent = self.boss.hp / self.boss.max_hp
        pygame.draw.rect(self.screen, RED, (x, y, bar_width * hp_percent, bar_height))
        pygame.draw.rect(self.screen, WHITE, (x, y, bar_width, bar_height), 2)
        
        boss_text = self.font.render("BOSS", True, RED)
        self.screen.blit(boss_text, (SCREEN_WIDTH // 2 - boss_text.get_width() // 2, y - 30))
    
    def draw_gameover(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        text = self.large_font.render("游戏结束", True, RED)
        score = self.font.render(f"最终分数: {self.score}", True, WHITE)
        restart = self.font.render("按 Enter 返回菜单", True, WHITE)
        
        self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 300))
        self.screen.blit(score, (SCREEN_WIDTH//2 - score.get_width()//2, 400))
        self.screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 500))
    
    def draw_victory(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        text = self.large_font.render("胜利!", True, YELLOW)
        score = self.font.render(f"最终分数: {self.score}", True, WHITE)
        restart = self.font.render("按 Enter 返回菜单", True, WHITE)
        
        self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 300))
        self.screen.blit(score, (SCREEN_WIDTH//2 - score.get_width()//2, 400))
        self.screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 500))

if __name__ == "__main__":
    game = Game()
    game.run()
