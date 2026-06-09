
import sys

with open('src/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_flip_method = False

for i, line in enumerate(lines):
    if "def flip_to_screen(self):" in line:
        in_flip_method = True
        new_lines.append(line)
        continue
    
    if in_flip_method and line.strip() == "": # End of method (roughly)
        # We assume the next def or end of file ends the flip method
        pass
    
    if in_flip_method and i > 0 and lines[i-1].strip().startswith("pygame.display.flip()"):
        in_flip_method = False

    # Skip lines where self.screen should remain
    if "pygame.display.set_mode" in line or in_flip_method:
        new_lines.append(line)
        continue
    
    # Replace in all other lines
    if "self.screen" in line:
        line = line.replace("self.screen", "self.virtual_surface")
    new_lines.append(line)

with open('src/main.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
