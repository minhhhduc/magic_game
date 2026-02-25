import cv2
import mediapipe as mp
import threading
import numpy as np

class VisionSystem:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)
        
        self.current_gesture = None
        self.drawing_points = []
        self.is_drawing = False
        self.running = True
        
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            success, frame = self.cap.read()
            if not success:
                continue
            
            # Flip frame for mirror effect
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                for hand_lms in results.multi_hand_landmarks:
                    # Index finger tip (ID 8)
                    index_tip = hand_lms.landmark[8]
                    h, w, c = frame.shape
                    cx, cy = int(index_tip.x * w), int(index_tip.y * h)
                    
                    # Detect if thumb and index are close (drawing mode)
                    thumb_tip = hand_lms.landmark[4]
                    tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
                    distance = np.sqrt((cx-tx)**2 + (cy-ty)**2)
                    
                    if distance < 40:
                        self.is_drawing = True
                        self.drawing_points.append((cx, cy))
                    else:
                        if self.is_drawing:
                            self._classify_gesture()
                            self.is_drawing = False
                            self.drawing_points = []
                    
                    self.mp_draw.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)
            
            # Draw trail
            for i in range(1, len(self.drawing_points)):
                cv2.line(frame, self.drawing_points[i-1], self.drawing_points[i], (0, 255, 150), 3)

            cv2.imshow("Vision - Magic Game", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break

    def _classify_gesture(self):
        if len(self.drawing_points) < 10:
            return

        # Simplified gesture classification based on start/end points and bounding box
        pts = np.array(self.drawing_points)
        x_min, y_min = np.min(pts, axis=0)
        x_max, y_max = np.max(pts, axis=0)
        dx = self.drawing_points[-1][0] - self.drawing_points[0][0]
        dy = self.drawing_points[-1][1] - self.drawing_points[0][1]
        
        width = x_max - x_min
        height = y_max - y_min
        
        # Recognize / (slant left-up to right-down or similar)
        if dy > 50 and dx > 50:
            self.current_gesture = "/"
        # Recognize \
        elif dy > 50 and dx < -50:
            self.current_gesture = "\\"
        # Recognize ^ (Peak)
        elif height > 50 and abs(dx) < 100:
            # Check if mid point is higher than start/end
            mid_pt = self.drawing_points[len(self.drawing_points)//2]
            if mid_pt[1] < self.drawing_points[0][1] - 30:
                self.current_gesture = "^"
        
        print(f"Detected Gesture: {self.current_gesture}")

    def get_gesture(self):
        g = self.current_gesture
        self.current_gesture = None
        return g

    def stop(self):
        self.running = False
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    v = VisionSystem()
    try:
        while v.running:
            pass
    except KeyboardInterrupt:
        v.stop()
