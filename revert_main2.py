with open(r'src\main.py', 'r', encoding='utf8') as f:
    text = f.read()

text = text.replace('self.level.draw(self.virtual_surface, cam_x - 0, cam_y, self)', 'self.level.draw(self.virtual_surface, cam_x, cam_y, self)')
text = text.replace('offset_pos = (sprite.rect.x - cam_x + 0, sprite.rect.y - cam_y)', 'offset_pos = (sprite.rect.x - cam_x, sprite.rect.y - cam_y)')
text = text.replace('outline_rect = pygame.Rect(enemy.rect.x - cam_x + 0 + 4, enemy.rect.y - cam_y - 10, bar_width, bar_height)', 'outline_rect = pygame.Rect(enemy.rect.x - cam_x + 4, enemy.rect.y - cam_y - 10, bar_width, bar_height)')
text = text.replace('fill_rect = pygame.Rect(enemy.rect.x - cam_x + 0 + 4, enemy.rect.y - cam_y - 10, fill, bar_height)', 'fill_rect = pygame.Rect(enemy.rect.x - cam_x + 4, enemy.rect.y - cam_y - 10, fill, bar_height)')
text = text.replace('self.draw_grid(cam_x - 0, cam_y)', 'self.draw_grid(cam_x, cam_y)')
text = text.replace('ft_pos = (ft.rect.x - cam_x + 0, ft.rect.y - cam_y)', 'ft_pos = (ft.rect.x - cam_x, ft.rect.y - cam_y)')

text = text.replace('pygame.draw.line(self.virtual_surface, WHITE, (0, 0), (0, HEIGHT), 2)', '')

with open(r'src\main.py', 'w', encoding='utf8') as f:
    f.write(text)
