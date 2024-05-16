import pygame
import pygame_gui
import os
import random
import cv2

# Definir constantes
WHITE = (255, 255, 255)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30

class Avatar(pygame.sprite.Sprite):
    def __init__(self, animations, name):
        super().__init__()
        self.animations = animations
        self.name = name
        self.current_animation = 'return'
        self.current_direction = 'derecha'  # Asumiendo que inicialmente se mueve a la derecha
        self.image_index = 0
        self.image = self.animations[self.current_animation][self.current_direction][self.image_index]
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = SCREEN_HEIGHT - 100
        self.speed = random.choice([-5, 5])
        self.move_frames = 300  # 10 seconds at 30 FPS
        self.pause_frames = 150  # 5 seconds at 30 FPS
        self.counter = self.move_frames
        self.font = pygame.font.Font(None, 36)
        self.selected = False
        self.update_direction()

    def update_direction(self):
        if self.speed > 0:
            self.current_direction = 'derecha'
        else:
            self.current_direction = 'izquierda'

    def update(self):
        self.counter -= 1
        if self.counter <= 0:
            if self.current_animation == 'return':
                self.current_animation = 'paused'
                self.counter = self.pause_frames
                self.speed = 0  # Stop moving
            else:
                self.current_animation = 'return'
                self.counter = self.move_frames
                self.speed = random.choice([-5, 5])  # Resume moving
                self.update_direction()

        # Update image
        self.image_index = (self.image_index + 1) % len(self.animations[self.current_animation][self.current_direction])
        self.image = self.animations[self.current_animation][self.current_direction][self.image_index]
        
        # Move avatar
        if self.speed != 0:
            old_x = self.rect.x
            self.rect.x += self.speed
            if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
                self.speed = -self.speed
                self.update_direction()
            elif old_x == self.rect.x:
                self.update_direction()

    def draw(self, surface):
        if self.selected:
            pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)
        surface.blit(self.image, self.rect)
        text_surf = self.font.render(self.name, True, WHITE)
        text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.top - 20))
        surface.blit(text_surf, text_rect)

def load_sprites(folder):
    sprites = {}
    for root, dirs, files in os.walk(folder, topdown=False):
        for name in dirs:
            path = os.path.join(root, name)
            if 'return' in path or 'paused' in path:
                key = os.path.basename(os.path.dirname(os.path.dirname(path)))
                if key not in sprites:
                    sprites[key] = {'return': {'derecha': [], 'izquierda': []}, 'paused': {'derecha': [], 'izquierda': []}}
                animation_type = os.path.basename(os.path.dirname(path))
                direction = os.path.basename(path)
                for file in os.listdir(path):
                    if file.endswith('.png'):
                        img_path = os.path.join(path, file)
                        img_cv = cv2.imread(img_path)
                        img_pygame = pygame.image.frombuffer(img_cv.tobytes(), img_cv.shape[1::-1], "BGR")
                        sprites[key][animation_type][direction].append(img_pygame)
    return sprites

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
clock = pygame.time.Clock()
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# Load sprites
sprite_animations = load_sprites('sprites')
all_sprites = pygame.sprite.Group()

# UI Components
name_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((50, 50), (200, 50)), manager=manager)
add_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((260, 50), (100, 50)), text='Add', manager=manager)
remove_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((370, 50), (100,50)), text='Remove', manager=manager)
close_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((480, 50), (100, 50)), text='Close', manager=manager)

# Main loop
running = True
selected_sprite = None

while running:
    time_delta = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check if clicked on a sprite
                for sprite in all_sprites:
                    if sprite.rect.collidepoint(event.pos):
                        if selected_sprite:
                            selected_sprite.selected = False
                        selected_sprite = sprite
                        selected_sprite.selected = True
                        break

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == add_button:
                    name = name_entry.get_text()
                    avatar_choice = random.choice(list(sprite_animations.keys()))
                    new_avatar = Avatar(sprite_animations[avatar_choice], name)
                    all_sprites.add(new_avatar)
                    name_entry.set_text('')
                
                elif event.ui_element == remove_button and selected_sprite:
                    selected_sprite.kill()
                    selected_sprite = None
                
                elif event.ui_element == close_button:
                    running = False

        manager.process_events(event)

    manager.update(time_delta)

    screen.fill((0, 0, 0, 0))  # Clear screen with transparent background
    for sprite in all_sprites:
        sprite.update()
        sprite.draw(screen)
    
    manager.draw_ui(screen)

    pygame.display.flip()


pygame.quit()





