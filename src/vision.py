import cv2
import threading
import numpy as np
import os
import sys

try:
    import mediapipe as mp
    from mediapipe.tasks.python import BaseOptions
    from mediapipe.tasks.python.vision import (
        HandLandmarker,
        HandLandmarkerOptions,
        HandLandmarkerResult,
        HandLandmarksConnections,
        RunningMode,
    )
    from mediapipe.tasks.python.vision import drawing_utils as mp_draw
    _MP_AVAILABLE = True
except ImportError:
    print("MediaPipe not installed. Please run: pip install mediapipe")
    _MP_AVAILABLE = False
except Exception as e:
    print(f"MediaPipe Import Error: {e}")
    _MP_AVAILABLE = False

# Add project root to path to import from src
base_path = os.path.dirname(os.path.abspath(__file__))
if base_path not in sys.path:
    sys.path.append(os.path.join(base_path, '..'))

from src.cv.predict_act import predict_action

# Path to the hand landmarker model
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'hand_landmarker.task')

class VisionSystem:
    def __init__(self):
        if not _MP_AVAILABLE:
            raise ImportError("MediaPipe not available")

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Hand landmarker model not found at {MODEL_PATH}. "
                "Download it from: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
            )

        try:
            options = HandLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=MODEL_PATH),
                running_mode=RunningMode.IMAGE,
                num_hands=1,
                min_hand_detection_confidence=0.7,
                min_tracking_confidence=0.5,
            )
            self.hand_landmarker = HandLandmarker.create_from_options(options)
        except Exception as e:
            print(f"MediaPipe HandLandmarker failed: {e}")
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

            # Convert to MediaPipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            results: HandLandmarkerResult = self.hand_landmarker.detect(mp_image)
            
            if results.hand_landmarks:
                for hand_lms in results.hand_landmarks:
                    # Index finger tip (ID 8)
                    index_tip = hand_lms[8]
                    cx, cy = int(index_tip.x * self.w), int(index_tip.y * self.h)
                    
                    # Middle finger tip (ID 12)
                    middle_tip = hand_lms[12]
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
                    
                    # Draw hand landmarks on frame manually
                    for connection in HandLandmarksConnections.HAND_CONNECTIONS:
                        start_lm = hand_lms[connection.start]
                        end_lm = hand_lms[connection.end]
                        sx, sy = int(start_lm.x * self.w), int(start_lm.y * self.h)
                        ex, ey = int(end_lm.x * self.w), int(end_lm.y * self.h)
                        cv2.line(frame, (sx, sy), (ex, ey), (0, 255, 0), 2)
                    for lm in hand_lms:
                        px, py = int(lm.x * self.w), int(lm.y * self.h)
                        cv2.circle(frame, (px, py), 4, (0, 0, 255), -1)
            
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

            spell, debug_img, raw_pred = predict_action(roi)
            
            # Show debug window with preprocessed image (scaled up for visibility)
            debug_display = cv2.resize(debug_img, (140, 140), interpolation=cv2.INTER_NEAREST)
            cv2.imshow("Debug - Preprocessed ROI (28x28)", debug_display)
            
            if spell is not None:
                self.current_gesture = spell
                print(f"\n==============================")
                print(f"SPELL DETECTED: {spell} (raw class: {raw_pred})")
                print(f"==============================\n")
            else:
                print(f"Unknown class: {raw_pred}, ignoring.")
                
        except Exception as e:
            print(f"Prediction Error: {e}")

    def get_gesture(self):
        g = self.current_gesture
        self.current_gesture = None
        return g

    def clear_gesture(self):
        """Reset internal state to prevent ghost skill casting."""
        self.current_gesture = None
        self.drawing_points = []
        self.is_drawing = False
        if hasattr(self, 'canvas'):
            self.canvas.fill(0)
        print("VisionSystem: Gesture buffer cleared.")

    def stop(self):
        self.running = False
        self.hand_landmarker.close()
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    v = VisionSystem()
    try:
        while v.running:
            pass
    except KeyboardInterrupt:
        v.stop()
