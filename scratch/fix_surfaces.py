
import sys

with open('src/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # Skip lines where self.screen should remain (init, flip, set_mode)
    line_num = i + 1
    if "pygame.display.set_mode" in line or "self.screen.get_size()" in line or "self.screen.fill" in line or "self.screen.blit" in line and "scaled_surf" in line or "pygame.display.flip()" in line:
        new_lines.append(line)
        continue
    
    # Replace in drawing lines
    if "self.screen" in line:
        line = line.replace("self.screen", "self.virtual_surface")
    new_lines.append(line)

with open('src/main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
