# -*- coding: utf-8 -*-
"""
星际守护者 - Star Defender
使用 Python 3.9 + Pygame 2.5.2 开发的纵向卷轴射击游戏
"""

import pygame
import random
import math
from enum import Enum

# 初始化 Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# 游戏状态
class GameState(Enum):
    START = 1
    PLAYING = 2
    GAME_OVER = 3
    VICTORY = 4

# ==================== 星空背景类 ====================
class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 3.0)
        self.brightness = random.randint(150, 255)
    
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

class StarField:
    def __init__(self, star_count=100):
        self.stars = [Star() for _ in range(star_count)]
    
    def update(self):
        for star in self.stars:
            star.update()
    
    def draw(self, screen):
        for star in self.stars:
            star.draw(screen)

# ==================== 爆炸效果类 ====================
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, size=30, color=ORANGE):
        super().__init__()
        self.x = x
        self.y = y
        self.size = 1
        self.max_size = size
        self.color = color
        self.lifetime = 20
        self.age = 0
        self.alpha = 255
        # 创建透明表面作为image
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        self.age += 1
        progress = self.age / self.lifetime
        self.size = int(1 + (self.max_size - 1) * progress)
        self.alpha = int(255 * (1 - progress))
        
        # 更新图像
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*self.color, self.alpha), 
                          (self.size, self.size), self.size)
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
        if self.age >= self.lifetime:
            self.kill()

# ==================== 子弹类 ====================
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=-90, speed=10, color=YELLOW, is_enemy=False):
        super().__init__()
        self.x = x
        self.y = y
        self.angle_rad = math.radians(angle)
        self.speed = speed
        self.color = color
        self.is_enemy = is_enemy
        self.width = 4
        self.height = 12
        
        # 计算速度分量
        self.vx = math.cos(self.angle_rad) * self.speed
        self.vy = math.sin(self.angle_rad) * self.speed
        
        # 创建图像
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.color, (0, 0, self.width, self.height))
        self.rect = self.image.get_rect(center=(int(x), int(y)))
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (int(self.x), int(self.y))
        
        # 移除超出屏幕的子弹
        if self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT:
            self.kill()

# ==================== 玩家类 ====================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100
        self.speed = 5
        self.size = 20
        self.weapon_level = 1
        self.max_weapon_level = 3
        self.shoot_cooldown = 0
        self.shoot_delay = 10
        self.invincible = False
        self.invincible_time = 0
        
        # 创建图像
        self.update_image()
    
    def update_image(self):
        # 创建玩家战机图像（白色三角形）
        size = self.size * 2 + 10
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        center = size // 2
        points = [
            (center, center - self.size),
            (center - self.size, center + self.size),
            (center + self.size, center + self.size)
        ]
        pygame.draw.polygon(self.image, WHITE, points)
        pygame.draw.polygon(self.image, CYAN, points, 2)
        
        # 引擎火焰
        flame_points = [
            (center - self.size//2, center + self.size),
            (center + self.size//2, center + self.size),
            (center, center + self.size + 10)
        ]
        pygame.draw.polygon(self.image, ORANGE, flame_points)
        
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
    
    def update(self, keys):
        # 键盘控制
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        
        # 归一化对角线移动
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
        
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        # 边界限制
        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))
        
        # 更新位置
        self.rect.center = (int(self.x), int(self.y))
        
        # 射击冷却
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # 无敌时间
        if self.invincible:
            self.invincible_time -= 1
            if self.invincible_time <= 0:
                self.invincible = False
        
        # 更新图像（用于引擎火焰动画）
        self.update_image()
    
    def shoot(self, bullet_group):
        if self.shoot_cooldown <= 0:
            bullets = []
            if self.weapon_level == 1:
                # 单发
                bullets.append(Bullet(self.x, self.y - 20, -90, 10, YELLOW))
            elif self.weapon_level == 2:
                # 双发
                bullets.append(Bullet(self.x - 10, self.y - 15, -90, 10, YELLOW))
                bullets.append(Bullet(self.x + 10, self.y - 15, -90, 10, YELLOW))
            else:
                # 扇形散射
                bullets.append(Bullet(self.x, self.y - 20, -90, 10, YELLOW))
                bullets.append(Bullet(self.x, self.y - 20, -75, 10, YELLOW))
                bullets.append(Bullet(self.x, self.y - 20, -105, 10, YELLOW))
            
            for bullet in bullets:
                bullet_group.add(bullet)
            
            self.shoot_cooldown = self.shoot_delay
            return True
        return False
    
    def upgrade_weapon(self):
        if self.weapon_level < self.max_weapon_level:
            self.weapon_level += 1
            return True
        return False
    
    def make_invincible(self, frames=60):
        self.invincible = True
        self.invincible_time = frames

# ==================== 敌机类 ====================
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=2, hp=1):
        super().__init__()
        self.x = x
        self.y = y
        self.speed = speed
        self.size = 18
        self.hp = hp
        self.max_hp = hp
        self.shoot_cooldown = random.randint(30, 90)
        self.angle = 0
        
        # 创建图像
        self.update_image()
    
    def update_image(self):
        size = self.size * 2 + 10
        self.image = pygame.Surface((size, size + 10), pygame.SRCALPHA)
        center = size // 2
        
        # 绘制红色倒三角形
        points = [
            (center, center + self.size),
            (center - self.size, center - self.size),
            (center + self.size, center - self.size)
        ]
        pygame.draw.polygon(self.image, RED, points)
        pygame.draw.polygon(self.image, MAGENTA, points, 2)
        
        # 绘制血条（如果HP大于1）
        if self.max_hp > 1:
            bar_width = 30
            bar_height = 4
            hp_ratio = self.hp / self.max_hp
            bar_x = center - bar_width // 2
            bar_y = 2
            
            pygame.draw.rect(self.image, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.image, GREEN, (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
        
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
    
    def update(self):
        self.y += self.speed
        self.angle += 3
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        self.rect.center = (int(self.x), int(self.y))
        
        if self.y > SCREEN_HEIGHT + 50:
            self.kill()
    
    def shoot(self, bullet_group):
        if self.shoot_cooldown <= 0:
            bullet = Bullet(self.x, self.y + 20, 90, 5, RED, True)
            bullet_group.add(bullet)
            self.shoot_cooldown = random.randint(60, 120)
            return True
        return False
    
    def take_damage(self, damage=1):
        self.hp -= damage
        self.update_image()
        return self.hp <= 0

# ==================== Boss类 ====================
class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.x = SCREEN_WIDTH // 2
        self.y = 100
        self.width = 120
        self.height = 80
        self.hp = 100
        self.max_hp = 100
        self.speed = 1.5
        self.direction = 1
        self.shoot_cooldown = 0
        self.shoot_pattern = 0
        self.angle = 0
        
        self.update_image()
    
    def update_image(self):
        self.image = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
        center_x = (self.width + 10) // 2
        center_y = (self.height + 10) // 2
        
        # 绘制Boss主体（大矩形）
        rect = pygame.Rect(center_x - self.width//2, center_y - self.height//2, 
                          self.width, self.height)
        pygame.draw.rect(self.image, DARK_GRAY, rect)
        pygame.draw.rect(self.image, RED, rect, 3)
        
        # 绘制Boss核心
        core_size = 30
        pygame.draw.circle(self.image, MAGENTA, (center_x, center_y), core_size)
        pygame.draw.circle(self.image, WHITE, (center_x, center_y), core_size - 5)
        
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
    
    def update(self):
        # 左右移动
        self.x += self.speed * self.direction
        if self.x <= self.width // 2 + 20 or self.x >= SCREEN_WIDTH - self.width // 2 - 20:
            self.direction *= -1
        
        self.angle += 2
        self.rect.center = (int(self.x), int(self.y))
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def shoot(self, bullet_group):
        if self.shoot_cooldown <= 0:
            if self.shoot_pattern == 0:
                # 环形弹幕
                for i in range(12):
                    angle = self.angle + i * 30
                    bullet = Bullet(self.x, self.y + 40, angle, 4, RED, True)
                    bullet_group.add(bullet)
                self.shoot_pattern = 1
                self.shoot_cooldown = 60
            else:
                # 快速连射
                for i in range(-2, 3):
                    angle = 90 + i * 15
                    bullet = Bullet(self.x, self.y + 40, angle, 6, RED, True)
                    bullet_group.add(bullet)
                self.shoot_pattern = 0
                self.shoot_cooldown = 40
            return True
        return False
    
    def take_damage(self, damage=1):
        self.hp -= damage
        return self.hp <= 0
    
    def draw(self, screen):
        # 绘制Boss图像
        screen.blit(self.image, self.rect)
        
        # 绘制血条
        bar_width = 200
        bar_height = 15
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 20
        
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        hp_ratio = self.hp / self.max_hp
        hp_color = GREEN if hp_ratio > 0.5 else (YELLOW if hp_ratio > 0.25 else RED)
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # 绘制Boss文字
        font = pygame.font.SysFont("simhei", 20)
        text = font.render("BOSS", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height + 15))
        screen.blit(text, text_rect)

# ==================== 能量块类 ====================
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type="weapon"):
        super().__init__()
        self.x = x
        self.y = y
        self.size = 12
        self.speed = 2
        self.power_type = power_type  # "weapon" 或 "bomb"
        self.angle = 0
        
        self.update_image()
    
    def update_image(self):
        size = self.size * 2 + 5
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        
        if self.power_type == "weapon":
            # 绘制绿色矩形
            rect_size = self.size
            pygame.draw.rect(self.image, GREEN, 
                           (center - rect_size//2, center - rect_size//2, rect_size, rect_size))
            pygame.draw.rect(self.image, WHITE, 
                           (center - rect_size//2, center - rect_size//2, rect_size, rect_size), 2)
            
            # 绘制W字样
            font = pygame.font.SysFont("simhei", 12)
            text = font.render("W", True, BLACK)
            text_rect = text.get_rect(center=(center, center))
            self.image.blit(text, text_rect)
        else:
            # 绘制炸弹补给（蓝色圆形）
            pygame.draw.circle(self.image, BLUE, (center, center), self.size)
            pygame.draw.circle(self.image, WHITE, (center, center), self.size, 2)
            
            # 绘制B字样
            font = pygame.font.SysFont("simhei", 12)
            text = font.render("B", True, WHITE)
            text_rect = text.get_rect(center=(center, center))
            self.image.blit(text, text_rect)
        
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
    
    def update(self):
        self.y += self.speed
        self.angle += 5
        self.rect.center = (int(self.x), int(self.y))
        
        if self.y > SCREEN_HEIGHT + 50:
            self.kill()

# ==================== 炸弹效果类 ====================
class BombEffect:
    def __init__(self):
        self.active = False
        self.radius = 0
        self.max_radius = int(math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2))
        self.alpha = 255
        
    def trigger(self):
        self.active = True
        self.radius = 10
        self.alpha = 255
    
    def update(self):
        if self.active:
            self.radius += 30
            if self.radius >= self.max_radius:
                self.alpha -= 10
                if self.alpha <= 0:
                    self.active = False
    
    def draw(self, screen):
        if self.active:
            surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 255, 200, self.alpha), 
                             (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), self.radius)
            screen.blit(surface, (0, 0))

# ==================== 游戏主类 ====================
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("星际守护者 - Star Defender")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.START
        
        # 初始化字体
        self.font_large = pygame.font.SysFont("simhei", 48)
        self.font_medium = pygame.font.SysFont("simhei", 32)
        self.font_small = pygame.font.SysFont("simhei", 20)
        
        # 游戏数据
        self.reset_game()
        
        # 星空背景
        self.starfield = StarField(150)
        
        # 炸弹效果
        self.bomb_effect = BombEffect()
    
    def reset_game(self):
        # 玩家
        self.player = Player()
        
        # 精灵组
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        # Boss
        self.boss = None
        self.boss_defeated = False
        
        # 游戏数据
        self.score = 0
        self.lives = 3
        self.bomb_count = 1
        self.max_bombs = 3
        
        # 敌机生成
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 60
        self.difficulty_multiplier = 1.0
        
        # 游戏状态
        self.state = GameState.PLAYING
    
    def spawn_enemy(self):
        if self.boss is not None:
            return
        
        self.enemy_spawn_timer += 1
        
        # 根据分数调整难度
        if self.score >= 1000 and self.boss is None and not self.boss_defeated:
            self.spawn_boss()
            return
        
        spawn_delay = max(20, int(self.enemy_spawn_delay / self.difficulty_multiplier))
        
        if self.enemy_spawn_timer >= spawn_delay:
            self.enemy_spawn_timer = 0
            x = random.randint(30, SCREEN_WIDTH - 30)
            
            # 根据分数增加敌机强度
            if self.score > 500:
                speed = random.uniform(2, 4)
                hp = random.randint(1, 3)
            else:
                speed = random.uniform(1.5, 3)
                hp = 1
            
            enemy = Enemy(x, -30, speed, hp)
            self.enemies.add(enemy)
    
    def spawn_boss(self):
        self.boss = Boss()
        # 清除现有敌机
        for enemy in self.enemies:
            enemy.kill()
    
    def use_bomb(self):
        if self.bomb_count > 0 and not self.bomb_effect.active:
            self.bomb_count -= 1
            self.bomb_effect.trigger()
            
            # 清除所有敌方子弹
            for bullet in self.enemy_bullets:
                bullet.kill()
            
            # 对普通敌机造成伤害
            for enemy in self.enemies:
                enemy.take_damage(10)
                if enemy.hp <= 0:
                    self.create_explosion(enemy.x, enemy.y)
                    enemy.kill()
            
            # 对Boss造成伤害
            if self.boss:
                self.boss.take_damage(20)
                if self.boss.hp <= 0:
                    self.boss_defeated = True
                    self.create_explosion(self.boss.x, self.boss.y, 80)
                    self.boss = None
                    self.score += 500
    
    def create_explosion(self, x, y, size=30):
        explosion = Explosion(x, y, size)
        self.explosions.add(explosion)
    
    def check_collisions(self):
        # 玩家子弹击中敌机
        for bullet in self.bullets:
            # 检查击中Boss
            if self.boss and self.boss.rect.colliderect(bullet.rect):
                bullet.kill()
                if self.boss.take_damage(1):
                    self.boss_defeated = True
                    self.create_explosion(self.boss.x, self.boss.y, 80)
                    self.boss = None
                    self.score += 500
                break
            
            # 检查击中普通敌机
            for enemy in self.enemies:
                if enemy.rect.colliderect(bullet.rect):
                    bullet.kill()
                    if enemy.take_damage(1):
                        self.create_explosion(enemy.x, enemy.y)
                        self.score += 10 * enemy.max_hp
                        
                        # 掉落能量块
                        if random.random() < 0.3:
                            power_type = "bomb" if random.random() < 0.2 else "weapon"
                            powerup = PowerUp(enemy.x, enemy.y, power_type)
                            self.powerups.add(powerup)
                        
                        enemy.kill()
                    break
        
        # 敌机子弹击中玩家
        if not self.player.invincible:
            for bullet in self.enemy_bullets:
                if self.player.rect.colliderect(bullet.rect):
                    bullet.kill()
                    self.player_hit()
                    break
        
        # 敌机撞击玩家
        if not self.player.invincible:
            for enemy in self.enemies:
                if self.player.rect.colliderect(enemy.rect):
                    self.create_explosion(enemy.x, enemy.y)
                    enemy.kill()
                    self.player_hit()
                    break
            
            # Boss撞击玩家
            if self.boss and self.player.rect.colliderect(self.boss.rect):
                self.player_hit()
        
        # 收集能量块
        for powerup in self.powerups:
            if self.player.rect.colliderect(powerup.rect):
                if powerup.power_type == "weapon":
                    if not self.player.upgrade_weapon():
                        self.score += 50
                else:  # bomb
                    self.bomb_count = min(self.max_bombs, self.bomb_count + 1)
                powerup.kill()
    
    def player_hit(self):
        self.lives -= 1
        self.create_explosion(self.player.x, self.player.y, 50)
        
        if self.lives <= 0:
            self.state = GameState.GAME_OVER
        else:
            self.player.make_invincible(120)
            self.player.weapon_level = 1
    
    def update(self):
        keys = pygame.key.get_pressed()
        
        if self.state == GameState.PLAYING:
            # 更新星空背景
            self.starfield.update()
            
            # 更新玩家
            self.player.update(keys)
            
            # 自动射击
            self.player.shoot(self.bullets)
            
            # 使用炸弹
            if keys[pygame.K_b]:
                self.use_bomb()
            
            # 生成敌机
            self.spawn_enemy()
            
            # 更新子弹
            self.bullets.update()
            self.enemy_bullets.update()
            
            # 更新敌机
            for enemy in self.enemies:
                enemy.update()
                enemy.shoot(self.enemy_bullets)
            
            # 更新Boss
            if self.boss:
                self.boss.update()
                self.boss.shoot(self.enemy_bullets)
            
            # 更新爆炸效果
            self.explosions.update()
            
            # 更新能量块
            self.powerups.update()
            
            # 更新炸弹效果
            self.bomb_effect.update()
            
            # 碰撞检测
            self.check_collisions()
            
            # 更新难度
            self.difficulty_multiplier = 1.0 + (self.score / 1000)
            
            # 检查胜利
            if self.boss_defeated:
                self.state = GameState.VICTORY
    
    def draw_ui(self):
        # 绘制分数
        score_text = self.font_small.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # 绘制生命值（心形）
        heart_y = 35
        for i in range(self.lives):
            heart_x = 15 + i * 25
            self.draw_heart(heart_x, heart_y, 8)
        
        # 绘制炸弹数量
        bomb_text = self.font_small.render(f"炸弹(B): {self.bomb_count}/{self.max_bombs}", True, BLUE)
        self.screen.blit(bomb_text, (10, 55))
        
        # 绘制武器等级
        weapon_colors = [WHITE, YELLOW, ORANGE]
        weapon_color = weapon_colors[min(self.player.weapon_level - 1, 2)]
        weapon_text = self.font_small.render(f"武器等级: {self.player.weapon_level}", True, weapon_color)
        self.screen.blit(weapon_text, (10, 80))
        
        # Boss战时显示提示
        if self.boss:
            warning_text = self.font_medium.render("WARNING: BOSS APPROACHING", True, RED)
            text_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(warning_text, text_rect)
    
    def draw_heart(self, x, y, size):
        # 绘制简单心形
        points = []
        for i in range(20):
            t = i * 2 * math.pi / 20
            hx = size * 16 * math.sin(t) ** 3
            hy = -size * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            points.append((x + hx / 16, y + hy / 16))
        pygame.draw.polygon(self.screen, RED, points)
    
    def draw(self):
        # 清屏
        self.screen.fill(BLACK)
        
        if self.state == GameState.START:
            self.draw_start_screen()
        elif self.state == GameState.PLAYING:
            # 绘制星空
            self.starfield.draw(self.screen)
            
            # 绘制游戏对象
            self.powerups.draw(self.screen)
            self.bullets.draw(self.screen)
            self.enemy_bullets.draw(self.screen)
            self.enemies.draw(self.screen)
            
            if self.boss:
                self.boss.draw(self.screen)
            
            # 绘制玩家（无敌时闪烁）
            if not self.player.invincible or self.player.invincible_time % 10 < 5:
                self.screen.blit(self.player.image, self.player.rect)
            
            self.explosions.draw(self.screen)
            
            # 绘制炸弹效果
            self.bomb_effect.draw(self.screen)
            
            # 绘制UI
            self.draw_ui()
            
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over_screen()
        elif self.state == GameState.VICTORY:
            self.draw_victory_screen()
        
        pygame.display.flip()
    
    def draw_start_screen(self):
        # 绘制星空
        self.starfield.update()
        self.starfield.draw(self.screen)
        
        title = self.font_large.render("星际守护者", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Star Defender", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 260))
        self.screen.blit(subtitle, subtitle_rect)
        
        instructions = [
            "操作说明:",
            "WASD 或 方向键 - 移动",
            "自动射击 - 无需按键",
            "B键 - 使用炸弹",
            "",
            "按空格键开始游戏"
        ]
        
        y = 350
        for line in instructions:
            text = self.font_small.render(line, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 30
    
    def draw_game_over_screen(self):
        # 绘制星空
        self.starfield.draw(self.screen)
        
        title = self.font_large.render("游戏结束", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(title, title_rect)
        
        score_text = self.font_medium.render(f"最终分数: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 380))
        self.screen.blit(score_text, score_rect)
        
        restart = self.font_small.render("按空格键重新开始", True, YELLOW)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, 450))
        self.screen.blit(restart, restart_rect)
    
    def draw_victory_screen(self):
        # 绘制星空
        self.starfield.update()
        self.starfield.draw(self.screen)
        
        title = self.font_large.render("胜利!", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(title, title_rect)
        
        score_text = self.font_medium.render(f"最终分数: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 380))
        self.screen.blit(score_text, score_rect)
        
        restart = self.font_small.render("按空格键开始下一周目", True, YELLOW)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, 450))
        self.screen.blit(restart, restart_rect)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == GameState.START:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.GAME_OVER:
                        self.reset_game()
                    elif self.state == GameState.VICTORY:
                        self.reset_game()
                        # 胜利后增加难度
                        self.difficulty_multiplier += 0.5
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

# 主程序入口
if __name__ == "__main__":
    game = Game()
    game.run()
