import glfw
from OpenGL.GL import *
import numpy as np

class PixelArtEditor:
    def __init__(self, width=800, height=600, grid_size=20):
        # Initialize GLFW
        if not glfw.init():
            return

        # Create window
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.cols = width // grid_size
        self.rows = height // grid_size

        # Create window
        self.window = glfw.create_window(width, height, "Pixel Art Editor", None, None)
        if not self.window:
            glfw.terminate()
            return

        # Make context current
        glfw.make_context_current(self.window)

        # Set callbacks
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
        glfw.set_cursor_pos_callback(self.window, self.cursor_pos_callback)
        glfw.set_key_callback(self.window, self.key_callback)

        # Initialize drawing parameters
        self.current_color = (0, 0, 0, 1)  # Black
        self.drawing = False
        self.last_grid_x = None
        self.last_grid_y = None
        self.eraser_mode = False

        # Canvas initialization
        self.canvas = np.full((self.rows, self.cols, 4), 
                               (1, 1, 1, 1), dtype=np.float32)  # White
        
        # Color palette
        self.palette = [
            (0, 0, 0, 1),     # Black
            (1, 0, 0, 1),     # Red
            (0, 1, 0, 1),     # Green
            (0, 0, 1, 1),     # Blue
            (1, 1, 0, 1),     # Yellow
            (1, 0, 1, 1),     # Magenta
            (0, 1, 1, 1),     # Cyan
            (1, 1, 1, 1)      # White
        ]

    def get_grid_position(self, x, y):
        """Convert screen coordinates to grid coordinates"""
        # Flip the y-coordinate
        flipped_y = self.height - y
        grid_x = int(x // self.grid_size)
        grid_y = int(flipped_y // self.grid_size)
        return grid_x, grid_y


    def draw_line(self, x1, y1, x2, y2, color):
        """Bresenham's line algorithm for pixel drawing"""
        # Swap coordinates if drawing from bottom to top
        if y1 > y2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        if dx > dy:
            err = dx / 2.0
            while x != x2:
                self.canvas[y, x] = color
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y2:
                self.canvas[y, x] = color
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        
        # Draw the final pixel
        self.canvas[y, x] = color

    def mouse_button_callback(self, window, button, action, mods):
        """Handle mouse button events"""
        if button == glfw.MOUSE_BUTTON_LEFT:
            x, y = glfw.get_cursor_pos(window)
            
            if action == glfw.PRESS:
                # Check if clicked in palette area
                if y > self.height - 50:
                    color_index = int(x // 50)
                    if color_index < len(self.palette):
                        self.current_color = self.palette[color_index]
                else:
                    # Start drawing or erasing
                    self.drawing = True
                    grid_x, grid_y = self.get_grid_position(x, y)
                    if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
                        self.canvas[grid_y, grid_x] = (1, 1, 1, 1) if self.eraser_mode else self.current_color
                        self.last_grid_x = grid_x
                        self.last_grid_y = grid_y
            
            elif action == glfw.RELEASE:
                self.drawing = False
                self.last_grid_x = None
                self.last_grid_y = None


    def cursor_pos_callback(self, window, x, y):
        if self.drawing and y < self.height - 50:
            grid_x, grid_y = self.get_grid_position(x, y)
            if (0 <= grid_x < self.cols and 0 <= grid_y < self.rows and 
                self.last_grid_x is not None and self.last_grid_y is not None):
                # Draw a line between the last point and current point
                color = (1, 1, 1, 1) if self.eraser_mode else self.current_color
                self.draw_line(self.last_grid_x, self.last_grid_y, grid_x, grid_y, color)
                # Update last position
                self.last_grid_x = grid_x
                self.last_grid_y = grid_y

    def key_callback(self, window, key, scancode, action, mods):
        """Handle keyboard events"""
        if action == glfw.PRESS:
            if key == glfw.KEY_C:
                # Clear canvas
                self.canvas.fill(1)
            elif key == glfw.KEY_S:
                # Save functionality (placeholder)
                print("Save functionality not implemented in this version")
            elif key == glfw.KEY_E:
                # Toggle eraser mode
                self.eraser_mode = not self.eraser_mode
                print("Eraser mode:", "On" if self.eraser_mode else "Off")


    def draw_grid(self):
        """Draw grid lines"""
        glColor3f(0.8, 0.8, 0.8)  # Light gray grid lines
        glBegin(GL_LINES)
        
        # Vertical lines
        for x in range(self.cols + 1):
            norm_x = x / self.cols * 2 - 1
            glVertex2f(norm_x, -1)
            glVertex2f(norm_x, 1)
        
        # Horizontal lines
        for y in range(self.rows + 1):
            norm_y = y / self.rows * 2 - 1
            glVertex2f(-1, norm_y)
            glVertex2f(1, norm_y)
        
        glEnd()

    def draw_canvas(self):
        glBegin(GL_QUADS)
        for y in range(self.rows):
            for x in range(self.cols):
                # Get color for this pixel
                color = self.canvas[y, x]
                glColor4fv(color)
                
                # Calculate normalized coordinates
                x1 = x / self.cols * 2 - 1
                y1 = y / self.rows * 2 - 1
                x2 = (x + 1) / self.cols * 2 - 1
                y2 = (y + 1) / self.rows * 2 - 1
                
                # Draw pixel as a quad
                glVertex2f(x1, y1)
                glVertex2f(x2, y1)
                glVertex2f(x2, y2)
                glVertex2f(x1, y2)
        glEnd()

    def draw_palette(self):
        """Draw color palette"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glBegin(GL_QUADS)
        for i, color in enumerate(self.palette):
            glColor4fv(color)
            x = i * 50
            glVertex2f(x, self.height - 50)
            glVertex2f(x + 50, self.height - 50)
            glVertex2f(x + 50, self.height)
            glVertex2f(x, self.height)
        glEnd()

    def run(self):
        """Main game loop"""
        while not glfw.window_should_close(self.window):
            # Clear the screen
            glClear(GL_COLOR_BUFFER_BIT)
            
            # Set up orthographic projection
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(-1, 1, -1, 1, -1, 1)
            
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # Draw canvas and grid
            self.draw_canvas()
            self.draw_grid()
            
            # Draw palette
            self.draw_palette()

            # Swap front and back buffers
            glfw.swap_buffers(self.window)

            # Poll for and process events
            glfw.poll_events()

        # Cleanup
        glfw.terminate()

# Run the editor
if __name__ == "__main__":
    editor = PixelArtEditor()
    editor.run()
