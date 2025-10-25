import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import nbtlib
import os

class SchematicViewer:
    def __init__(self, schem_path, texture_path="C:/Users/ryant/Documents/Coding Projects/mc-command-block-modifier-master/src/resource_pack/textures/block"):
        self.schem_path = schem_path
        self.texture_path = texture_path
        self.WIDTH, self.HEIGHT = 800, 600
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Schematic 3D Viewer")
        self.clock = pygame.time.Clock()
        self.FPS = 60

        # Colors (fallback if textures are missing)
        self.WHITE = (1.0, 1.0, 1.0, 1.0)
        self.GRAY = (0.5, 0.5, 0.5, 1.0)
        self.RED = (1.0, 0.0, 0.0, 1.0)
        self.BLUE = (0.0, 0.0, 1.0, 1.0)
        self.GREEN = (0.0, 1.0, 0.0, 1.0)
        self.ORANGE = (1.0, 0.65, 0.0, 1.0)
        self.LIGHT_GRAY = (0.7, 0.7, 0.7, 0.4)
        self.DARK_GRAY = (0.4, 0.4, 0.4, 0.4)

        # Block color mapping (fallback)
        self.block_colors = {
            "minecraft:command_block": self.ORANGE,
            "minecraft:stone": self.GRAY,
            "default": self.GRAY
        }

        # Texture mapping
        self.textures = {}
        self.load_textures()

        # Render region
        self.RENDER_WIDTH = 600
        self.RENDER_HEIGHT = 400
        self.RENDER_X = (self.WIDTH - self.RENDER_WIDTH) // 2
        self.RENDER_Y = (self.HEIGHT - self.RENDER_HEIGHT) // 2

        # Camera settings
        self.camera_distance = 15.0
        self.camera_yaw = 45.0
        self.camera_pitch = 20.0
        self.fov = 60.0
        self.near = 0.1
        self.far = 1000.0
        self.camera_x, self.camera_y, self.camera_z = 0.0, 0.0, 0.0

        # Lighting settings
        self.light_dir = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.ambient = 0.3

        # Load blocks
        self.blocks = self.parse_schematic(schem_path)
        print(f"Loaded {len(self.blocks)} blocks")
        self.selected_block = None

        # Mouse interaction
        self.dragging_left = False
        self.dragging_middle = False
        self.last_mouse_pos = (0, 0)

        self.init_opengl()
        self.center_camera()

    def load_textures(self):
        """Load textures from the resource pack folder."""
        glEnable(GL_TEXTURE_2D)
        for block_name in self.block_colors:
            texture_name = block_name.split(":")[-1] + ".png"  # e.g., command_block.png
            texture_path = os.path.join(self.texture_path, texture_name)
            if os.path.exists(texture_path):
                try:
                    image = pygame.image.load(texture_path)
                    image = pygame.transform.flip(image, False, True)  # Flip for OpenGL
                    image_data = pygame.image.tostring(image, "RGBA", 1)
                    width, height = image.get_size()
                    texture_id = glGenTextures(1)
                    glBindTexture(GL_TEXTURE_2D, texture_id)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
                    self.textures[block_name] = texture_id
                    print(f"Loaded texture for {block_name}: {texture_path}")
                except Exception as e:
                    print(f"Failed to load texture {texture_path}: {e}")
            else:
                print(f"Texture not found for {block_name}: {texture_path} (using fallback color)")

    def init_opengl(self):
        """Initialize OpenGL settings."""
        if not glGetString(GL_VERSION):
            print("OpenGL context not initialized. Check GPU drivers.")
            pygame.quit()
            return
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.2, 0.2, 0.2, 1.0)  # Dark gray background
        glViewport(self.RENDER_X, self.RENDER_Y, self.RENDER_WIDTH, self.RENDER_HEIGHT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, self.RENDER_WIDTH / self.RENDER_HEIGHT, self.near, self.far)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def parse_schematic(self, path):
        """Parse a .schem file to extract block positions and types."""
        blocks = []
        try:
            # Attempt to load with nbtlib.load, specifying gzipped=True
            schematic = nbtlib.load(path, gzipped=True)
            data = schematic.root
            width, height, length = data['Width'], data['Height'], data['Length']
            palette = data['Palette']
            block_data = data['BlockData']
            offset = data.get('Offset', [0, 0, 0])
            ox, oy, oz = offset
            print(f"Schematic dimensions: {width}x{height}x{length}, Offset: {ox},{oy},{oz}")

            inverse_palette = {int(v): k for k, v in palette.items()}
            block_indices = [int(i) for i in block_data]

            for y in range(height):
                for z in range(length):
                    for x in range(width):
                        index = y * (length * width) + z * width + x
                        idx = block_indices[index]
                        if idx in inverse_palette:
                            state = inverse_palette[idx]
                            block_name = state.split('[')[0]
                            blocks.append((x + ox, y + oy, z + oz, block_name))
        except Exception as e:
            print(f"Error parsing schematic {path}: {e}")
            # Try alternative parsing without gzip
            try:
                schematic = nbtlib.load(path, gzipped=False)
                data = schematic.root
                width, height, length = data['Width'], data['Height'], data['Length']
                palette = data['Palette']
                block_data = data['BlockData']
                offset = data.get('Offset', [0, 0, 0])
                ox, oy, oz = offset
                print(f"Schematic dimensions (non-gzipped): {width}x{height}x{length}, Offset: {ox},{oy},{oz}")

                inverse_palette = {int(v): k for k, v in palette.items()}
                block_indices = [int(i) for i in block_data]

                for y in range(height):
                    for z in range(length):
                        for x in range(width):
                            index = y * (length * width) + z * width + x
                            idx = block_indices[index]
                            if idx in inverse_palette:
                                state = inverse_palette[idx]
                                block_name = state.split('[')[0]
                                blocks.append((x + ox, y + oy, z + oz, block_name))
            except Exception as e2:
                print(f"Alternative parsing failed for {path}: {e2}")
        return blocks

    def center_camera(self):
        """Center the camera on the schematic."""
        if self.blocks:
            xs = [b[0] for b in self.blocks]
            ys = [b[1] for b in self.blocks]
            zs = [b[2] for b in self.blocks]
            self.camera_x = (min(xs) + max(xs)) / 2
            self.camera_y = (min(ys) + max(ys)) / 2
            self.camera_z = (min(zs) + max(zs)) / 2
            max_dim = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 1)
            self.camera_distance = max(5, max_dim * 1.5)
            print(f"Camera centered at ({self.camera_x}, {self.camera_y}, {self.camera_z}), distance: {self.camera_distance}")
        else:
            print("No blocks to center camera on")
            self.camera_distance = 10.0  # Default distance for empty schematic

    def update_camera(self):
        """Update camera position and orientation."""
        cos_pitch = np.cos(np.radians(self.camera_pitch))
        sin_pitch = np.sin(np.radians(self.camera_pitch))
        cos_yaw = np.cos(np.radians(self.camera_yaw))
        sin_yaw = np.sin(np.radians(self.camera_yaw))
        camera_pos = np.array([
            self.camera_x + self.camera_distance * cos_pitch * sin_yaw,
            self.camera_y + self.camera_distance * sin_pitch,
            self.camera_z - self.camera_distance * cos_pitch * cos_yaw
        ], dtype=np.float32)
        glLoadIdentity()
        gluLookAt(
            camera_pos[0], camera_pos[1], camera_pos[2],
            self.camera_x, self.camera_y, self.camera_z,
            0.0, 1.0, 0.0
        )
        return camera_pos

    def get_camera_vectors(self):
        """Return camera right, up, and forward vectors."""
        cos_pitch = np.cos(np.radians(self.camera_pitch))
        sin_pitch = np.sin(np.radians(self.camera_pitch))
        cos_yaw = np.cos(np.radians(self.camera_yaw))
        sin_yaw = np.sin(np.radians(self.camera_yaw))
        forward = np.array([-cos_pitch * sin_yaw, sin_pitch, -cos_pitch * cos_yaw], dtype=np.float32)
        forward = forward / np.linalg.norm(forward)
        right = np.array([cos_yaw, 0.0, -sin_yaw], dtype=np.float32)
        right = right / np.linalg.norm(right)
        up = np.cross(right, forward)
        up = up / np.linalg.norm(up)
        return right, up, forward

    def draw_block(self, x, y, z, block_name, is_selected=False):
        """Draw a block with texture or fallback color."""
        vertices = np.array([
            [x-0.5, y-0.5, z-0.5], [x+0.5, y-0.5, z-0.5],
            [x+0.5, y+0.5, z-0.5], [x-0.5, y+0.5, z-0.5],
            [x-0.5, y-0.5, z+0.5], [x+0.5, y-0.5, z+0.5],
            [x+0.5, y+0.5, z+0.5], [x-0.5, y+0.5, z+0.5]
        ], dtype=np.float32)
        faces = [
            (0, 1, 2, 3), (5, 4, 7, 6), (1, 5, 6, 2),
            (4, 0, 3, 7), (3, 2, 6, 7), (4, 5, 1, 0)
        ]
        face_normals = [
            [0, 0, -1], [0, 0, 1], [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0]
        ]
        texcoords = [
            (0, 0), (1, 0), (1, 1), (0, 1)
        ]

        texture_id = self.textures.get(block_name)
        if texture_id:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture_id)
        else:
            glDisable(GL_TEXTURE_2D)
            color = self.block_colors.get(block_name, self.block_colors["default"])
            glColor4f(*color)

        for i, face in enumerate(faces):
            glBegin(GL_QUADS)
            normal = face_normals[i]
            dot = max(0, -np.dot(normal, self.light_dir))
            intensity = self.ambient + (1 - self.ambient) * dot
            if not texture_id:
                face_color = [
                    min(1.0, color[0] * intensity),
                    min(1.0, color[1] * intensity),
                    min(1.0, color[2] * intensity),
                    color[3]
                ]
                glColor4f(*face_color)
            glNormal3fv(normal)
            for j, vertex_idx in enumerate(face):
                if texture_id:
                    glTexCoord2f(*texcoords[j])
                glVertex3fv(vertices[vertex_idx])
            glEnd()

        # Draw edges
        glDisable(GL_TEXTURE_2D)
        glColor4f(0.0, 0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        edges = [
            (0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4),
            (0,4), (1,5), (2,6), (3,7)
        ]
        for edge in edges:
            glVertex3fv(vertices[edge[0]])
            glVertex3fv(vertices[edge[1]])
        glEnd()
        if is_selected:
            glColor4f(self.ORANGE[0], self.ORANGE[1], self.ORANGE[2], 1.0)
            glBegin(GL_LINES)
            for edge in edges:
                glVertex3fv(vertices[edge[0]])
                glVertex3fv(vertices[edge[1]])
            glEnd()

    def draw_ground(self):
        """Draw a checkerboard ground plane."""
        grid_size = 20
        tile_size = 1.0
        glDisable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        for i in range(-grid_size, grid_size + 1):
            for j in range(-grid_size, grid_size + 1):
                x = i * tile_size
                z = j * tile_size
                color = self.LIGHT_GRAY if (i + j) % 2 == 0 else self.DARK_GRAY
                glColor4f(*color)
                glVertex3f(x, -0.5, z)
                glVertex3f(x + tile_size, -0.5, z)
                glVertex3f(x + tile_size, -0.5, z + tile_size)
                glVertex3f(x, -0.5, z + tile_size)
        glEnd()

    def select_block(self, mx, my, camera_pos):
        """Select the closest block to the mouse click."""
        closest = None
        min_dist = float('inf')
        mx = (mx - self.RENDER_X) / self.RENDER_WIDTH * 2 - 1
        my = -(my - self.RENDER_Y) / self.RENDER_HEIGHT * 2 + 1
        for i, (bx, by, bz, _) in enumerate(self.blocks):
            dist = np.linalg.norm(np.array([bx, by, bz]) - camera_pos)
            if dist < min_dist:
                min_dist = dist
                closest = i
        self.selected_block = closest

    def run(self):
        """Main loop for rendering."""
        running = True
        move_speed = 0.1
        font = pygame.font.SysFont("arial", 24)
        while running:
            camera_pos = self.update_camera()
            keys = pygame.key.get_pressed()
            shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.RENDER_X <= event.pos[0] < self.RENDER_X + self.RENDER_WIDTH and self.RENDER_Y <= event.pos[1] < self.RENDER_Y + self.RENDER_HEIGHT:
                        if event.button == 1:
                            self.dragging_left = True
                            self.last_mouse_pos = event.pos
                            self.select_block(*event.pos, camera_pos)
                        elif event.button == 2:
                            self.dragging_middle = True
                            self.last_mouse_pos = event.pos
                        elif event.button == 4:
                            self.camera_distance = max(2, self.camera_distance - 0.5)
                        elif event.button == 5:
                            self.camera_distance = min(50, self.camera_distance + 0.5)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging_left = False
                    elif event.button == 2:
                        self.dragging_middle = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging_left:
                        dx, dy = event.pos[0] - self.last_mouse_pos[0], event.pos[1] - self.last_mouse_pos[1]
                        right, up, _ = self.get_camera_vectors()
                        pan_speed = 0.02
                        self.camera_x -= dx * pan_speed * right[0]
                        self.camera_y -= dx * pan_speed * right[1]
                        self.camera_z -= dx * pan_speed * right[2]
                        self.camera_x += dy * pan_speed * up[0]
                        self.camera_y += dy * pan_speed * up[1]
                        self.camera_z += dy * pan_speed * up[2]
                        self.last_mouse_pos = event.pos
                    elif self.dragging_middle:
                        dx, dy = event.pos[0] - self.last_mouse_pos[0], event.pos[1] - self.last_mouse_pos[1]
                        self.camera_yaw += dx * 0.1
                        self.camera_pitch = max(-89, min(89, self.camera_pitch + dy * 0.1))
                        self.last_mouse_pos = event.pos

            # WASD movement
            if shift:
                right, _, forward = self.get_camera_vectors()
                if keys[pygame.K_w]:
                    self.camera_x += move_speed * forward[0]
                    self.camera_y += move_speed * forward[1]
                    self.camera_z += move_speed * forward[2]
                if keys[pygame.K_s]:
                    self.camera_x -= move_speed * forward[0]
                    self.camera_y -= move_speed * forward[1]
                    self.camera_z -= move_speed * forward[2]
                if keys[pygame.K_a]:
                    self.camera_x -= move_speed * right[0]
                    self.camera_y -= move_speed * right[1]
                    self.camera_z -= move_speed * right[2]
                if keys[pygame.K_d]:
                    self.camera_x += move_speed * right[0]
                    self.camera_y += move_speed * right[1]
                    self.camera_z += move_speed * right[2]

            # Draw
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.draw_ground()
            for i, (x, y, z, block_name) in enumerate(self.blocks):
                self.draw_block(x, y, z, block_name, is_selected=(i == self.selected_block))

            # UI
            self.screen.fill((0.1, 0.1, 0.1))
            instructions = [
                "Left drag: Pan, Middle drag: Orbit, Scroll: Zoom",
                "Shift + WASD: Move camera",
                "Left click: Select block (orange outline)",
                "ESC or 'p': Exit"
            ]
            if not self.blocks:
                instructions.append("No blocks loaded. Check schematic file.")
            for i, text in enumerate(instructions):
                surface = font.render(text, True, self.WHITE)
                self.screen.blit(surface, (10, 10 + i * 30))

            pygame.display.flip()
            self.clock.tick(self.FPS)

        # Cleanup textures
        for texture_id in self.textures.values():
            glDeleteTextures([texture_id])
        pygame.quit()