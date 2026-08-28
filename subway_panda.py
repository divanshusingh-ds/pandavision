import pygame
import random
import sys
import cv2
import mediapipe as mp
import threading

# ==========================================
# WEBCAM CONTROL CLASS (Built-in)
# ==========================================
class WebcamControl:
    def __init__(self):
        print("📷 Step 1: Opening webcam...")
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("❌ Webcam not found!")
            raise Exception("Webcam not found")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("✅ Step 2: Webcam opened!")
        
        print("📷 Step 3: Initializing MediaPipe...")
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        print("✅ Step 4: MediaPipe initialized!")
        
        self.jump = False
        self.duck = False
        self.move_left = False
        self.move_right = False
        self.running = True
        
        self.prev_shoulder_y = None
        self.prev_hip_x = None
        self.cooldown = 0
        self.COOLDOWN_FRAMES = 5
        
        self.JUMP_THRESHOLD = 0.015
        self.DUCK_THRESHOLD = 0.015
        self.LANE_THRESHOLD = 0.05
        
        self.thread = threading.Thread(target=self.run)
        self.lock = threading.Lock()
        self.started = False
        print("✅ Step 5: WebcamControl ready!")
        
    def start(self):
        if not self.started:
            self.started = True
            self.thread.start()
            print("🎥 Step 6: Thread started!")
        
    def run(self):
        print("📷 Step 7: Webcam thread running...")
        frame_count = 0
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("⚠️ Failed to capture frame")
                continue
            
            frame_count += 1
            if frame_count % 30 == 0:
                print(f"📷 Captured {frame_count} frames")
                
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                left_shoulder = landmarks[11]
                right_shoulder = landmarks[12]
                shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
                
                if self.prev_shoulder_y is not None and self.cooldown == 0:
                    delta_y = self.prev_shoulder_y - shoulder_y
                    
                    if delta_y > self.JUMP_THRESHOLD:
                        with self.lock:
                            self.jump = True
                        self.cooldown = self.COOLDOWN_FRAMES
                        print("🦘 JUMP!")
                    
                    if shoulder_y - self.prev_shoulder_y > self.DUCK_THRESHOLD:
                        with self.lock:
                            self.duck = True
                        self.cooldown = self.COOLDOWN_FRAMES
                        print("🦆 DUCK!")
                
                self.prev_shoulder_y = shoulder_y
                
                left_hip = landmarks[23]
                right_hip = landmarks[24]
                hip_x = (left_hip.x + right_hip.x) / 2
                
                if self.prev_hip_x is not None and self.cooldown == 0:
                    delta_x = hip_x - self.prev_hip_x
                    
                    if delta_x > self.LANE_THRESHOLD:
                        with self.lock:
                            self.move_right = True
                        self.cooldown = self.COOLDOWN_FRAMES
                        print("➡️ RIGHT!")
                    
                    elif delta_x < -self.LANE_THRESHOLD:
                        with self.lock:
                            self.move_left = True
                        self.cooldown = self.COOLDOWN_FRAMES
                        print("⬅️ LEFT!")
                
                self.prev_hip_x = hip_x
                
                self.mp_draw.draw_landmarks(
                    frame, 
                    results.pose_landmarks, 
                    self.mp_pose.POSE_CONNECTIONS
                )
                
                cv2.putText(frame, "🟢 BODY DETECTED!", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Shoulder Y: {shoulder_y:.3f}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                cv2.putText(frame, f"Hip X: {hip_x:.3f}", (10, 85),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            else:
                cv2.putText(frame, "🔴 NO BODY DETECTED!", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, "Stand in front of camera", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            cv2.imshow('Body Tracking - Subway Panda', frame)
            
            if self.cooldown > 0:
                self.cooldown -= 1
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()
                break
                
        self.cap.release()
        cv2.destroyAllWindows()
        
    def get_jump(self):
        with self.lock:
            if self.jump:
                self.jump = False
                return True
            return False
            
    def get_duck(self):
        with self.lock:
            if self.duck:
                self.duck = False
                return True
            return False
            
    def get_move_left(self):
        with self.lock:
            if self.move_left:
                self.move_left = False
                return True
            return False
            
    def get_move_right(self):
        with self.lock:
            if self.move_right:
                self.move_right = False
                return True
            return False
            
    def stop(self):
        self.running = False
        print("👋 Webcam Controller Stopped!")

# ==========================================
# GAME CONSTANTS
# ==========================================
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GROUND_Y = 500
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
LANES = [200, 400, 600]

# ==========================================
# PANDA CLASS
# ==========================================
class Panda:
    def __init__(self):
        self.x = 400
        self.y = GROUND_Y - 60
        self.width = 50
        self.height = 60
        self.lane = 1
        self.is_jumping = False
        self.is_ducking = False
        self.is_dead = False
        self.jump_vel = 0
        self.gravity = 0.8
        self.jump_power = -15
        self.target_x = self.x
        self.move_speed = 12
        
    def change_lane(self, direction):
        new_lane = self.lane + direction
        if 0 <= new_lane <= 2:
            self.lane = new_lane
            self.target_x = LANES[self.lane]
            
    def jump(self):
        if not self.is_jumping and not self.is_ducking and not self.is_dead:
            self.is_jumping = True
            self.jump_vel = self.jump_power
    
    def duck(self):
        if not self.is_jumping and not self.is_dead:
            self.is_ducking = True
            self.height = 35
    
    def update(self):
        if abs(self.x - self.target_x) > 2:
            if self.x < self.target_x:
                self.x += self.move_speed
            else:
                self.x -= self.move_speed
        else:
            self.x = self.target_x
        
        if self.is_jumping:
            self.y += self.jump_vel
            self.jump_vel += self.gravity
            if self.y >= GROUND_Y - 60:
                self.y = GROUND_Y - 60
                self.is_jumping = False
        
        if not self.is_ducking and not self.is_jumping:
            self.height = 60
    
    def draw(self, screen):
        color = (200, 0, 0) if self.is_dead else (50, 50, 50)
        
        if self.is_ducking:
            pygame.draw.rect(screen, color, (self.x, self.y + 25, 70, 35), border_radius=15)
            pygame.draw.rect(screen, (200, 200, 200), (self.x + 10, self.y + 30, 50, 20), border_radius=10)
            pygame.draw.circle(screen, WHITE, (self.x + 20, self.y + 38), 6)
            pygame.draw.circle(screen, WHITE, (self.x + 50, self.y + 38), 6)
            pygame.draw.circle(screen, BLACK, (self.x + 22, self.y + 38), 3)
            pygame.draw.circle(screen, BLACK, (self.x + 52, self.y + 38), 3)
            return
        
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), border_radius=20)
        pygame.draw.rect(screen, (200, 200, 200), (self.x + 8, self.y + 15, self.width - 16, self.height - 25), border_radius=10)
        pygame.draw.circle(screen, color, (self.x + 10, self.y + 5), 10)
        pygame.draw.circle(screen, color, (self.x + 40, self.y + 5), 10)
        
        if self.is_dead:
            for x_off in [15, 35]:
                pygame.draw.line(screen, BLACK, (self.x + x_off, self.y + 15), (self.x + x_off + 10, self.y + 25), 2)
                pygame.draw.line(screen, BLACK, (self.x + x_off + 10, self.y + 15), (self.x + x_off, self.y + 25), 2)
        else:
            pygame.draw.circle(screen, WHITE, (self.x + 15, self.y + 20), 8)
            pygame.draw.circle(screen, WHITE, (self.x + 35, self.y + 20), 8)
            pygame.draw.circle(screen, BLACK, (self.x + 17, self.y + 20), 4)
            pygame.draw.circle(screen, BLACK, (self.x + 37, self.y + 20), 4)
        
        pygame.draw.ellipse(screen, BLACK, (self.x + 22, self.y + 30, 6, 4))
        if not self.is_dead:
            pygame.draw.arc(screen, BLACK, (self.x + 18, self.y + 34, 14, 8), 0, 3.14, 2)
    
    def get_rect(self):
        if self.is_ducking:
            return pygame.Rect(self.x, self.y + 25, 70, 35)
        return pygame.Rect(self.x, self.y, self.width, self.height)

# ==========================================
# OBSTACLE CLASS
# ==========================================
class Obstacle:
    def __init__(self, lane):
        self.x = SCREEN_WIDTH + 50
        self.lane = lane
        self.x_pos = LANES[lane]
        self.width = 50
        self.height = 60
        self.speed = 8
        self.type = random.choice(['train', 'barrier'])
        self.color = (180, 50, 50) if self.type == 'train' else (200, 200, 50)
        if self.type == 'train':
            self.height = 80
    
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        if self.type == 'train':
            pygame.draw.rect(screen, self.color, (self.x, self.x_pos - 20, self.width, self.height))
            pygame.draw.rect(screen, (100, 100, 100), (self.x, self.x_pos - 20, self.width, 10))
            for i in range(3):
                pygame.draw.rect(screen, (255, 255, 200), (self.x + 5 + i*15, self.x_pos, 10, 15))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.x_pos - 30, self.width, 20))
            pygame.draw.rect(screen, (150, 150, 0), (self.x + 10, self.x_pos - 40, 10, 30))
            pygame.draw.rect(screen, (150, 150, 0), (self.x + 30, self.x_pos - 40, 10, 30))
    
    def get_rect(self):
        if self.type == 'train':
            return pygame.Rect(self.x, self.x_pos - 20, self.width, self.height)
        return pygame.Rect(self.x, self.x_pos - 40, self.width, 40)

# ==========================================
# COIN CLASS
# ==========================================
class Coin:
    def __init__(self, lane):
        self.x = SCREEN_WIDTH + 50
        self.lane = lane
        self.x_pos = LANES[lane]
        self.size = 20
        self.speed = 7
    
    def update(self):
        self.x -= self.speed
    
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (self.x, self.x_pos), self.size)
        pygame.draw.circle(screen, (200, 200, 0), (self.x, self.x_pos), self.size - 4)
        pygame.draw.circle(screen, YELLOW, (self.x - 4, self.x_pos - 4), 5)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.x_pos - self.size, self.size * 2, self.size * 2)

# ==========================================
# GAME CLASS
# ==========================================
class Game:
    def __init__(self):
        print("🎮 Step 1: Initializing game...")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🐼 Subway Panda - Body Control")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 60)
        print("✅ Step 2: Pygame initialized!")
        
        self.score = 0
        self.coins = 0
        self.game_over = False
        self.frame_count = 0
        
        self.panda = Panda()
        self.obstacles = []
        self.coins_list = []
        self.spawn_timer = 0
        self.bg_scroll = 0
        self.lane_cooldown = 0
        
        # ==========================================
        # WEBCAM - FINAL TRY!
        # ==========================================
        print("🎥 Step 3: Starting webcam...")
        try:
            self.webcam = WebcamControl()
            self.webcam.start()
            self.use_webcam = True
            print("✅ Step 4: Webcam initialized successfully!")
        except Exception as e:
            print(f"❌ Step 4: Webcam failed: {e}")
            self.webcam = None
            self.use_webcam = False
        
        print("\n" + "="*50)
        print("🐼 SUBWAY PANDA - BODY CONTROL")
        print("="*50)
        print(f"🎥 Webcam Status: {'ACTIVE ✅' if self.use_webcam else 'INACTIVE ❌'}")
        print("🎮 Body Movements:")
        print("   ⬅️ Lean LEFT  → Move Left")
        print("   ➡️ Lean RIGHT → Move Right")
        print("   ⬆️ Body UP   → Jump")
        print("   ⬇️ Body DOWN → Duck")
        print("   ⌨️  R = Restart | Q = Quit")
        print("="*50 + "\n")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()
                if event.key == pygame.K_q:
                    return False
        return True
    
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
                if self.frame_count % 15 == 0:
                    self.panda.is_ducking = False
                    self.panda.height = 60
            if self.lane_cooldown == 0:
                if self.webcam.get_move_left():
                    self.panda.change_lane(-1)
                    self.lane_cooldown = 5
                elif self.webcam.get_move_right():
                    self.panda.change_lane(1)
                    self.lane_cooldown = 5
        
        if self.lane_cooldown > 0:
            self.lane_cooldown -= 1
        
        self.panda.update()
        
        self.spawn_timer += 1
        if self.spawn_timer > random.randint(60, 120):
            self.obstacles.append(Obstacle(random.randint(0, 2)))
            self.spawn_timer = 0
            if random.random() < 0.3:
                self.coins_list.append(Coin(random.randint(0, 2)))
        
        for obs in self.obstacles[:]:
            obs.update()
            if obs.x < -100:
                self.obstacles.remove(obs)
        
        for coin in self.coins_list[:]:
            coin.update()
            if coin.x < -100:
                self.coins_list.remove(coin)
        
        panda_rect = self.panda.get_rect()
        for obs in self.obstacles:
            if panda_rect.colliderect(obs.get_rect()):
                self.game_over = True
                self.panda.is_dead = True
                break
        
        for coin in self.coins_list[:]:
            if panda_rect.colliderect(coin.get_rect()):
                self.coins_list.remove(coin)
                self.coins += 1
                self.score += 5
        
        self.score += 0.2
        self.bg_scroll -= 2
        if self.bg_scroll < -800:
            self.bg_scroll = 0
    
    def draw(self):
        self.screen.fill((50, 150, 200))
        
        for i in range(3):
            x = (i * 300 + self.bg_scroll * 0.3) % 900 - 100
            pygame.draw.ellipse(self.screen, (255, 255, 255), (x, 50 + i*40, 100, 40))
            pygame.draw.ellipse(self.screen, (255, 255, 255), (x + 30, 40 + i*40, 80, 50))
        
        for i in range(5):
            x = i * 200 + self.bg_scroll * 0.5
            x = x % 1000 - 100
            height = 100 + ((i * 50) % 150)
            pygame.draw.rect(self.screen, (100, 100, 120), (x, GROUND_Y - height, 80, height))
            for wy in range(height - 20, 10, -30):
                for wx in range(10, 70, 25):
                    pygame.draw.rect(self.screen, (200, 200, 50), (x + wx, GROUND_Y - wy, 12, 15))
        
        pygame.draw.rect(self.screen, (50, 50, 50), (0, GROUND_Y, SCREEN_WIDTH, 100))
        
        for i in range(0, SCREEN_WIDTH + 40, 40):
            x = (i + self.bg_scroll) % (SCREEN_WIDTH + 40)
            pygame.draw.rect(self.screen, WHITE, (x, GROUND_Y, 20, 5))
        
        for lane_x in [300, 500]:
            for y in range(GROUND_Y, SCREEN_HEIGHT, 30):
                pygame.draw.rect(self.screen, (200, 200, 200), (lane_x - 2, y, 4, 15))
        
        for i, lane_x in enumerate(LANES):
            color = GREEN if i == self.panda.lane else (100, 100, 100)
            pygame.draw.rect(self.screen, color, (lane_x - 50, GROUND_Y + 20, 100, 5))
        
        for coin in self.coins_list:
            coin.draw(self.screen)
        for obs in self.obstacles:
            obs.draw(self.screen)
        self.panda.draw(self.screen)
        
        score_text = self.font.render(f"SCORE: {int(self.score):04d}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 200, 20))
        
        coin_text = self.font.render(f"🪙 {self.coins}", True, YELLOW)
        self.screen.blit(coin_text, (SCREEN_WIDTH - 200, 60))
        
        status = "ACTIVE" if (self.use_webcam and self.webcam) else "INACTIVE"
        color = GREEN if (self.use_webcam and self.webcam) else RED
        status_text = self.font.render(f"🎥 {status}", True, color)
        self.screen.blit(status_text, (10, 10))
        
        lane_names = ["⬅️ LEFT", "⏺ CENTER", "RIGHT ➡️"]
        lane_text = self.font.render(lane_names[self.panda.lane], True, WHITE)
        self.screen.blit(lane_text, (10, 60))
        
        hint = self.small_font.render("⬅️➡️ Lean | ⬆️ Jump | ⬇️ Duck", True, WHITE)
        self.screen.blit(hint, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT - 30))
        
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            go_text = self.big_font.render("GAME OVER", True, RED)
            self.screen.blit(go_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100))
            
            score_text = self.font.render(f"Score: {int(self.score)}", True, WHITE)
            self.screen.blit(score_text, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2 - 30))
            
            coin_text = self.font.render(f"Coins: {self.coins}", True, YELLOW)
            self.screen.blit(coin_text, (SCREEN_WIDTH//2 - 40, SCREEN_HEIGHT//2 + 10))
            
            restart_text = self.font.render("Press R to Restart", True, WHITE)
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 + 60))
        
        pygame.display.flip()
    
    def reset_game(self):
        self.game_over = False
        self.score = 0
        self.coins = 0
        self.obstacles = []
        self.coins_list = []
        self.panda = Panda()
        self.spawn_timer = 0
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        if self.webcam:
            self.webcam.stop()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()