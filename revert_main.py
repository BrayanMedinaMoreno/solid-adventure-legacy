with open(r'src\main.py', 'r', encoding='utf8') as f:
    text = f.read()

# Revert LEFT_PANEL_WIDTH offset
text = text.replace('LEFT_PANEL_WIDTH', '0')

# Except where we define it, let's remove that definition entirely.
import re
text = re.sub(r'        from settings import UI_WIDTH\n        LEFT_PANEL_WIDTH = UI_WIDTH\n        self.virtual_surface.set_clip\(pygame.Rect\(0, 0, MAP_WIDTH, HEIGHT\)\)', '        self.virtual_surface.set_clip(pygame.Rect(0, 0, MAP_WIDTH, HEIGHT))', text)

with open(r'src\main.py', 'w', encoding='utf8') as f:
    f.write(text)
