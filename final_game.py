import math
import random
import sys
import threading
import time

import cv2
import pygame

# ============================================================
# MEDIAPIPE DISABLED - USING OPENCV ONLY!
# ============================================================
MEDIAPIPE_AVAILABLE = False
mp = None


# ============================================================
# PANDA VISION — POLISHED TOUCHLESS RUNNER
# ============================================================

WIDTH, HEIGHT = 1000, 600
GROUND_Y = 500
FPS = 60

LANES = [220, 500, 780]

GRAVITY = 0.82
JUMP_POWER = -17.0

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PandaVision — Touchless Runner")
clock = pygame.time.Clock()

FONT = pygame.font.Font(None, 34)
SMALL_FONT = pygame.font.Font(None, 25)
BIG_FONT = pygame.font.Font(None, 72)
TITLE_FONT = pygame.font.Font(None, 58)


# -----------------------------
# Colors
# -----------------------------
WHITE = (248, 248, 248)
BLACK = (22, 22, 22)
DARK = (32, 36, 42)
GRAY = (115, 120, 126)
LIGHT_GRAY = (210, 214, 220)
GREEN = (75, 190, 105)
RED = (235, 75, 75)
YELLOW = (245, 205, 65)
BAMBOO = (80, 170, 80)
BAMBOO_DARK = (42, 112, 55)
PANDA_BLACK = (28, 30, 32)
PANDA_WHITE = (245, 245, 242)
SKY_TOP = (120, 205, 246)
SKY_BOTTOM = (224, 183, 226)


def clamp(value, low, high):
    return max(low, min(high, value))


def lerp(a, b, amount):
    return a + (b - a) * amount


# ============================================================
# WEBCAM CONTROL - OPENCV ONLY!
# ============================================================

class WebcamControl:
    """
    OpenCV motion tracking only - MediaPipe disabled.
    
    Controls:
      Wave left/right before starting -> start
      Move body left/right             -> change lane
      Move body upward                 -> jump
      Move body downward              -> duck
    """

    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            # Try the default backend if DirectShow fails.
            self.cap.release()
            self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            raise RuntimeError("Could not open webcam.")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.running = False
        self.thread = None
        self.lock = threading.Lock()

        self.game_started = False
        self.body_detected = False

        self.jump_event = False
        self.duck_event = False
        self.left_event = False
        self.right_event = False

        self.cx = None
        self.cy = None
        self.body_height = None

        self.prev_cx = None
        self.prev_cy = None
        self.prev_h = None

        self.smooth_cx = None
        self.smooth_cy = None
        self.smooth_h = None

        self.cooldown = 0
        self.COOLDOWN_FRAMES = 9

        self.last_action = "READY"
        self.last_action_time = 0

        self.motion_history = []
        self.wave_score = 0

        # Motion fallback - OpenCV.
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=160,
            varThreshold=32,
            detectShadows=False,
        )

        self.fallback_warmup = 0

        # MediaPipe disabled - using OpenCV only!
        self.pose = None
        print("📷 Using OpenCV motion tracking only!")

    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
        )
        self.thread.start()

    def _set_event(self, name):
        with self.lock:
            setattr(self, f"{name}_event", True)
            self.last_action = name.upper()
            self.last_action_time = time.time()

    def _process_motion_fallback(self, frame):
        self.fallback_warmup += 1

        mask = self.bg_subtractor.apply(frame)

        # Ignore the initial background-learning period.
        if self.fallback_warmup < 35:
            return None

        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (5, 5),
        )

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        best = None
        best_area = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 1200 or area < best_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            # Reject tiny horizontal background noise.
            if h < 60 or w < 35:
                continue

            best = (x, y, w, h)
            best_area = area

        if best is None:
            return None

        x, y, w, h = best
        cx = x + w // 2
        cy = y + h // 2

        return cx, cy, h, (x, y, x + w, y + h), None

    def _detect_actions(self, cx, cy, h):
        if self.smooth_cx is None:
            self.smooth_cx = cx
            self.smooth_cy = cy
            self.smooth_h = h
        else:
            self.smooth_cx = lerp(self.smooth_cx, cx, 0.38)
            self.smooth_cy = lerp(self.smooth_cy, cy, 0.38)
            self.smooth_h = lerp(self.smooth_h, h, 0.38)

        cx = self.smooth_cx
        cy = self.smooth_cy
        h = self.smooth_h

        if self.prev_cx is None:
            self.prev_cx = cx
            self.prev_cy = cy
            self.prev_h = h
            return

        dx = cx - self.prev_cx
        dy = cy - self.prev_cy
        dh = h - self.prev_h

        if not self.game_started:
            self.motion_history.append(cx)

            if len(self.motion_history) > 24:
                self.motion_history.pop(0)

            if len(self.motion_history) >= 12:
                movement = max(self.motion_history) - min(
                    self.motion_history
                )

                if movement > 55:
                    self.wave_score += 1
                else:
                    self.wave_score = max(0, self.wave_score - 1)

                if self.wave_score >= 4:
                    with self.lock:
                        self.game_started = True

                    self.motion_history.clear()
                    self.wave_score = 0
                    self.last_action = "GAME START"

            self.prev_cx = cx
            self.prev_cy = cy
            self.prev_h = h
            return

        if self.cooldown > 0:
            self.cooldown -= 1

        if self.cooldown == 0:
            # Horizontal body movement.
            if dx > 18:
                self._set_event("right")
                self.cooldown = self.COOLDOWN_FRAMES

            elif dx < -18:
                self._set_event("left")
                self.cooldown = self.COOLDOWN_FRAMES

            # Vertical movement.
            # Moving upward means body center moves up.
            elif dy < -13:
                self._set_event("jump")
                self.cooldown = self.COOLDOWN_FRAMES

            # Moving downward OR temporarily shrinking body box.
            elif dy > 18 or dh < -10:
                self._set_event("duck")
                self.cooldown = self.COOLDOWN_FRAMES

        self.prev_cx = cx
        self.prev_cy = cy
        self.prev_h = h

    def _draw_camera_ui(self, frame, detection):
        if detection:
            x, y, h, box, _ = detection
            x1, y1, x2, y2 = box

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (80, 220, 120),
                2,
            )

            cv2.circle(
                frame,
                (int(x), int(y)),
                6,
                (0, 255, 255),
                -1,
            )

        # Show status
        mode = "OPENCV MOTION TRACKING"
        color = (70, 230, 100) if detection else (0, 180, 255)

        cv2.putText(
            frame,
            mode,
            (12, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            color,
            2,
        )

        status = (
            "GAME RUNNING"
            if self.game_started
            else "WAVE LEFT-RIGHT TO START"
        )

        cv2.putText(
            frame,
            status,
            (12, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"ACTION: {self.last_action}",
            (12, 82),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 220, 80),
            2,
        )

        cv2.putText(
            frame,
            "Move LEFT/RIGHT | UP=JUMP | DOWN=DUCK",
            (12, frame.shape[0] - 16),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (240, 240, 240),
            1,
        )

    def _run(self):
        while self.running:
            ok, frame = self.cap.read()

            if not ok:
                continue

            frame = cv2.flip(frame, 1)

            # OpenCV motion tracking only
            detection = self._process_motion_fallback(frame)

            with self.lock:
                self.body_detected = detection is not None

            if detection is not None:
                cx, cy, h, _, _ = detection

                with self.lock:
                    self.cx = cx
                    self.cy = cy
                    self.body_height = h

                self._detect_actions(cx, cy, h)
            else:
                with self.lock:
                    self.body_detected = False

                # Don't immediately destroy the smoothed state.
                self.motion_history.clear()
                self.wave_score = max(0, self.wave_score - 1)

            self._draw_camera_ui(frame, detection)

            cv2.imshow("PandaVision — Webcam", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                self.running = False
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def is_game_started(self):
        with self.lock:
            return self.game_started

    def is_body_detected(self):
        with self.lock:
            return self.body_detected

    def get_event(self, name):
        with self.lock:
            attr = f"{name}_event"
            value = getattr(self, attr)
            setattr(self, attr, False)
            return value

    def reset_start(self):
        with self.lock:
            self.game_started = False
            self.motion_history.clear()
            self.wave_score = 0
            self.prev_cx = None
            self.prev_cy = None
            self.prev_h = None
            self.last_action = "READY"

    def stop(self):
        self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.5)

        if self.pose is not None:
            try:
                self.pose.close()
            except Exception:
                pass

        print("Webcam stopped.")


# ============================================================
# PANDA
# ============================================================

class Panda:
    def __init__(self):
        self.lane = 1
        self.x = float(LANES[self.lane] - 30)
        self.target_x = float(LANES[self.lane] - 30)

        self.base_w = 60
        self.base_h = 82

        self.y = float(GROUND_Y - self.base_h)
        self.vy = 0.0

        self.jumping = False
        self.ducking = False
        self.dead = False

        self.anim_time = 0.0
        self.run_frame = 0

        self.duck_timer = 0

    def move_left(self):
        if self.lane > 0 and not self.dead:
            self.lane -= 1
            self.target_x = LANES[self.lane] - 30

    def move_right(self):
        if self.lane < 2 and not self.dead:
            self.lane += 1
            self.target_x = LANES[self.lane] - 30

    def jump(self):
        if (
            not self.jumping
            and not self.ducking
            and not self.dead
        ):
            self.jumping = True
            self.vy = JUMP_POWER

    def duck(self):
        if not self.jumping and not self.dead:
            self.ducking = True
            self.duck_timer = 14

    def update(self, dt):
        # Smooth lane movement.
        self.x = lerp(self.x, self.target_x, min(1.0, 12.0 * dt))

        if self.jumping:
            self.y += self.vy
            self.vy += GRAVITY

            if self.y >= GROUND_Y - self.base_h:
                self.y = GROUND_Y - self.base_h
                self.vy = 0
                self.jumping = False

        if self.ducking:
            self.duck_timer -= 1

            if self.duck_timer <= 0:
                self.ducking = False

        self.anim_time += dt

        if self.anim_time >= 0.11:
            self.anim_time = 0
            self.run_frame = (self.run_frame + 1) % 4

    def get_rect(self):
        if self.ducking:
            return pygame.Rect(
                int(self.x + 2),
                int(GROUND_Y - 48),
                72,
                43,
            )

        return pygame.Rect(
            int(self.x + 8),
            int(self.y + 8),
            45,
            70,
        )

    def draw(self, surface):
        x = int(self.x)
        y = int(self.y)

        if self.dead:
            self._draw_dead(surface, x, y)
            return

        if self.ducking:
            self._draw_duck(surface, x, GROUND_Y - 48)
            return

        # Shadow.
        shadow = pygame.Rect(x + 7, GROUND_Y - 8, 48, 8)
        pygame.draw.ellipse(surface, (55, 55, 55), shadow)

        # Body.
        pygame.draw.rect(
            surface,
            PANDA_BLACK,
            (x + 8, y + 23, 45, 53),
            14,
        )

        # Belly.
        pygame.draw.ellipse(
            surface,
            PANDA_WHITE,
            (x + 16, y + 36, 29, 35),
        )

        # Ears.
        pygame.draw.circle(
            surface,
            PANDA_BLACK,
            (x + 16, y + 19),
            11,
        )
        pygame.draw.circle(
            surface,
            PANDA_BLACK,
            (x + 45, y + 19),
            11,
        )

        # Head.
        pygame.draw.ellipse(
            surface,
            PANDA_WHITE,
            (x + 8, y + 8, 46, 43),
        )

        # Eye patches.
        pygame.draw.ellipse(
            surface,
            PANDA_BLACK,
            (x + 14, y + 21, 14, 18),
        )
        pygame.draw.ellipse(
            surface,
            PANDA_BLACK,
            (x + 34, y + 21, 14, 18),
        )

        # Eyes.
        pygame.draw.circle(surface, WHITE, (x + 22, y + 29), 4)
        pygame.draw.circle(surface, WHITE, (x + 41, y + 29), 4)

        pygame.draw.circle(surface, BLACK, (x + 23, y + 30), 2)
        pygame.draw.circle(surface, BLACK, (x + 40, y + 30), 2)

        # Nose + mouth.
        pygame.draw.ellipse(
            surface,
            PANDA_BLACK,
            (x + 28, y + 37, 7, 5),
        )
        pygame.draw.arc(
            surface,
            PANDA_BLACK,
            (x + 25, y + 39, 13, 9),
            0,
            math.pi,
            2,
        )

        # Arms.
        pygame.draw.line(
            surface,
            PANDA_BLACK,
            (x + 10, y + 46),
            (x + 1, y + 58),
            8,
        )
        pygame.draw.line(
            surface,
            PANDA_BLACK,
            (x + 50, y + 46),
            (x + 59, y + 58),
            8,
        )

        # Running legs — four-frame animation.
        phase = self.run_frame

        if self.jumping:
            leg_a = (x + 17, y + 72, x + 9, y + 80)
            leg_b = (x + 43, y + 72, x + 52, y + 80)
        elif phase in (0, 2):
            leg_a = (x + 20, y + 70, x + 12, y + 81)
            leg_b = (x + 40, y + 70, x + 48, y + 81)
        else:
            leg_a = (x + 20, y + 70, x + 25, y + 82)
            leg_b = (x + 40, y + 70, x + 35, y + 82)

        pygame.draw.line(surface, PANDA_BLACK, leg_a[:2], leg_a[2:], 9)
        pygame.draw.line(surface, PANDA_BLACK, leg_b[:2], leg_b[2:], 9)

    def _draw_duck(self, surface, x, y):
        pygame.draw.ellipse(
            surface,
            (55, 55, 55),
            (x + 4, y + 36, 68, 9),
        )

        pygame.draw.rect(
            surface,
            PANDA_BLACK,
            (x + 7, y + 12, 67, 34),
            13,
        )

        pygame.draw.ellipse(
            surface,
            PANDA_WHITE,
            (x + 18, y + 18, 38, 25),
        )

        # Face.
        pygame.draw.circle(surface, PANDA_BLACK, (x + 23, y + 15), 10)
        pygame.draw.circle(surface, PANDA_BLACK, (x + 47, y + 15), 10)

        pygame.draw.circle(surface, WHITE, (x + 27, y + 16), 4)
        pygame.draw.circle(surface, WHITE, (x + 50, y + 16), 4)

        pygame.draw.circle(surface, BLACK, (x + 28, y + 16), 2)
        pygame.draw.circle(surface, BLACK, (x + 49, y + 16), 2)

        pygame.draw.line(
            surface,
            PANDA_BLACK,
            (x + 20, y + 45),
            (x + 10, y + 51),
            7,
        )
        pygame.draw.line(
            surface,
            PANDA_BLACK,
            (x + 58, y + 45),
            (x + 68, y + 51),
            7,
        )

    def _draw_dead(self, surface, x, y):
        pygame.draw.rect(
            surface,
            (150, 45, 50),
            (x + 5, y + 20, 56, 55),
            14,
        )

        pygame.draw.circle(
            surface,
            (245, 245, 245),
            (x + 20, y + 39),
            7,
        )
        pygame.draw.circle(
            surface,
            (245, 245, 245),
            (x + 43, y + 39),
            7,
        )

        pygame.draw.line(surface, RED, (x + 15, y + 34), (x + 25, y + 44), 3)
        pygame.draw.line(surface, RED, (x + 25, y + 34), (x + 15, y + 44), 3)
        pygame.draw.line(surface, RED, (x + 38, y + 34), (x + 48, y + 44), 3)
        pygame.draw.line(surface, RED, (x + 48, y + 34), (x + 38, y + 44), 3)


# ============================================================
# OBSTACLES
# ============================================================

class Obstacle:
    TYPES = ("bamboo", "rock", "log")

    def __init__(self, lane, speed):
        self.lane = lane
        self.x = WIDTH + random.randint(20, 80)
        self.speed = speed
        self.kind = random.choice(self.TYPES)

        if self.kind == "bamboo":
            self.w, self.h = 35, 65
        elif self.kind == "rock":
            self.w, self.h = 65, 43
        else:
            self.w, self.h = 75, 38

        self.y = GROUND_Y - self.h

    def update(self, dt):
        self.x -= self.speed * dt

    def get_rect(self):
        return pygame.Rect(
            int(self.x + 5),
            int(self.y + 5),
            self.w - 10,
            self.h - 5,
        )

    def draw(self, surface):
        x = int(self.x)
        y = int(self.y)

        if self.kind == "bamboo":
            # Stalk.
            pygame.draw.rect(
                surface,
                BAMBOO,
                (x + 8, y, 19, self.h),
                6,
            )

            for yy in range(y + 10, y + self.h, 18):
                pygame.draw.line(
                    surface,
                    BAMBOO_DARK,
                    (x + 8, yy),
                    (x + 27, yy),
                    2,
                )

            pygame.draw.ellipse(
                surface,
                BAMBOO_DARK,
                (x - 8, y + 12, 20, 9),
            )
            pygame.draw.ellipse(
                surface,
                BAMBOO_DARK,
                (x + 25, y + 28, 20, 9),
            )

        elif self.kind == "rock":
            points = [
                (x, y + self.h),
                (x + 10, y + 16),
                (x + 28, y + 3),
                (x + 52, y + 10),
                (x + self.w, y + self.h),
            ]
            pygame.draw.polygon(surface, (105, 108, 112), points)
            pygame.draw.line(
                surface,
                (145, 148, 152),
                (x + 25, y + 9),
                (x + 15, y + 28),
                3,
            )

        else:
            pygame.draw.rect(
                surface,
                (130, 82, 48),
                (x, y + 7, self.w, self.h - 7),
                13,
            )

            for xx in range(x + 15, x + self.w, 22):
                pygame.draw.line(
                    surface,
                    (170, 110, 65),
                    (xx, y + 9),
                    (xx, y + self.h - 6),
                    2,
                )


class Coin:
    def __init__(self, lane, speed):
        self.lane = lane
        self.x = WIDTH + random.randint(60, 180)
        self.y = GROUND_Y - random.choice((90, 125, 160))
        self.speed = speed
        self.radius = 12
        self.spin = random.random() * math.tau

    def update(self, dt):
        self.x -= self.speed * dt
        self.spin += dt * 7

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def draw(self, surface):
        x = int(self.x)
        y = int(self.y)

        width = max(4, int(abs(math.cos(self.spin)) * 12))

        pygame.draw.ellipse(
            surface,
            YELLOW,
            (x - width, y - self.radius, width * 2, self.radius * 2),
        )

        pygame.draw.ellipse(
            surface,
            (255, 235, 115),
            (x - max(2, width - 4), y - 7, max(4, width * 2 - 8), 14),
        )


# ============================================================
# BACKGROUND
# ============================================================

def draw_gradient(surface):
    for y in range(HEIGHT):
        t = y / HEIGHT

        r = int(lerp(SKY_TOP[0], SKY_BOTTOM[0], t))
        g = int(lerp(SKY_TOP[1], SKY_BOTTOM[1], t))
        b = int(lerp(SKY_TOP[2], SKY_BOTTOM[2], t))

        pygame.draw.line(
            surface,
            (r, g, b),
            (0, y),
            (WIDTH, y),
        )


def draw_cloud(surface, x, y, scale=1.0):
    pygame.draw.ellipse(
        surface,
        WHITE,
        (
            int(x),
            int(y),
            int(90 * scale),
            int(35 * scale),
        ),
    )
    pygame.draw.ellipse(
        surface,
        WHITE,
        (
            int(x + 25 * scale),
            int(y - 15 * scale),
            int(55 * scale),
            int(45 * scale),
        ),
    )
    pygame.draw.ellipse(
        surface,
        WHITE,
        (
            int(x + 52 * scale),
            int(y - 8 * scale),
            int(55 * scale),
            int(40 * scale),
        ),
    )


def draw_background(surface, scroll):
    draw_gradient(surface)

    # Sun.
    pygame.draw.circle(
        surface,
        (255, 235, 150),
        (850, 90),
        38,
    )

    # Clouds.
    for i in range(4):
        x = (i * 310 - scroll * 0.22) % (WIDTH + 180) - 100
        draw_cloud(surface, x, 90 + (i % 2) * 55, 0.9)

    # Distant hills.
    hill_scroll = scroll * 0.12

    for i in range(-1, 6):
        x = i * 230 - hill_scroll % 230

        pygame.draw.polygon(
            surface,
            (105, 155, 130),
            [
                (x, GROUND_Y),
                (x + 115, GROUND_Y - 135),
                (x + 230, GROUND_Y),
            ],
        )

    # Bamboo silhouettes.
    tree_scroll = scroll * 0.35

    for i in range(-1, 11):
        x = i * 110 - tree_scroll % 110

        pygame.draw.rect(
            surface,
            (74, 135, 83),
            (int(x), GROUND_Y - 80, 10, 80),
            border_radius=5,
        )

        pygame.draw.ellipse(
            surface,
            (74, 135, 83),
            (int(x - 25), GROUND_Y - 82, 38, 15),
        )

        pygame.draw.ellipse(
            surface,
            (74, 135, 83),
            (int(x + 5), GROUND_Y - 58, 38, 15),
        )

    # Ground.
    pygame.draw.rect(
        surface,
        (42, 45, 48),
        (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y),
    )

    pygame.draw.rect(
        surface,
        (90, 95, 100),
        (0, GROUND_Y, WIDTH, 5),
    )

    # Moving road markings.
    for i in range(-1, 25):
        x = (i * 70 - scroll * 2.3) % (WIDTH + 70) - 70

        pygame.draw.rect(
            surface,
            (195, 198, 200),
            (int(x), GROUND_Y + 35, 34, 4),
            2,
        )


# ============================================================
# UI HELPERS
# ============================================================

def draw_text(surface, text, font, position, color=WHITE, center=False):
    image = font.render(text, True, color)

    rect = image.get_rect()

    if center:
        rect.center = position
    else:
        rect.topleft = position

    surface.blit(image, rect)


def draw_panel(surface, rect, alpha=180):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill((18, 20, 24, alpha))
    pygame.draw.rect(
        panel,
        (255, 255, 255, 25),
        panel.get_rect(),
        1,
        border_radius=16,
    )
    surface.blit(panel, rect.topleft)


# ============================================================
# MAIN GAME
# ============================================================

def main():
    try:
        webcam = WebcamControl()
        webcam.start()
        webcam_active = True
        print("✅ WEBCAM ACTIVE! (OpenCV motion tracking)")
        print("👋 WAVE LEFT-RIGHT TO START!\n")
    except Exception as exc:
        print("Webcam unavailable:", exc)
        webcam = None
        webcam_active = False

    panda = Panda()

    obstacles = []
    coins = []

    running = True
    game_over = False

    score = 0.0
    coins_collected = 0
    high_score = 0

    spawn_timer = 0.0
    next_spawn = 1.5

    game_time = 0.0
    scroll = 0.0

    countdown = 0.0
    started_last_frame = False

    # Keyboard is kept as a development/testing fallback.
    keyboard_mode = False

    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.033)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_F1:
                    keyboard_mode = not keyboard_mode
                    print(f"Keyboard mode: {'ON' if keyboard_mode else 'OFF'}")

                if event.key == pygame.K_SPACE:
                    panda.jump()

                if event.key == pygame.K_DOWN:
                    panda.duck()

                if event.key == pygame.K_LEFT:
                    panda.move_left()

                if event.key == pygame.K_RIGHT:
                    panda.move_right()

                if event.key == pygame.K_r and game_over:
                    panda = Panda()
                    obstacles.clear()
                    coins.clear()

                    score = 0
                    coins_collected = 0

                    spawn_timer = 0
                    next_spawn = 1.5

                    game_time = 0
                    countdown = 0

                    game_over = False
                    started_last_frame = False

                    if webcam:
                        webcam.reset_start()

        # ----------------------------------------
        # Start state
        # ----------------------------------------
        webcam_started = webcam.is_game_started() if webcam else False

        if keyboard_mode:
            game_started = True
        else:
            game_started = webcam_started if webcam else False

        if game_started and not started_last_frame:
            countdown = 2.0
            started_last_frame = True

        # ----------------------------------------
        # Countdown
        # ----------------------------------------
        if countdown > 0:
            countdown -= dt

        # ----------------------------------------
        # Gameplay
        # ----------------------------------------
        if game_started and countdown <= 0 and not game_over:
            game_time += dt

            # Difficulty increases gradually.
            world_speed = 260 + min(210, game_time * 3.2)

            scroll += world_speed * dt

            # Webcam controls.
            if not keyboard_mode and webcam:
                if webcam.get_event("left"):
                    panda.move_left()

                if webcam.get_event("right"):
                    panda.move_right()

                if webcam.get_event("jump"):
                    panda.jump()

                if webcam.get_event("duck"):
                    panda.duck()

            panda.update(dt)

            # Score is based on survival time.
            score = int(game_time * 10) + coins_collected * 25

            # Spawn.
            spawn_timer += dt

            if spawn_timer >= next_spawn:
                spawn_timer = 0

                lane = random.randrange(3)

                obstacles.append(
                    Obstacle(
                        lane,
                        world_speed,
                    )
                )

                if random.random() < 0.45:
                    coin_lane = random.randrange(3)

                    coins.append(
                        Coin(
                            coin_lane,
                            world_speed,
                        )
                    )

                # Faster game = slightly shorter spawn gap.
                next_spawn = random.uniform(
                    max(0.72, 1.35 - game_time * 0.006),
                    max(1.0, 1.8 - game_time * 0.004),
                )

            # Update obstacles.
            for obstacle in obstacles[:]:
                obstacle.speed = world_speed
                obstacle.update(dt)

                if obstacle.x + obstacle.w < -30:
                    obstacles.remove(obstacle)

            # Update coins.
            for coin in coins[:]:
                coin.speed = world_speed
                coin.update(dt)

                if coin.x < -40:
                    coins.remove(coin)

            panda_rect = panda.get_rect()

            # Collision.
            for obstacle in obstacles:
                if panda_rect.colliderect(obstacle.get_rect()):
                    game_over = True
                    panda.dead = True

                    high_score = max(high_score, score)
                    break

            # Coins.
            for coin in coins[:]:
                if panda_rect.colliderect(coin.get_rect()):
                    coins.remove(coin)
                    coins_collected += 1

        elif game_over:
            scroll += 30 * dt

        # ----------------------------------------
        # DRAW
        # ----------------------------------------
        draw_background(screen, scroll)

        for coin in coins:
            coin.draw(screen)

        for obstacle in obstacles:
            obstacle.draw(screen)

        panda.draw(screen)

        # Top HUD.
        draw_panel(
            screen,
            pygame.Rect(20, 18, WIDTH - 40, 68),
            120,
        )

        webcam_status = (
            "OPENCV MOTION TRACKING"
            if webcam_active and not keyboard_mode
            else "KEYBOARD TEST MODE"
        )

        status_color = GREEN if webcam_active else RED

        draw_text(
            screen,
            webcam_status,
            SMALL_FONT,
            (38, 31),
            status_color,
        )

        draw_text(
            screen,
            f"SCORE  {score:05.0f}",
            FONT,
            (WIDTH - 250, 25),
            WHITE,
        )

        draw_text(
            screen,
            f"BEST  {high_score:05.0f}",
            SMALL_FONT,
            (WIDTH - 245, 58),
            YELLOW,
        )

        draw_text(
            screen,
            f"COINS  {coins_collected:02d}",
            SMALL_FONT,
            (WIDTH - 130, 58),
            YELLOW,
        )

        # Lane indicator.
        lane_names = ("LEFT", "CENTER", "RIGHT")

        draw_text(
            screen,
            f"LANE: {lane_names[panda.lane]}",
            SMALL_FONT,
            (38, 60),
            LIGHT_GRAY,
        )

        # Start overlay.
        if not game_started and not game_over:
            draw_panel(
                screen,
                pygame.Rect(180, 155, WIDTH - 360, 260),
                205,
            )

            draw_text(
                screen,
                "PANDAVISION",
                TITLE_FONT,
                (WIDTH // 2, 205),
                WHITE,
                center=True,
            )

            draw_text(
                screen,
                "TOUCHLESS PANDA RUNNER",
                SMALL_FONT,
                (WIDTH // 2, 250),
                LIGHT_GRAY,
                center=True,
            )

            if webcam_active and not keyboard_mode:
                draw_text(
                    screen,
                    "WAVE LEFT → RIGHT TO START",
                    FONT,
                    (WIDTH // 2, 305),
                    YELLOW,
                    center=True,
                )

                draw_text(
                    screen,
                    "Move your body • jump • duck",
                    SMALL_FONT,
                    (WIDTH // 2, 345),
                    LIGHT_GRAY,
                    center=True,
                )

                draw_text(
                    screen,
                    "No keyboard required",
                    SMALL_FONT,
                    (WIDTH // 2, 380),
                    GREEN,
                    center=True,
                )
            else:
                draw_text(
                    screen,
                    "PRESS F1 FOR KEYBOARD TEST MODE",
                    FONT,
                    (WIDTH // 2, 315),
                    YELLOW,
                    center=True,
                )

        # Countdown.
        if game_started and countdown > 0 and not game_over:
            value = max(1, int(math.ceil(countdown)))

            draw_panel(
                screen,
                pygame.Rect(360, 190, 280, 150),
                190,
            )

            draw_text(
                screen,
                str(value),
                BIG_FONT,
                (WIDTH // 2, 255),
                YELLOW,
                center=True,
            )

        # Game over.
        if game_over:
            draw_panel(
                screen,
                pygame.Rect(250, 155, 500, 280),
                220,
            )

            draw_text(
                screen,
                "GAME OVER",
                BIG_FONT,
                (WIDTH // 2, 215),
                RED,
                center=True,
            )

            draw_text(
                screen,
                f"SCORE  {score:05.0f}",
                FONT,
                (WIDTH // 2, 285),
                WHITE,
                center=True,
            )

            draw_text(
                screen,
                f"COINS  {coins_collected:02d}",
                SMALL_FONT,
                (WIDTH // 2, 325),
                YELLOW,
                center=True,
            )

            draw_text(
                screen,
                "PRESS R TO RUN AGAIN",
                FONT,
                (WIDTH // 2, 375),
                GREEN,
                center=True,
            )

        # Bottom controls.
        if game_started and not game_over:
            draw_text(
                screen,
                "← → MOVE     ↑ JUMP     ↓ DUCK",
                SMALL_FONT,
                (WIDTH // 2, HEIGHT - 28),
                LIGHT_GRAY,
                center=True,
            )

        pygame.display.flip()

    if webcam:
        webcam.stop()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()