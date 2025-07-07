import pygame
import sys

pygame.init()

try:
    # Intenta inicializar el subsistema de video
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pygame Test")
    screen.fill((255, 0, 0)) # Rellena la pantalla de rojo
    pygame.display.flip()

    print("Pygame display initialized successfully!")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        pygame.time.Clock().tick(30)

except pygame.error as e:
    print(f"Error al inicializar Pygame: {e}")
    print("Asegúrate de estar ejecutando en un entorno gráfico o con X11 forwarding.")
finally:
    pygame.quit()
    sys.exit()