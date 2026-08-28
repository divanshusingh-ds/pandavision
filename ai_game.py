import pygame
import random
import numpy as np
from collections import deque

class AIObstacleGenerator:
    def __init__(self):
        self.difficulty = 1
        self.patterns = deque(maxlen=20)
        self.last_spawn_score = 0
        
    def get_next_obstacle(self, score, speed):
        # Difficulty increases with score
        self.difficulty = 1 + (score // 100) * 0.3
        
        # Smart spacing
        min_gap = max(60, 150 - self.difficulty * 10)
        
        # Predict next obstacle type
        if len(self.patterns) > 5:
            # Most common pattern
            from collections import Counter
            counter = Counter(self.patterns)
            next_type = counter.most_common(1)[0][0]
        else:
            next_type = random.choice(['cactus', 'bird'])
        
        # Create obstacle
        obstacle = {
            'type': next_type,
            'x': 800,
            'y': 400 if next_type == 'cactus' else 330,
            'width': 30 if next_type == 'cactus' else 40,
            'height': 40 if next_type == 'cactus' else 30,
            'speed': 6 + self.difficulty * 0.5
        }
        
        self.patterns.append(next_type)
        self.last_spawn_score = score
        
        return obstacle

class AIDifficultyController:
    def __init__(self):
        self.difficulty = 1
        self.player_jumps = 0
        self.player_deaths = 0
        self.success_rate = 0.5
        
    def update(self, jumps, deaths, obstacles_passed):
        self.player_jumps = jumps
        self.player_deaths = deaths
        
        if jumps > 0:
            self.success_rate = (jumps - deaths) / jumps
        
        # Auto-adjust difficulty
        if self.success_rate > 0.8:
            self.difficulty = min(10, self.difficulty + 0.1)
        elif self.success_rate < 0.4:
            self.difficulty = max(1, self.difficulty - 0.1)
        
        return {
            'speed': 6 + (self.difficulty - 1) * 0.5,
            'spawn_rate': max(60, 150 - self.difficulty * 10),
            'difficulty': round(self.difficulty, 1)
        }

class AIAnalyzer:
    def __init__(self):
        self.history = deque(maxlen=30)
        self.prediction = None
        
    def analyze(self, shoulder_y, hip_y, time):
        self.history.append({
            'shoulder': shoulder_y,
            'hip': hip_y,
            'time': time
        })
        
        if len(self.history) > 10:
            # Predict next move
            recent = list(self.history)[-10:]
            shoulder_values = [h['shoulder'] for h in recent]
            
            if shoulder_values[-1] < shoulder_values[-3] - 0.01:
                return 'jump'
            elif shoulder_values[-1] > shoulder_values[-3] + 0.01:
                return 'duck'
        
        return None

# Main Game Class
class AIPandaRunner:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 500))
        pygame.display.set_caption("🤖 AI-Powered Panda Runner")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
        self.big_font = pygame.font.Font(None, 60)
        
        # AI Components
        self.ai_obstacle = AIObstacleGenerator()
        self.ai_difficulty = AIDifficultyController()
        self.ai_analyzer = AIAnalyzer()
        
        # Game state
        self.score = 0
        self.jumps = 0
        self.deaths = 0
        self.game_over = False
        self.panda_y = 400
        self.panda_jump = False
        self.jump_vel = 0
        
        # Obstacles
        self.obstacles = []
        self.spawn_timer = 0
        
        print("🤖 AI-Powered Panda Runner Started!")
        print("🎯 AI will adapt to your skill level!")
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.panda_jump = True
                    self.jump_vel = -12
                    self.jumps += 1
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
        return True
        
    def update(self):
        if self.game_over:
            return
            
        # Jump physics
        if self.panda_jump:
            self.panda_y += self.jump_vel
            self.jump_vel += 0.8
            if self.panda_y >= 400:
                self.panda_y = 400
                self.panda_jump = False
        
        # AI Difficulty Update
        diff_data = self.ai_difficulty.update(
            self.jumps, self.deaths, len(self.obstacles)
        )
        
        # AI Obstacle Spawning
        self.spawn_timer += 1
        if self.spawn_timer > diff_data['spawn_rate']:
            obstacle = self.ai_obstacle.get_next_obstacle(
                self.score, diff_data['speed']
            )
            self.obstacles.append(obstacle)
            self.spawn_timer = 0
        
        # Update obstacles
        for obs in self.obstacles[:]:
            obs['x'] -= obs['speed']
            if obs['x'] < -50:
                self.obstacles.remove(obs)
                self.score += 10
        
        # Collision detection
        panda_rect = pygame.Rect(100, self.panda_y, 40, 50)
        for obs in self.obstacles:
            obs_rect = pygame.Rect(obs['x'], obs['y'], obs['width'], obs['height'])
            if panda_rect.colliderect(obs_rect):
                self.game_over = True
                self.deaths += 1
        
        # AI Score prediction
        if self.score > 0 and self.score % 50 == 0:
            predicted = self.score * 1.2
            print(f"🤖 AI predicts you'll reach: {int(predicted)}")
        
    def draw(self):
        self.screen.fill((255, 255, 255))
        
        # Ground
        pygame.draw.rect(self.screen, (200, 200, 200), (0, 450, 800, 50))
        
        # Panda
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (100, self.panda_y, 40, 50))
        pygame.draw.circle(self.screen, (50, 50, 50), 
                          (110, self.panda_y - 10), 15)
        pygame.draw.circle(self.screen, (50, 50, 50), 
                          (130, self.panda_y - 10), 15)
        pygame.draw.circle(self.screen, (255, 255, 255), 
                          (115, self.panda_y - 5), 8)
        pygame.draw.circle(self.screen, (255, 255, 255), 
                          (125, self.panda_y - 5), 8)
        pygame.draw.circle(self.screen, (0, 0, 0), 
                          (118, self.panda_y - 5), 4)
        pygame.draw.circle(self.screen, (0, 0, 0), 
                          (128, self.panda_y - 5), 4)
        
        # Obstacles
        for obs in self.obstacles:
            if obs['type'] == 'cactus':
                pygame.draw.rect(self.screen, (34, 139, 34),
                                (obs['x'], obs['y'], obs['width'], obs['height']))
            else:
                pygame.draw.ellipse(self.screen, (255, 140, 0),
                                   (obs['x'], obs['y'], obs['width'], obs['height']))
        
        # Score
        score_text = self.font.render(f"SCORE: {self.score:04d}", True, (0, 0, 0))
        self.screen.blit(score_text, (680, 20))
        
        # AI Difficulty
        diff_text = self.font.render(
            f"🤖 AI Level: {self.ai_difficulty.difficulty:.1f}", 
            True, (0, 100, 200)
        )
        self.screen.blit(diff_text, (10, 10))
        
        # AI Prediction
        if not self.game_over:
            pred = self.ai_analyzer.analyze(
                self.panda_y, 0, pygame.time.get_ticks()
            )
            if pred:
                pred_text = self.font.render(f"🤖 Predicts: {pred}", True, (200, 0, 200))
                self.screen.blit(pred_text, (10, 40))
        
        # Game Over
        if self.game_over:
            overlay = pygame.Surface((800, 500))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            go_text = self.big_font.render("GAME OVER", True, (255, 255, 255))
            self.screen.blit(go_text, (250, 200))
            
            restart_text = self.font.render("Press R to Restart", True, (255, 255, 255))
            self.screen.blit(restart_text, (320, 270))
        
        pygame.display.flip()
        
    def reset_game(self):
        self.game_over = False
        self.score = 0
        self.obstacles = []
        self.panda_y = 400
        self.panda_jump = False
        self.jump_vel = 0
        self.spawn_timer = 0
        self.ai_difficulty.difficulty = 1
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    game = AIPandaRunner()
    game.run()