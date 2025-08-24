import math
import requests
from io import BytesIO
from PIL import Image
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import QTimer, QSize
from PyQt6.QtWidgets import QApplication
from OpenGL.GL import *
from OpenGL.GLU import *

uvs_dict = {
    "head": [
        (8, 8, 8, 8),
        (24, 8, 8, 8),
        (0, 8, 8, 8),
        (16, 8, 8, 8),
        (8, 0, 8, 8),
        (16, 0, 8, 8),
    ],
    "hat": [
        (40, 8, 8, 8),
        (56, 8, 8, 8),
        (32, 8, 8, 8),
        (48, 8, 8, 8),
        (40, 0, 8, 8),
        (48, 0, 8, 8),
    ],
    "body": [
        (20, 20, 8, 12),
        (32, 20, 8, 12),
        (16, 20, 4, 12),
        (28, 20, 4, 12),
        (20, 16, 8, 4),
        (28, 16, 8, 4),
    ],
    "jacket": [
        (20, 36, 8, 12),
        (16, 36, 4, 12),
        (28, 36, 4, 12),
        (32, 36, 8, 12),
        (20, 32, 8, 4),
        (28, 32, 8, 4),
    ],
    "arm-left": [
        (36, 52, 4, 12),
        (44, 52, 4, 12),
        (32, 52, 4, 12),
        (40, 52, 4, 12),
        (36, 48, 4, 4),
        (40, 48, 4, 4),
    ],
    "arm-left-slim": [
        (36, 52, 3, 12),
        (43, 52, 3, 12),
        (32, 52, 4, 12),
        (39, 52, 4, 12),
        (36, 48, 3, 4),
        (39, 48, 3, 4),
    ],
    "sleeve-left": [
        (52, 52, 4, 12),
        (48, 52, 4, 12),
        (56, 52, 4, 12),
        (60, 52, 4, 12),
        (52, 48, 4, 4),
        (56, 48, 4, 4),
    ],
    "sleeve-left-slim": [
        (52, 52, 3, 12),
        (48, 52, 3, 12),
        (55, 52, 4, 12),
        (59, 52, 4, 12),
        (52, 48, 3, 4),
        (55, 48, 3, 4),
    ],
    "arm-right": [
        (44, 20, 4, 12),
        (52, 20, 4, 12),
        (40, 20, 4, 12),
        (48, 20, 4, 12),
        (44, 16, 4, 4),
        (48, 16, 4, 4),
    ],
    "arm-right-slim": [
        (44, 20, 3, 12),
        (51, 20, 3, 12),
        (40, 20, 4, 12),
        (47, 20, 4, 12),
        (44, 16, 3, 4),
        (47, 16, 3, 4),
    ],
    "sleeve-right": [
        (44, 36, 4, 12),
        (52, 36, 4, 12),
        (40, 36, 4, 12),
        (48, 36, 4, 12),
        (44, 32, 4, 4),
        (48, 32, 4, 4),
    ],
    "sleeve-right-slim": [
        (44, 36, 3, 12),
        (51, 36, 3, 12),
        (40, 36, 4, 12),
        (47, 36, 4, 12),
        (44, 32, 3, 4),
        (47, 32, 3, 4),
    ],
    "leg-left": [
        (20, 52, 4, 12),
        (28, 52, 4, 12),
        (16, 52, 4, 12),
        (24, 52, 4, 12),
        (20, 48, 4, 4),
        (24, 48, 4, 4),
    ],
    "pant-left": [
        (4, 52, 4, 12),
        (0, 52, 4, 12),
        (8, 52, 4, 12),
        (12, 52, 4, 12),
        (4, 48, 4, 4),
        (8, 48, 4, 4),
    ],
    "leg-right": [
        (4, 20, 4, 12),
        (12, 20, 4, 12),
        (0, 20, 4, 12),
        (8, 20, 4, 12),
        (4, 16, 4, 4),
        (8, 16, 4, 4),
    ],
    "pant-right": [
        (4, 36, 4, 12),
        (12, 36, 4, 12),
        (0, 36, 4, 12),
        (8, 36, 4, 12),
        (4, 32, 4, 4),
        (8, 32, 4, 4),
    ],
}


class MinecraftViewer(QOpenGLWidget):
    swing_phase = 0
    slim: bool
    skin_url: str
    def __init__(self, skin_url, slim, parent=None):
        super().__init__(parent=parent)
        self.setMouseTracking(True)
        self.slim = slim
        self.skin_url = skin_url
        self.head_angle_x = 0
        self.head_angle_y = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS

    def minimumSizeHint(self):
        return QSize(10, 30)
    
    def update_animation(self):
        self.swing_phase += 0.1  # Adjust speed here
        self.update()  # Triggers paintGL

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glClearColor(0.2, 0.2, 0.2, 1.0)  # Background color
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # Load texture
        self.texture_id = self.load_skin_texture(self.skin_url)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h if h else 1)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h if h else 1.0, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        model_height = 32
        model_width = 12
        #margin_px = 50

        w = max(self.width(), 1)
        h = max(self.height(), 1)

        aspect = w / h
        #margin_x_frac = min(margin_px / w, 0.4)  # Clamp max 40%
        #margin_y_frac = min(margin_px / h, 0.4)

        margin_x_frac = 0.1
        margin_y_frac = 0.1

        # Prevent division by zero
        denom_y = max(1e-3, 1 - 2 * margin_y_frac)
        denom_x = max(1e-3, 1 - 2 * margin_x_frac)

        fov_y_rad = math.radians(45.0)

        total_height = model_height / denom_y
        total_width = model_width / denom_x

        dist_y = total_height / (2 * math.tan(fov_y_rad / 2))
        fov_x_rad = 2 * math.atan(math.tan(fov_y_rad / 2) * aspect)
        dist_x = total_width / (2 * math.tan(fov_x_rad / 2))

        distance = max(dist_x, dist_y)

        model_center_y = model_height / 2 - 2

        gluLookAt(0, model_center_y, distance,
                  0, model_center_y, 0,
                  0, 1, 0)

        glBindTexture(GL_TEXTURE_2D, self.texture_id)

        self.draw_body()
        self.draw_leg(-2, True, 0)
        self.draw_leg(2, False, math.pi)
        self.draw_arm(-6, True, 0)
        self.draw_arm(6, False, math.pi)
        self.draw_head()
        self.draw_hat()
        self.draw_sleeve(-6, True, 0)
        self.draw_sleeve(6, False, math.pi)
        self.draw_pant(-2, True, 0)
        self.draw_pant(2, False, math.pi)
        self.draw_jacket()

    def mouseMoveEvent(self, event):
        dx = event.position().x() - self.width() / 2
        dy = event.position().y() - self.height() / 2
        self.head_angle_y = dx / 5
        self.head_angle_x = dy / 5
        self.update()

    def load_skin_texture(self, url):
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img = img.convert("RGBA")
        img_data = img.tobytes()

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            img.width,
            img.height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            img_data,
        )
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        return texture_id

    def uv(self, x, y, w, h, mirror=False):
        u1 = x / 64.0
        v1 = y / 64.0
        u2 = (x + w) / 64.0
        v2 = (y + h) / 64.0

        if mirror:
            u1, u2 = u2, u1  # Swap U coordinates for horizontal mirroring

        return (u1, v1, u2, v2)

    def draw_box(self, size, uv_faces):
        w, h, d = size
        w /= 2
        h /= 2
        d /= 2

        # Define the coordinates for the faces
        coords = [
            [[-w, -h, d], [w, -h, d], [w, h, d], [-w, h, d]],  # Front
            [[w, -h, -d], [-w, -h, -d], [-w, h, -d], [w, h, -d]],  # Back
            [[-w, -h, -d], [-w, -h, d], [-w, h, d], [-w, h, -d]],  # Left
            [[w, -h, d], [w, -h, -d], [w, h, -d], [w, h, d]],  # Right
            [[-w, h, d], [w, h, d], [w, h, -d], [-w, h, -d]],  # Top
            [[-w, -h, -d], [w, -h, -d], [w, -h, d], [-w, -h, d]],  # Bottom
        ]

        glBegin(GL_QUADS)
        for i in range(6):
            u0, v0, u1, v1 = uv_faces[i]
            glTexCoord2f(u0, v1)
            glVertex3fv(coords[i][0])
            glTexCoord2f(u1, v1)
            glVertex3fv(coords[i][1])
            glTexCoord2f(u1, v0)
            glVertex3fv(coords[i][2])
            glTexCoord2f(u0, v0)
            glVertex3fv(coords[i][3])
        glEnd()

    def draw_head(self):
        glPushMatrix()
        diff=-4
        glTranslatef(0, 24+diff, 0)

        glRotatef(self.head_angle_x, 1, 0, 0)
        glRotatef(self.head_angle_y, 0, 1, 0)

        glTranslatef(0, -diff, 0)  # Move back to base of the head
        # Head UVs (8x8 faces from 64x64 texture)
        uvs = list(map(lambda uv: self.uv(*uv), uvs_dict["head"]))
        self.draw_box((8, 8, 8), uvs)
        glPopMatrix()

    def draw_body(self):
        glPushMatrix()
        glTranslatef(0, 14, 0)

        uvs = list(map(lambda uv: self.uv(*uv), uvs_dict["body"]))
        self.draw_box((8, 12, 4), uvs)
        glPopMatrix()

    def draw_arm(self, x_offset, left, swing_offset):
        pivot_down = 2
        glPushMatrix()
        # Translate to shoulder joint (top of arm)
        glTranslatef(x_offset, 20 - pivot_down, 0)

        # Apply swing rotation around Z (local forward/back motion)
        swing_angle = (
            math.sin(self.swing_phase + swing_offset) * 30
        )  # Adjust amplitude as needed
        glRotatef(swing_angle, 1, 0, 0)

        # Move origin back down to draw the arm box below the pivot point
        glTranslatef(0, -6 + pivot_down, 0)  # 12/2 = 6, since arm height is 12

        if left:
            uvs = list(map(lambda uv: self.uv(*uv), uvs_dict["arm-left-slim" if self.slim else "arm-left"]))
        else:
            uvs = list(map(lambda uv: self.uv(*uv), uvs_dict["arm-right-slim" if self.slim else "arm-right"]))
        self.draw_box((3 if self.slim else 4, 12, 4), uvs)
        glPopMatrix()

    def draw_leg(self, x_offset, left, swing_offset):
        glPushMatrix()
        # Translate to shoulder joint (top of arm)
        glTranslatef(x_offset, 8, 0)

        # Apply swing rotation around Z (local forward/back motion)
        swing_angle = (
            math.sin(self.swing_phase + swing_offset) * 30
        )  # Adjust amplitude as needed
        glRotatef(swing_angle, 1, 0, 0)

        # Move origin back down to draw the arm box below the pivot point
        glTranslatef(0, -6, 0)  # 12/2 = 6, since arm height is 12

        if left:
            uvs = list(map(lambda uv: self.uv(*uv), uvs_dict["leg-left"]))
        else:
            uvs = list(map(lambda uv: self.uv(*uv), uvs_dict["leg-right"]))
        self.draw_box((4, 12, 4), uvs)
        glPopMatrix()

    def draw_hat(self):
        glPushMatrix()
        diff=-4
        glTranslatef(0, 24+diff, 0)

        glRotatef(self.head_angle_x, 1, 0, 0)
        glRotatef(self.head_angle_y, 0, 1, 0)

        glTranslatef(0, -diff, 0)  # Move back to base of the head
        # Head UVs (8x8 faces from 64x64 texture)
        uvs = list(map(lambda uv: self.uv(*uv), uvs_dict["hat"]))
        self.draw_box((9, 9, 9), uvs)
        glPopMatrix()

    def draw_jacket(self):
        glPushMatrix()
        glTranslatef(0, 14, 0)

        uvs = list(map(lambda uv: self.uv(*uv), uvs_dict["jacket"]))
        self.draw_box((8.5, 12.5, 4.5), uvs)
        glPopMatrix()

    def draw_sleeve(self, x_offset, left, swing_offset):
        glPushMatrix()
        pivot_down = 2
        # Translate to shoulder joint (top of arm)
        glTranslatef(x_offset, 20 - pivot_down, 0)

        # Apply swing rotation around Z (local forward/back motion)
        swing_angle = (
            math.sin(self.swing_phase + swing_offset) * 30
        )  # Adjust amplitude as needed
        glRotatef(swing_angle, 1, 0, 0)

        # Move origin back down to draw the arm box below the pivot point
        glTranslatef(0, -6 + pivot_down, 0)  # 12/2 = 6, since arm height is 12

        if left:
            uvs = list(map(lambda uv: self.uv(*uv), uvs_dict["sleeve-left-slim" if self.slim else "sleeve-left"]))
        else:
            uvs = list(map(lambda uv: self.uv(*uv), uvs_dict["sleeve-right-slim" if self.slim else "sleeve-right"]))
        self.draw_box((3.5 if self.slim else 4.5, 12.5, 4.5), uvs)
        glPopMatrix()

    def draw_pant(self, x_offset, left, swing_offset):
        glPushMatrix()
        # Translate to shoulder joint (top of arm)
        glTranslatef(x_offset, 8, 0)

        # Apply swing rotation around Z (local forward/back motion)
        swing_angle = (
            math.sin(self.swing_phase + swing_offset) * 30
        )  # Adjust amplitude as needed
        glRotatef(swing_angle, 1, 0, 0)

        # Move origin back down to draw the arm box below the pivot point
        glTranslatef(0, -6, 0)  # 12/2 = 6, since arm height is 12

        if left:
            uvs = list(map(lambda uv: self.uv(*uv), uvs_dict["pant-left"]))
        else:
            uvs = list(map(lambda uv: self.uv(*uv), uvs_dict["pant-right"]))
        self.draw_box((4.5, 12.5, 4.5), uvs)
        glPopMatrix()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = MinecraftViewer("https://www.minecraftskins.net/ghastpilot/download", False)
    w.show()
    sys.exit(app.exec())