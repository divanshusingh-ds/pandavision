import pygame
import os

def create_all_frames():
    """Ek panda image se saare frames generate karo"""
    
    os.makedirs('assets/panda', exist_ok=True)
    os.makedirs('assets/obstacles', exist_ok=True)
    
    print("🎨 Generating all panda frames from single image...")
    print("=" * 50)
    
    # Load original panda image
    try:
        original = pygame.image.load('assets/panda.png')
        original = pygame.transform.scale(original, (60, 65))
        print("✅ Loaded: panda.png")
    except:
        print("❌ panda.png not found! Creating from scratch...")
        original = create_default_panda()
    
    # Duck image load karo
    try:
        duck_img = pygame.image.load('assets/Duck.png')
        duck_img = pygame.transform.scale(duck_img, (70, 40))
        print("✅ Loaded: Duck.png")
    except:
        print("❌ Duck.png not found! Creating from scratch...")
        duck_img = create_default_duck()
    
    # RUNNING FRAMES (4)
    print("\n🏃 Creating Running Frames...")
    run1 = original.copy()
    pygame.image.save(run1, 'assets/panda/run1.png')
    print("  ✅ run1.png")
    run2 = pygame.transform.scale(original, (60, 60))
    pygame.image.save(run2, 'assets/panda/run2.png')
    print("  ✅ run2.png")
    run3 = pygame.transform.flip(original, True, False)
    pygame.image.save(run3, 'assets/panda/run3.png')
    print("  ✅ run3.png")
    run4 = pygame.transform.flip(pygame.transform.scale(original, (60, 60)), True, False)
    pygame.image.save(run4, 'assets/panda/run4.png')
    print("  ✅ run4.png")
    
    # JUMPING FRAMES (2)
    print("\n🦘 Creating Jumping Frames...")
    jump1 = pygame.transform.scale(original, (55, 70))
    pygame.image.save(jump1, 'assets/panda/jump1.png')
    print("  ✅ jump1.png")
    jump2 = pygame.transform.scale(original, (65, 60))
    pygame.image.save(jump2, 'assets/panda/jump2.png')
    print("  ✅ jump2.png")
    
    # DUCK FRAMES (2)
    print("\n🦆 Creating Ducking Frames...")
    duck1 = duck_img.copy()
    pygame.image.save(duck1, 'assets/panda/duck1.png')
    print("  ✅ duck1.png")
    duck2 = pygame.transform.scale(duck_img, (70, 30))
    pygame.image.save(duck2, 'assets/panda/duck2.png')
    print("  ✅ duck2.png")
    
    # DEAD FRAME
    print("\n💀 Creating Dead Frame...")
    dead = original.copy()
    dead = apply_dead_effect(dead)
    pygame.image.save(dead, 'assets/panda/dead.png')
    print("  ✅ dead.png")
    
    # OBSTACLES
    print("\n🌵 Creating Obstacles...")
    create_obstacles()
    
    print("\n" + "=" * 50)
    print("🎉 ALL FRAMES CREATED SUCCESSFULLY!")
    print("📁 Location: assets/panda/")
    print("=" * 50)

def create_default_panda():
    surf = pygame.Surface((60, 65), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (50, 50, 50), (5, 10, 50, 50), border_radius=15)
    pygame.draw.rect(surf, (220, 220, 220), (12, 20, 36, 35), border_radius=10)
    pygame.draw.circle(surf, (50, 50, 50), (12, 10), 10)
    pygame.draw.circle(surf, (50, 50, 50), (48, 10), 10)
    pygame.draw.circle(surf, (255, 255, 255), (18, 22), 7)
    pygame.draw.circle(surf, (255, 255, 255), (42, 22), 7)
    pygame.draw.circle(surf, (0, 0, 0), (20, 22), 4)
    pygame.draw.circle(surf, (0, 0, 0), (44, 22), 4)
    pygame.draw.ellipse(surf, (0, 0, 0), (26, 30, 8, 5))
    pygame.draw.arc(surf, (0, 0, 0), (22, 34, 16, 8), 0, 3.14, 2)
    pygame.draw.ellipse(surf, (50, 50, 50), (8, 55, 14, 10))
    pygame.draw.ellipse(surf, (50, 50, 50), (38, 55, 14, 10))
    return surf

def create_default_duck():
    surf = pygame.Surface((70, 40), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (50, 50, 50), (5, 5, 60, 30), border_radius=15)
    pygame.draw.rect(surf, (220, 220, 220), (12, 10, 46, 20), border_radius=10)
    pygame.draw.circle(surf, (50, 50, 50), (12, 5), 8)
    pygame.draw.circle(surf, (50, 50, 50), (58, 5), 8)
    pygame.draw.circle(surf, (255, 255, 255), (20, 15), 6)
    pygame.draw.circle(surf, (255, 255, 255), (50, 15), 6)
    pygame.draw.circle(surf, (0, 0, 0), (22, 15), 3)
    pygame.draw.circle(surf, (0, 0, 0), (52, 15), 3)
    return surf

def apply_dead_effect(surf):
    dead = surf.copy()
    pygame.draw.line(dead, (0, 0, 0), (15, 22), (25, 32), 2)
    pygame.draw.line(dead, (0, 0, 0), (25, 22), (15, 32), 2)
    pygame.draw.line(dead, (0, 0, 0), (35, 22), (45, 32), 2)
    pygame.draw.line(dead, (0, 0, 0), (45, 22), (35, 32), 2)
    red_overlay = pygame.Surface((60, 65), pygame.SRCALPHA)
    red_overlay.fill((200, 0, 0, 100))
    dead.blit(red_overlay, (0, 0))
    pygame.draw.ellipse(dead, (255, 0, 0), (26, 40, 8, 10))
    return dead

def create_obstacles():
    # Cactus 1
    surf = pygame.Surface((30, 40), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (34, 139, 34), (10, 5, 10, 35), border_radius=5)
    pygame.image.save(surf, 'assets/obstacles/cactus1.png')
    print("  ✅ cactus1.png")
    
    # Cactus 2
    surf = pygame.Surface((35, 45), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (34, 139, 34), (12, 5, 10, 40), border_radius=5)
    pygame.draw.rect(surf, (34, 139, 34), (2, 15, 10, 15), border_radius=3)
    pygame.image.save(surf, 'assets/obstacles/cactus2.png')
    print("  ✅ cactus2.png")
    
    # Cactus 3
    surf = pygame.Surface((40, 50), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (34, 139, 34), (15, 5, 10, 45), border_radius=5)
    pygame.draw.rect(surf, (34, 139, 34), (2, 20, 12, 20), border_radius=3)
    pygame.draw.rect(surf, (34, 139, 34), (26, 25, 12, 15), border_radius=3)
    pygame.image.save(surf, 'assets/obstacles/cactus3.png')
    print("  ✅ cactus3.png")
    
    # Bird 1
    surf = pygame.Surface((40, 30), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.ellipse(surf, (255, 140, 0), (5, 8, 30, 15))
    pygame.draw.polygon(surf, (255, 140, 0), [(5, 12), (15, 0), (25, 12)])
    pygame.draw.polygon(surf, (255, 140, 0), [(15, 12), (25, 0), (35, 12)])
    pygame.draw.circle(surf, (0, 0, 0), (30, 10), 3)
    pygame.draw.polygon(surf, (255, 165, 0), [(35, 12), (40, 15), (35, 18)])
    pygame.image.save(surf, 'assets/obstacles/bird1.png')
    print("  ✅ bird1.png")
    
    # Bird 2
    surf = pygame.Surface((40, 30), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.ellipse(surf, (255, 140, 0), (5, 8, 30, 15))
    pygame.draw.polygon(surf, (255, 140, 0), [(5, 12), (15, 25), (25, 12)])
    pygame.draw.polygon(surf, (255, 140, 0), [(15, 12), (25, 25), (35, 12)])
    pygame.draw.circle(surf, (0, 0, 0), (30, 10), 3)
    pygame.draw.polygon(surf, (255, 165, 0), [(35, 12), (40, 15), (35, 18)])
    pygame.image.save(surf, 'assets/obstacles/bird2.png')
    print("  ✅ bird2.png")
    
    # Rock
    surf = pygame.Surface((35, 25), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.ellipse(surf, (139, 139, 139), (5, 5, 25, 15))
    pygame.draw.ellipse(surf, (169, 169, 169), (8, 5, 20, 12))
    pygame.image.save(surf, 'assets/obstacles/rock.png')
    print("  ✅ rock.png")

if __name__ == "__main__":
    pygame.init()
    create_all_frames()
    pygame.quit()