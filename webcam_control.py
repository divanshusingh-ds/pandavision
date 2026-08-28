import cv2
import threading

class WebcamControl:
    def __init__(self):
        print("📷 Opening webcam...")
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Webcam not found!")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        print("✅ Webcam opened!")
        
        # Simple motion detection variables
        self.prev_frame = None
        self.motion_history = []
        
        self.jump = False
        self.duck = False
        self.left = False
        self.right = False
        self.running = True
        
        self.cooldown = 0
        self.thread = threading.Thread(target=self.run)
        self.lock = threading.Lock()
        self.started = False
        self.initialized = False
        
    def start(self):
        if not self.started:
            self.started = True
            self.thread.start()
            print("🎥 Webcam Thread Started!")
            self.initialized = True
        
    def run(self):
        print("📷 Webcam thread running (MediaPipe FREE!)")
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # Motion detection
            if self.prev_frame is not None:
                diff = cv2.absdiff(self.prev_frame, gray)
                thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                
                # Find contours (body movement)
                contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Track body position
                if contours:
                    # Largest contour = body
                    largest = max(contours, key=cv2.contourArea)
                    if cv2.contourArea(largest) > 2000:  # Minimum area
                        x, y, w, h = cv2.boundingRect(largest)
                        
                        # Body center
                        cx = x + w // 2
                        cy = y + h // 2
                        
                        # Store motion data
                        self.motion_history.append((cx, cy, w, h))
                        if len(self.motion_history) > 10:
                            self.motion_history.pop(0)
                        
                        # Detect movement patterns
                        if len(self.motion_history) > 5:
                            self.detect_movement()
                        
                        # Draw on frame
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, "🟢 BODY DETECTED!", (10, 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(frame, f"Area: {int(cv2.contourArea(largest))}", (10, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                else:
                    cv2.putText(frame, "🔴 NO MOTION!", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                cv2.putText(frame, "📷 Calibrating...", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            self.prev_frame = gray
            
            if self.cooldown > 0:
                self.cooldown -= 1
            
            cv2.imshow('Webcam - Motion Control', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
    
    def detect_movement(self):
        """Detect movement patterns from motion history"""
        if not self.motion_history or len(self.motion_history) < 5:
            return
        
        recent = self.motion_history[-5:]
        
        # Calculate center movement
        cx_vals = [m[0] for m in recent]
        cy_vals = [m[1] for m in recent]
        w_vals = [m[2] for m in recent]
        h_vals = [m[3] for m in recent]
        
        # Check for JUMP (box height increases - body stretches up)
        if max(h_vals) - min(h_vals) > 20 and self.cooldown == 0:
            with self.lock:
                self.jump = True
            self.cooldown = 10
            print("🦘 JUMP!")
        
        # Check for DUCK (box height decreases - body squats)
        elif min(h_vals) - max(h_vals) < -15 and self.cooldown == 0:
            with self.lock:
                self.duck = True
            self.cooldown = 10
            print("🦆 DUCK!")
        
        # Check for LEFT (box moves left)
        elif cx_vals[-1] - cx_vals[0] < -15 and self.cooldown == 0:
            with self.lock:
                self.left = True
            self.cooldown = 10
            print("⬅️ LEFT!")
        
        # Check for RIGHT (box moves right)
        elif cx_vals[-1] - cx_vals[0] > 15 and self.cooldown == 0:
            with self.lock:
                self.right = True
            self.cooldown = 10
            print("➡️ RIGHT!")
    
    def get_jump(self):
        with self.lock:
            if self.jump:
                self.jump = False
                return True
            return False
    
    def get_duck(self):
        with self.lock:
            if self.duck:
                self.duck = False
                return True
            return False
    
    def get_left(self):
        with self.lock:
            if self.left:
                self.left = False
                return True
            return False
    
    def get_right(self):
        with self.lock:
            if self.right:
                self.right = False
                return True
            return False
    
    def stop(self):
        self.running = False
        print("👋 Webcam Stopped!")