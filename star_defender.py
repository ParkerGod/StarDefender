# -*- coding: utf-8 -*-
import pygame
import random
import math
import sys

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 100, 255)
PURPLE = (150, 0, 255)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

class StarField:
    def __init__(self):
        self.stars = []
        for _ in range(150):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            speed = random.uniform(1, 4)
            size = random.randint(1, 3)
            brightness = random.randint(100, 255)
            self.stars.append([x, y, speed, size, brightness])
    
    def update(self):
        for star in self.stars:
            star[1] += star[2]
            if star[1] > SCREEN_HEIGHT:
                star[0] = random.randint(0, SCREEN_WIDTH)
                star[1] = 0
                star[2] = random.uniform(1, 4)
    
    def draw(self, screen):
        for star in self.stars:
            color = (star[4], star[4], star[4])
            if star[3] == 1:
                screen.set_at((int(star[0]), int(star[1])), color)
            else:
                pygame.draw.circle(screen, color, (int(star[0]), int(star[1])), star[3])


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 40
        self.height = 50
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._draw_ship()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 20
        self.speed = 6
        self.lives = 3
        self.weapon_level = 1
        self.max_weapon_level = 5
        self.shoot_delay = 200
        self.last_shot = pygame.time.get_ticks()
        self.invincible = False
        self.invincible_timer = 0
        self.flash_timer = 0
    
    def _draw_ship(self):
        points = [
            (self.width // 2, 0),
            (0, self.height),
            (self.width // 4, self.height - 10),
            (self.width * 3 // 4, self.height - 10),
            (self.width, self.height)
        ]
        pygame.draw.polygon(self.image, WHITE, points)
        pygame.draw.polygon(self.image, CYAN, points, 2)
        engine_points = [
            (self.width // 4, self.height - 5),
            (self.width // 2, self.height + 5),
            (self.width * 3 // 4, self.height - 5)
        ]
        pygame.draw.polygon(self.image, ORANGE, engine_points)
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
        
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        
        if self.invincible:
            if pygame.time.get_ticks() - self.invincible_timer > 2000:
                self.invincible = False
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullets = []
            if self.weapon_level == 1:
                bullets.append(Bullet(self.rect.centerx, self.rect.top, 0, -10))
            elif self.weapon_level == 2:
                bullets.append(Bullet(self.rect.centerx - 10, self.rect.top, 0, -10))
                bullets.append(Bullet(self.rect.centerx + 10, self.rect.top, 0, -10))
            elif self.weapon_level == 3:
                bullets.append(Bullet(self.rect.centerx, self.rect.top, 0, -10))
                bullets.append(Bullet(self.rect.centerx - 15, self.rect.top, -1, -10))
                bullets.append(Bullet(self.rect.centerx + 15, self.rect.top, 1, -10))
            elif self.weapon_level == 4:
                bullets.append(Bullet(self.rect.centerx - 10, self.rect.top, 0, -10))
                bullets.append(Bullet(self.rect.centerx + 10, self.rect.top, 0, -10))
                bullets.append(Bullet(self.rect.centerx - 20, self.rect.top, -2, -9))
                bullets.append(Bullet(self.rect.centerx + 20, self.rect.top, 2, -9))
            else:
                for angle in range(-30, 31, 15):
                    rad = math.radians(angle)
                    vx = math.sin(rad) * 10
                    vy = -math.cos(rad) * 10
                    bullets.append(Bullet(self.rect.centerx, self.rect.top, vx, vy))
            return bullets
        return []
    
    def draw(self, screen):
        if self.invincible:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                screen.blit(self.image, self.rect)
        else:
            screen.blit(self.image, self.rect)
    
    def hit(self):
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            return True
        return False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, is_enemy=False):
        super().__init__()
        self.is_enemy = is_enemy
        if is_enemy:
            self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(self.image, RED, (4, 4), 4)
        else:
            self.image = pygame.Surface((6, 15), pygame.SRCALPHA)
            pygame.draw.rect(self.image, YELLOW, (0, 0, 6, 15))
            pygame.draw.rect(self.image, ORANGE, (1, 0, 4, 15))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.vx = vx
        self.vy = vy
    
    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type="normal"):
        super().__init__()
        self.enemy_type = enemy_type
        if enemy_type == "normal":
            self.width = 30
            self.height = 35
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            points = [
                (self.width // 2, self.height),
                (0, 0),
                (self.width // 4, 10),
                (self.width * 3 // 4, 10),
                (self.width, 0)
            ]
            pygame.draw.polygon(self.image, RED, points)
            pygame.draw.polygon(self.image, ORANGE, points, 2)
            self.health = 1
            self.speed = random.uniform(2, 4)
            self.score_value = 10
        elif enemy_type == "fast":
            self.width = 25
            self.height = 30
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            points = [
                (self.width // 2, self.height),
                (0, 5),
                (self.width // 2, 0),
                (self.width, 5)
            ]
            pygame.draw.polygon(self.image, PURPLE, points)
            pygame.draw.polygon(self.image, WHITE, points, 2)
            self.health = 1
            self.speed = random.uniform(4, 6)
            self.score_value = 15
        elif enemy_type == "tank":
            self.width = 40
            self.height = 45
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            points = [
                (self.width // 2, self.height),
                (0, 10),
                (0, 0),
                (self.width, 0),
                (self.width, 10)
            ]
            pygame.draw.polygon(self.image, ORANGE, points)
            pygame.draw.polygon(self.image, RED, points, 2)
            self.health = 3
            self.speed = random.uniform(1.5, 2.5)
            self.score_value = 30
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.rect.y = -self.height
        self.shoot_timer = 0
        self.shoot_delay = random.randint(1500, 3000)
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
    
    def can_shoot(self):
        now = pygame.time.get_ticks()
        if now - self.shoot_timer > self.shoot_delay:
            self.shoot_timer = now
            return True
        return False


class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 150
        self.height = 100
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self._draw_boss()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.y = -self.height
        self.target_y = 50
        self.max_health = 100
        self.health = self.max_health
        self.speed = 2
        self.direction = 1
        self.shoot_timer = 0
        self.shoot_delay = 500
        self.attack_pattern = 0
        self.entering = True
        self.score_value = 500
    
    def _draw_boss(self):
        pygame.draw.rect(self.image, RED, (20, 10, 110, 80))
        pygame.draw.rect(self.image, ORANGE, (20, 10, 110, 80), 3)
        pygame.draw.rect(self.image, (100, 0, 0), (0, 30, 30, 40))
        pygame.draw.rect(self.image, (100, 0, 0), (120, 30, 30, 40))
        pygame.draw.polygon(self.image, YELLOW, [
            (self.width // 2, 90),
            (self.width // 2 - 15, 70),
            (self.width // 2 + 15, 70)
        ])
        pygame.draw.circle(self.image, CYAN, (self.width // 2, 40), 15)
        pygame.draw.circle(self.image, WHITE, (self.width // 2, 40), 10)
    
    def update(self):
        if self.entering:
            if self.rect.y < self.target_y:
                self.rect.y += 2
            else:
                self.entering = False
        else:
            self.rect.x += self.speed * self.direction
            if self.rect.right >= SCREEN_WIDTH:
                self.direction = -1
            if self.rect.left <= 0:
                self.direction = 1
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.shoot_timer > self.shoot_delay and not self.entering:
            self.shoot_timer = now
            bullets = []
            self.attack_pattern = (self.attack_pattern + 1) % 3
            
            if self.attack_pattern == 0:
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    vx = math.sin(rad) * 5
                    vy = math.cos(rad) * 5
                    b = Bullet(self.rect.centerx, self.rect.centery, vx, vy, is_enemy=True)
                    bullets.append(b)
            elif self.attack_pattern == 1:
                for i in range(-2, 3):
                    b = Bullet(self.rect.centerx + i * 20, self.rect.bottom, 0, 6, is_enemy=True)
                    bullets.append(b)
            else:
                for i in range(5):
                    angle = -30 + i * 15
                    rad = math.radians(angle)
                    vx = math.sin(rad) * 6
                    vy = math.cos(rad) * 6
                    b = Bullet(self.rect.centerx, self.rect.bottom, vx, vy, is_enemy=True)
                    bullets.append(b)
            
            return bullets
        return []
    
    def draw_health_bar(self, screen):
        bar_width = 200
        bar_height = 20
        x = (SCREEN_WIDTH - bar_width) // 2
        y = 10
        pygame.draw.rect(screen, RED, (x, y, bar_width, bar_height))
        health_width = int(bar_width * self.health / self.max_health)
        pygame.draw.rect(screen, GREEN, (x, y, health_width, bar_height))
        pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height), 2)


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type="weapon"):
        super().__init__()
        self.power_type = power_type
        self.size = 20
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.angle = 0
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 2
    
    def update(self):
        self.rect.y += self.speed
        self.angle += 3
        self._draw_powerup()
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
    
    def _draw_powerup(self):
        self.image.fill((0, 0, 0, 0))
        if self.power_type == "weapon":
            points = []
            for i in range(4):
                angle = math.radians(self.angle + i * 90)
                x = self.size // 2 + math.cos(angle) * 8
                y = self.size // 2 + math.sin(angle) * 8
                points.append((x, y))
            pygame.draw.polygon(self.image, GREEN, points)
            pygame.draw.polygon(self.image, WHITE, points, 2)
        elif self.power_type == "bomb":
            pygame.draw.circle(self.image, BLUE, (self.size // 2, self.size // 2), 8)
            pygame.draw.circle(self.image, CYAN, (self.size // 2, self.size // 2), 5)
        elif self.power_type == "life":
            self._draw_heart(self.size // 2, self.size // 2, 8)
    
    def _draw_heart(self, x, y, size):
        pygame.draw.circle(self.image, RED, (x - size // 2, y), size // 2)
        pygame.draw.circle(self.image, RED, (x + size // 2, y), size // 2)
        points = [(x - size, y), (x + size, y), (x, y + size)]
        pygame.draw.polygon(self.image, RED, points)


class Explosion:
    def __init__(self, x, y, color=ORANGE, max_radius=40):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = max_radius
        self.color = color
        self.finished = False
        self.growth_rate = 3
    
    def update(self):
        self.radius += self.growth_rate
        if self.radius >= self.max_radius:
            self.finished = True
    
    def draw(self, screen):
        alpha = int(255 * (1 - self.radius / self.max_radius))
        for i in range(3):
            r = self.radius - i * 10
            if r > 0:
                color = (
                    min(255, self.color[0] + i * 30),
                    max(0, self.color[1] - i * 50),
                    0
                )
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(r), 2)


class FlashEffect:
    def __init__(self):
        self.active = False
        self.alpha = 255
        self.duration = 10
        self.frame = 0
    
    def trigger(self):
        self.active = True
        self.alpha = 200
        self.frame = 0
    
    def update(self):
        if self.active:
            self.frame += 1
            self.alpha = max(0, 200 - self.frame * 25)
            if self.frame >= self.duration:
                self.active = False
    
    def draw(self, screen):
        if self.active and self.alpha > 0:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.fill(WHITE)
            flash_surface.set_alpha(self.alpha)
            screen.blit(flash_surface, (0, 0))


class EnemySpawner:
    def __init__(self):
        self.spawn_timer = 0
        self.base_delay = 1500
        self.min_delay = 400
        self.boss_spawned = False
    
    def update(self, score):
        now = pygame.time.get_ticks()
        delay = max(self.min_delay, self.base_delay - score // 10)
        
        if now - self.spawn_timer > delay:
            self.spawn_timer = now
            if random.random() < 0.7:
                return Enemy("normal")
            elif random.random() < 0.8:
                return Enemy("fast")
            else:
                return Enemy("tank")
        return None
    
    def should_spawn_boss(self, score):
        return score >= 1000 and not self.boss_spawned


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Star Defender - Xing Ji Shou Hu Zhe")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 72)
        
        self.state = "start"
        self.reset_game()
    
    def reset_game(self):
        self.star_field = StarField()
        self.player = Player()
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        self.all_sprites.add(self.player)
        
        self.score = 0
        self.bomb_count = 1
        self.max_bombs = 3
        self.explosions = []
        self.flash_effect = FlashEffect()
        self.spawner = EnemySpawner()
        self.boss = None
        self.game_won = False
        self.loop_count = 1
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == "start":
                    if event.key == pygame.K_SPACE:
                        self.state = "playing"
                        self.reset_game()
                
                elif self.state == "playing":
                    if event.key == pygame.K_b:
                        self.use_bomb()
                    if event.key == pygame.K_ESCAPE:
                        self.state = "start"
                
                elif self.state == "game_over":
                    if event.key == pygame.K_SPACE:
                        self.state = "start"
                
                elif self.state == "victory":
                    if event.key == pygame.K_SPACE:
                        self.state = "playing"
                        self.loop_count += 1
                        self.reset_game()
        
        return True
    
    def use_bomb(self):
        if self.bomb_count > 0:
            self.bomb_count -= 1
            self.flash_effect.trigger()
            
            for enemy in self.enemies:
                if not isinstance(enemy, Boss):
                    self.explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                    if random.random() < 0.3:
                        power_type = random.choice(["weapon", "bomb", "life"])
                        self.powerups.add(PowerUp(enemy.rect.centerx, enemy.rect.centery, power_type))
                    self.score += enemy.score_value
                    enemy.kill()
            
            for bullet in self.enemy_bullets:
                bullet.kill()
            
            if self.boss:
                self.boss.health -= 20
    
    def update(self):
        if self.state != "playing":
            return
        
        self.star_field.update()
        self.player.update()
        
        bullets = self.player.shoot()
        for bullet in bullets:
            self.bullets.add(bullet)
            self.all_sprites.add(bullet)
        
        self.bullets.update()
        self.enemy_bullets.update()
        self.enemies.update()
        self.powerups.update()
        
        for bullet in self.bullets:
            hits = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for enemy in hits:
                enemy.health -= 1
                bullet.kill()
                
                if enemy.health <= 0:
                    self.explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery))
                    
                    if random.random() < 0.25:
                        power_type = random.choice(["weapon", "bomb", "life"])
                        self.powerups.add(PowerUp(enemy.rect.centerx, enemy.rect.centery, power_type))
                    
                    self.score += enemy.score_value
                    enemy.kill()
        
        for bullet in self.enemy_bullets:
            if pygame.sprite.collide_rect(bullet, self.player):
                if self.player.hit():
                    self.explosions.append(Explosion(self.player.rect.centerx, self.player.rect.centery, CYAN))
                    bullet.kill()
                    if self.player.lives <= 0:
                        self.state = "game_over"
        
        for enemy in self.enemies:
            if pygame.sprite.collide_rect(enemy, self.player):
                if self.player.hit():
                    self.explosions.append(Explosion(self.player.rect.centerx, self.player.rect.centery, CYAN))
                    if self.player.lives <= 0:
                        self.state = "game_over"
            
            if not isinstance(enemy, Boss) and enemy.can_shoot():
                b = Bullet(enemy.rect.centerx, enemy.rect.bottom, 0, 5, is_enemy=True)
                self.enemy_bullets.add(b)
        
        powerup_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerup_hits:
            if powerup.power_type == "weapon":
                if self.player.weapon_level < self.player.max_weapon_level:
                    self.player.weapon_level += 1
                else:
                    self.score += 50
            elif powerup.power_type == "bomb":
                if self.bomb_count < self.max_bombs:
                    self.bomb_count += 1
                else:
                    self.score += 30
            elif powerup.power_type == "life":
                self.player.lives = min(5, self.player.lives + 1)
        
        if not self.boss:
            if self.spawner.should_spawn_boss(self.score):
                self.boss = Boss()
                self.enemies.add(self.boss)
            else:
                new_enemy = self.spawner.update(self.score)
                if new_enemy:
                    self.enemies.add(new_enemy)
        else:
            if self.boss.alive():
                boss_bullets = self.boss.shoot()
                for bullet in boss_bullets:
                    self.enemy_bullets.add(bullet)
            else:
                self.explosions.append(Explosion(self.boss.rect.centerx, self.boss.rect.centery, PURPLE, 80))
                self.score += 500
                self.boss = None
                self.spawner.boss_spawned = False
                self.state = "victory"
        
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.finished:
                self.explosions.remove(explosion)
        
        self.flash_effect.update()
    
    def draw(self):
        self.screen.fill(BLACK)
        self.star_field.draw(self.screen)
        
        if self.state == "start":
            self.draw_start_screen()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "game_over":
            self.draw_game()
            self.draw_game_over()
        elif self.state == "victory":
            self.draw_game()
            self.draw_victory()
        
        pygame.display.flip()
    
    def draw_start_screen(self):
        title = self.title_font.render("STAR DEFENDER", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
        
        subtitle = self.font.render("Xing Ji Shou Hu Zhe", True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 280))
        
        instructions = [
            "WASD or Arrow Keys - Move",
            "SPACE - Shoot (Auto)",
            "B - Use Bomb",
            "",
            "Press SPACE to Start"
        ]
        
        y = 400
        for line in instructions:
            text = self.small_font.render(line, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 30
    
    def draw_game(self):
        for bullet in self.bullets:
            self.screen.blit(bullet.image, bullet.rect)
        
        for bullet in self.enemy_bullets:
            self.screen.blit(bullet.image, bullet.rect)
        
        for enemy in self.enemies:
            self.screen.blit(enemy.image, enemy.rect)
        
        for powerup in self.powerups:
            self.screen.blit(powerup.image, powerup.rect)
        
        self.player.draw(self.screen)
        
        for explosion in self.explosions:
            explosion.draw(self.screen)
        
        self.flash_effect.draw(self.screen)
        
        if self.boss:
            self.boss.draw_health_bar(self.screen)
        
        self.draw_ui()
    
    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        lives_text = self.font.render("Lives: ", True, WHITE)
        self.screen.blit(lives_text, (10, 45))
        for i in range(self.player.lives):
            self.draw_heart(90 + i * 25, 55, 8)
        
        bomb_text = self.font.render(f"Bombs: {self.bomb_count}", True, WHITE)
        self.screen.blit(bomb_text, (SCREEN_WIDTH - 120, 10))
        
        weapon_text = self.small_font.render(f"Weapon Lv.{self.player.weapon_level}", True, GREEN)
        self.screen.blit(weapon_text, (SCREEN_WIDTH - 100, 45))
        
        if self.loop_count > 1:
            loop_text = self.small_font.render(f"Loop {self.loop_count}", True, YELLOW)
            self.screen.blit(loop_text, (SCREEN_WIDTH // 2 - loop_text.get_width() // 2, 10))
    
    def draw_heart(self, x, y, size):
        pygame.draw.circle(self.screen, RED, (x - size // 2, y), size // 2)
        pygame.draw.circle(self.screen, RED, (x + size // 2, y), size // 2)
        points = [(x - size, y), (x + size, y), (x, y + size)]
        pygame.draw.polygon(self.screen, RED, points)
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(150)
        self.screen.blit(overlay, (0, 0))
        
        text = self.title_font.render("GAME OVER", True, RED)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300))
        
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 400))
        
        restart_text = self.small_font.render("Press SPACE to Restart", True, WHITE)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 500))
    
    def draw_victory(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(150)
        self.screen.blit(overlay, (0, 0))
        
        text = self.title_font.render("VICTORY!", True, GREEN)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300))
        
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 400))
        
        continue_text = self.small_font.render("Press SPACE for Next Loop", True, YELLOW)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 500))
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
