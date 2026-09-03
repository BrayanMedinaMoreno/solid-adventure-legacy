import pygame
from entities.enemy import Enemy
from settings import *

class Goblin(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "Goblin"
        self.vida = 50
        self.max_vida = 50
        self.fuerza = 14
        self.defensa = 2
        self.xp_recompensa = 20
        
        self.frames = []
        try:
            sheet = pygame.image.load('assets/sprites/goblin.png').convert_alpha()
            frame_w = 32
            frame_h = 32
            
            coords = [(0, 0), (32, 0), (0, 32)]
            for cx, cy in coords:
                frame = sheet.subsurface((cx, cy, frame_w, frame_h))
                frame = pygame.transform.scale(frame, (TILESIZE, TILESIZE))
                self.frames.append(frame)
                
            if self.frames:
                self.image = self.frames[0]
                self.current_frame = 0
                self.last_update = pygame.time.get_ticks()
                self.frame_rate = 200
        except Exception as e:
            print("Error cargando goblin.png:", e)
            pass

    def update(self):
        if hasattr(self, 'frames') and self.frames:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]

class Orco(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "Orco Fuerte"
        self.vida = 100
        self.max_vida = 100
        self.fuerza = 28
        self.defensa = 10
        self.xp_recompensa = 50
        
        # Le cambiamos el color al fallback si no hay imagen propia
        self.image.fill((0,0,0,0)) # Limpiar
        pygame.draw.polygon(self.image, GREEN, [(TILESIZE//2, 4), (TILESIZE-4, TILESIZE-4), (4, TILESIZE-4)])

class Slime(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "Slime Pegajoso"
        self.vida = 40
        self.max_vida = 40
        self.fuerza = 10
        self.defensa = 1
        self.xp_recompensa = 15
        
        # Cargar el sprite animado
        self.frames = []
        try:
            sheet = pygame.image.load('assets/sprites/idle_slime.png').convert_alpha()
            w, h = sheet.get_size()
            # El archivo idle_slime.png es de 72x48. Son 3 columnas de 24px y 2 filas de 24px.
            # Solo tomaremos la primera fila para la animación idle (3 frames de 24x24).
            frame_w = 24
            frame_h = 24
            frames_count = w // frame_w
            
            for i in range(frames_count):
                frame = sheet.subsurface((i * frame_w, 0, frame_w, frame_h))
                frame = pygame.transform.scale(frame, (TILESIZE, TILESIZE))
                self.frames.append(frame)
            
            if self.frames:
                self.image = self.frames[0]
                self.current_frame = 0
                self.last_update = pygame.time.get_ticks()
                self.frame_rate = 200 # ms por frame
        except Exception as e:
            print("Error cargando idle_slime:", e)
            pass

    def update(self):
        if hasattr(self, 'frames') and self.frames:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]

class SlimeMutante(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "Slime Mutante"
        self.vida = 60
        self.max_vida = 60
        self.fuerza = 15
        self.defensa = 2
        self.xp_recompensa = 30
        
        self.frames = []
        try:
            sheet = pygame.image.load('assets/sprites/idle_slime_2.png').convert_alpha()
            w, h = sheet.get_size()
            frame_w = 24
            frame_h = 24
            frames_count = w // frame_w
            
            for i in range(frames_count):
                frame = sheet.subsurface((i * frame_w, 0, frame_w, frame_h))
                frame = pygame.transform.scale(frame, (TILESIZE, TILESIZE))
                self.frames.append(frame)
            
            if self.frames:
                self.image = self.frames[0]
                self.current_frame = 0
                self.last_update = pygame.time.get_ticks()
                self.frame_rate = 200
        except Exception as e:
            print("Error cargando idle_slime_2:", e)
            pass

    def update(self):
        if hasattr(self, 'frames') and self.frames:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]

class SlimeRosa(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "Slime Rosa Especial"
        self.vida = 100
        self.max_vida = 100
        self.fuerza = 22
        self.defensa = 4
        self.xp_recompensa = 75
        
        self.frames = []
        try:
            import os
            path = 'assets/sprites/idle_slime_3.png'
            if not os.path.exists(path):
                path = 'assets/sprites/idle_slime_rosa'
            sheet = pygame.image.load(path).convert_alpha()
            w, h = sheet.get_size()
            frame_w = 24
            frame_h = 24
            frames_count = w // frame_w
            
            for i in range(frames_count):
                frame = sheet.subsurface((i * frame_w, 0, frame_w, frame_h))
                frame = pygame.transform.scale(frame, (TILESIZE, TILESIZE))
                self.frames.append(frame)
            
            if self.frames:
                self.image = self.frames[0]
                self.current_frame = 0
                self.last_update = pygame.time.get_ticks()
                self.frame_rate = 180
        except Exception as e:
            print("Error cargando slime rosa:", e)
            pass

    def update(self):
        if hasattr(self, 'frames') and self.frames:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]

class SlimeArcano(Enemy):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "Slime Arcano"
        self.vida = 85
        self.max_vida = 85
        self.fuerza = 18
        self.defensa = 3
        self.xp_recompensa = 45
        
        self.frames = []
        try:
            sheet = pygame.image.load('assets/sprites/idle_slime_4.png').convert_alpha()
            w, h = sheet.get_size()
            frame_w = 24
            frame_h = 24
            frames_count = w // frame_w
            
            for i in range(frames_count):
                frame = sheet.subsurface((i * frame_w, 0, frame_w, frame_h))
                frame = pygame.transform.scale(frame, (TILESIZE, TILESIZE))
                self.frames.append(frame)
            
            if self.frames:
                self.image = self.frames[0]
                self.current_frame = 0
                self.last_update = pygame.time.get_ticks()
                self.frame_rate = 200
        except Exception as e:
            print("Error cargando idle_slime_4.png:", e)
            pass

    def update(self):
        if hasattr(self, 'frames') and self.frames:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]

class SlimeBoss(SlimeRosa):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.name = "REY SLIME ROSA (BOSS)"
        self.max_vida = 300
        self.vida = 300
        self.fuerza = 35
        self.defensa = 5
        self.xp_recompensa = 500
        self.titulo = "Soberano de la Viscosidad"
        self.last_stand_used = False
        # Escalar visualmente para que se vea como un jefe
        if hasattr(self, 'frames') and self.frames:
            new_frames = []
            for frame in self.frames:
                new_frame = pygame.transform.scale(frame, (int(TILESIZE*1.5), int(TILESIZE*1.5)))
                new_frames.append(new_frame)
            self.frames = new_frames
            self.image = self.frames[0]
        else:
            self.image = pygame.transform.scale(self.image, (int(TILESIZE*1.5), int(TILESIZE*1.5)))
            
        self.rect = self.image.get_rect(center=self.rect.center)
