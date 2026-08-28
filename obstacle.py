import pygame
import random

class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.speed = 8
        self.type = random.choice(['cactus', 'bird'])
        
        # Load images
        self.images = self.load_images()
        self.current_image = None
        
        if self.type == 'bird':
            self.y = 330
            self.height = 30
            
    def load_images(self):
        images = {}
        try:
            for i in range(1, 4):
                img = pygame.image.load(f'assets/obstacles/cactus{i}.png')
                images[f'cactus{i}'] = pygame.transform.scale(img, (30, 40))
            img = pygame.image.load('assets/obstacles/bird1.png')
            images['bird1'] = pygame.transform.scale(img, (40, 30))
            img = pygame.image.load('assets/obstacles/bird2.png')
            images['bird2'] = pygame.transform.scale(img, (40, 30))
        except:
            images = self.create_fallback()
        return images
        
    def create_fallback(self):
        images = {}
        for i in range(1,4):
            s = pygame.Surface((30,40), pygame.SRCALPHA)
            pygame.draw.rect(s, (34,139,34), (5,5,20,35))
            images[f'cactus{i}'] = s
        s = pygame.Surface((40,30), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (255,140,0), (5,5,30,20))
        images['bird1'] = s
        s = pygame.Surface((40,30), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (255,140,0), (5,5,30,20))
        images['bird2'] = s
        return images
        
    def update(self):
        self.x -= self.speed
        # Bird wing flap animation
        if self.type == 'bird':
            if pygame.time.get_ticks() % 500 < 250:
                self.current_image = self.images.get('bird1')
            else:
                self.current_image = self.images.get('bird2')
                
    def draw(self, screen):
        if self.type == 'cactus':
            idx = random.choice([1,2,3])
            img = self.images.get(f'cactus{idx}')
            if img:
                screen.blit(img, (self.x, self.y))
        else:
            if not self.current_image:
                self.current_image = self.images.get('bird1')
            if self.current_image:
                screen.blit(self.current_image, (self.x, self.y))
                
    def get_rect(self):
        if self.type == 'bird':
            return pygame.Rect(self.x, self.y, 40, 30)
        return pygame.Rect(self.x, self.y, 30, 40)