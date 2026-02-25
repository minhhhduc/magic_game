import cv2
import threading
import numpy as np
import os
import sys

# Try multiple import styles for mediapipe to ensure compatibility
try:
    import mediapipe as mp
    # Robustly find solutions if standard import fails
    try:
        from mediapipe.solutions import hands as mp_hands
        from mediapipe.solutions import drawing_utils as mp_draw
    except ImportError:
        # Some versions (0.10.x) hide solutions inside python/solutions
        mp_path = os.path.dirname(mp.__file__)
        python_path = os.path.join(mp_path, 'python')
        if python_path not in sys.path:
            sys.path.append(python_path)
        import solutions.hands as mp_hands
        import solutions.drawing_utils as mp_draw
except Exception as e:
    print(f"MediaPipe Import Critical Error: {e}")
    # Fallback to allow game to start in keyboard mode
    mp_hands = None
    mp_draw = None

# Add project root to path to import from src
base_path = os.path.dirname(os.path.abspath(__file__))
if base_path not in sys.path:
    sys.path.append(os.path.join(base_path, '..'))

from src.cv.predict_act import predict_action

class VisionSystem:
    def __init__(self):
        if mp_hands is None:
            raise ImportError("MediaPipe not available")
            
        try:
            self.hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            self.mp_draw = mp_draw
        except Exception as e:
            print(f"MediaPipe hands failed: {e}")
            raise e

        self.cap = cv2.VideoCapture(0)
        
        # Canvas for drawing
        ret, frame = self.cap.read()
        if ret:
            self.h, self.w, _ = frame.shape
        else:
            self.h, self.w = 480, 640
            
        self.canvas = np.zeros((self.h, self.w), dtype=np.uint8)
        
        self.current_gesture: str | None = None
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
                    cx, cy = int(index_tip.x * self.w), int(index_tip.y * self.h)
                    
                    # Middle finger tip (ID 12)
                    middle_tip = hand_lms.landmark[12]
                    mx, my = int(middle_tip.x * self.w), int(middle_tip.y * self.h)
                    
                    # Distance between Index and Middle tips
                    distance = np.sqrt((cx-mx)**2 + (cy-my)**2)
                    
                    # If pinched (Index and Middle touch), STOP drawing and PREDICT
                    if distance < 40:
                        if self.is_drawing:
                            print("Stop Drawing - Predicting...")
                            self._classify_gesture()
                            self.is_drawing = False
                            self.drawing_points = []
                            self.canvas.fill(0)
                    else:
                        # Otherwise, Draw with Index finger
                        self.is_drawing = True
                        if len(self.drawing_points) > 0:
                            last_pt = self.drawing_points[-1]
                            # Simple distance check to prevent huge lines if hand jumps
                            dist_move = np.sqrt((cx-last_pt[0])**2 + (cy-last_pt[1])**2)
                            if dist_move < 100:
                                cv2.line(self.canvas, last_pt, (cx, cy), 255, 15)
                        self.drawing_points.append((cx, cy))
                    
                    if self.mp_draw and mp_hands:
                        self.mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
            
            # Overlay drawing on frame
            drawing_mask = self.canvas > 0
            frame[drawing_mask] = [0, 255, 150] # Neon green trail

            # Show windows
            cv2.imshow("Vision - Camera", frame)
            cv2.imshow("Vision - Canvas (What you draw)", self.canvas)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break

    def _classify_gesture(self):
        if len(self.drawing_points) < 10: # Minimum points to consider a drawing
            return

        try:
            # Crop the drawing area to handle better scale
            pts = np.array(self.drawing_points)
            x, y, w, h = cv2.boundingRect(pts)
            
            # Add some padding
            pad = 40
            y1, y2 = max(0, y-pad), min(self.h, y+h+pad)
            x1, x2 = max(0, x-pad), min(self.w, x+w+pad)
            
            roi = self.canvas[y1:y2, x1:x2]
            if roi.size == 0:
                roi = self.canvas

            pred = predict_action(roi)
            
            # Normalize common symbols to match game expectations
            if pred in ["O", "o", "0", "@", "4"]:
                self.current_gesture = "O"
            elif pred in ["/", "7", "1"]:
                self.current_gesture = "/"
            elif pred in ["\\", "L", "l", "backslash", "2"]:
                self.current_gesture = "\\"
            elif pred in ["|", "I", "3"]:
                self.current_gesture = "|"
            else:
                self.current_gesture = pred
            
            print(f"\n==============================")
            print(f"🪄  SPELL DETECTED: {self.current_gesture}")
            print(f"==============================\n")
                
        except Exception as e:
            print(f"Prediction Error: {e}")

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
