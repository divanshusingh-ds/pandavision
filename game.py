import pygame
import sys
import random
from panda import Panda
from obstacle import Obstacle
from webcam_control import WebcamControl

# Initialize
pygame.init()
pygame.display.set_caption("🐼 Panda Runner - Webcam Control")

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
GROUND_Y = 460
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.running = True
        self.game_over = False
        self.score = 0
        self.high_score = 2840
        self.frame_count = 0
        
        # Day/Night
        self.is_night = False
        self.day_cycle = 0
        
        # Game objects
        self.panda = Panda(100, GROUND_Y - 60)
        self.obstacles = []
        self.obstacle_timer = 0
        
        # Webcam control
        try:
            self.webcam = WebcamControl()
            self.webcam.start()
            self.use_webcam = True
            print("✅ Webcam initialized successfully!")
        except Exception as e:
            print(f"⚠️ Webcam failed: {e}")
            self.webcam = None
            self.use_webcam = False
        
        print("🐼 Panda Runner Started!")
        print("Controls: SPACE=Jump, DOWN=Duck, R=Restart, C=Toggle Webcam")
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.panda.jump()
                elif event.key == pygame.K_DOWN and not self.game_over:
                    self.panda.duck()
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_c and self.webcam:
                    self.use_webcam = not self.use_webcam
                    print(f"Webcam: {'ON' if self.use_webcam else 'OFF'}")
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.panda.is_ducking = False
                    self.panda.height = self.panda.original_height
                    
    def update(self):
        if self.game_over:
            return
            
        self.frame_count += 1
        
        # Webcam controls
        if self.use_webcam and self.webcam:
            if self.webcam.get_jump():
                self.panda.jump()
            if self.webcam.get_duck():
                self.panda.duck()
                
        self.panda.update()
        
        # Spawn obstacles
        self.obstacle_timer += 1
        if self.obstacle_timer > random.randint(60, 150):
            self.obstacles.append(Obstacle(SCREEN_WIDTH, GROUND_Y - 40))
            self.obstacle_timer = 0
            
        # Update obstacles
        for obs in self.obstacles[:]:
            obs.update()
            if obs.x < -50:
                self.obstacles.remove(obs)
                self.score += 10
                
        # Collision
        panda_rect = pygame.Rect(self.panda.x, self.panda.y, 
                                self.panda.width, self.panda.height)
        for obs in self.obstacles:
            if panda_rect.colliderect(obs.get_rect()):
                self.game_over = True
                self.panda.is_dead = True
                
        if self.score > self.high_score:
            self.high_score = self.score
            
        # Day/Night
        self.day_cycle += 1
        if self.day_cycle > 200:
            self.day_cycle = 0
            self.is_night = not self.is_night
            
    def draw(self):
        # Background
        if self.is_night:
            self.screen.fill(DARK_GRAY)
            if self.frame_count % 2 == 0:
                for _ in range(50):
                    x = random.randint(0, SCREEN_WIDTH)
                    y = random.randint(0, GROUND_Y)
                    pygame.draw.circle(self.screen, WHITE, (x, y), 1)
        else:
            self.screen.fill(WHITE)
            
        # Ground
        pygame.draw.rect(self.screen, GRAY if self.is_night else (200,200,200),
                        (0, GROUND_Y, SCREEN_WIDTH, 40))
        
        # Ground line
        color = WHITE if self.is_night else BLACK
        for i in range(0, SCREEN_WIDTH, 40):
            offset = (self.frame_count * 2) % 40
            pygame.draw.rect(self.screen, color, (i - offset, GROUND_Y, 20, 2))
        
        # Draw objects
        self.panda.draw(self.screen)
        for obs in self.obstacles:
            obs.draw(self.screen)
            
        # Score
        color = WHITE if self.is_night else BLACK
        score_text = self.font.render(f"SCORE: {self.score:04d}", True, color)
        self.screen.blit(score_text, (SCREEN_WIDTH - 200, 30))
        
        high_text = self.small_font.render(f"HI-SCORE: {self.high_score:04d}", True, color)
        self.screen.blit(high_text, (SCREEN_WIDTH - 200, 70))
        
        # Status
        status = "ACTIVE" if (self.use_webcam and self.webcam) else "INACTIVE"
        status_color = (0,255,0) if (self.use_webcam and self.webcam) else (255,0,0)
        status_text = self.small_font.render(f"Webcam {status}", True, status_color)
        self.screen.blit(status_text, (10, 10))
        
        # Game Over
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            go_text = self.font.render("GAME OVER", True, WHITE)
            self.screen.blit(go_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
            restart_text = self.small_font.render("Press R to Restart", True, WHITE)
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 + 10))
            
    def reset_game(self):
        self.game_over = False
        self.score = 0
        self.obstacles = []
        self.panda = Panda(100, GROUND_Y - 60)
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
            
        if self.webcam:
            self.webcam.stop()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()