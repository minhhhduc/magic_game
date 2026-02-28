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
    _MP_AVAILABLE = True
except ImportError:
    print("MediaPipe not installed. Please run: pip install mediapipe")
    _MP_AVAILABLE = False
except Exception as e:
    print(f"MediaPipe Import Error: {e}")
    _MP_AVAILABLE = False

from config.iconfig import MODEL_PATH
from config.settings import TURN_PREDICT_CONSOLE
from vision.cv.predict_act import predict_action

# Add project root to path to import from src
base_path = os.path.dirname(os.path.abspath(__file__))
if os.path.join(base_path, '..') not in sys.path:
    sys.path.append(os.path.join(base_path, '..'))

class VisionSystem:
    def __init__(self):
        if not _MP_AVAILABLE:
            raise ImportError("MediaPipe not available")

        # Basic state
        self.lock = threading.Lock()
        self.h, self.w = 480, 640  # Default until camera starts
        self.canvas = np.zeros((self.h, self.w), dtype=np.uint8)
        self._current_gesture = None
        self.drawing_points = []
        self.is_drawing = False
        self.current_frame = None
        self.debug_roi = None  # Add this
        self.running = True
        
        # Start initialization thread
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        import traceback
        try:
            # 1. Threaded Initialization
            if not os.path.exists(MODEL_PATH):
                print(f"Error: Model not found at {MODEL_PATH}")
                self.running = False
                return

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
                self.running = False
                return

            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.h, self.w, _ = frame.shape
                    with self.lock:
                        self.canvas = np.zeros((self.h, self.w), dtype=np.uint8)
            else:
                print("Error: Could not open camera.")
                self.running = False
                return

            # 2. Main Loop
            while self.running:
                success, frame = self.cap.read()
                if not success or frame is None:
                    continue
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert to MediaPipe Image
                if not self.running or not hasattr(self, 'hand_landmarker'):
                    continue

                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                
                try:
                    results: HandLandmarkerResult = self.hand_landmarker.detect(mp_image)
                except Exception as e:
                    if "not running" in str(e):
                        continue
                    raise e
                
                with self.lock:
                    if results.hand_landmarks:
                        for hand_lms in results.hand_landmarks:
                            # Index finger tip (ID 8)
                            index_tip = hand_lms[8]
                            cx, cy = int(index_tip.x * self.w), int(index_tip.y * self.h)
                            
                            # Middle finger tip (ID 12)
                            middle_tip = hand_lms[12]
                            mx, my = int(middle_tip.x * self.w), int(middle_tip.y * self.h)
                            
                            # Distance between Index and Middle tips
                            distance = float(np.sqrt((cx-mx)**2 + (cy-my)**2))
                            
                            # If pinched (Index and Middle touch), STOP drawing and PREDICT
                            if distance < 40:
                                if self.is_drawing:
                                    if TURN_PREDICT_CONSOLE: print("Stop Drawing - Predicting...")
                                    self._classify_gesture_locked()
                                    self.is_drawing = False
                                    self.drawing_points = []
                                    self.canvas.fill(0)
                            else:
                                # Otherwise, Draw with Index finger
                                self.is_drawing = True
                                if len(self.drawing_points) > 0:
                                    last_pt = self.drawing_points[-1]
                                    dist_move = np.sqrt((cx-last_pt[0])**2 + (cy-last_pt[1])**2)
                                    if dist_move < 100:
                                        cv2.line(self.canvas, last_pt, (cx, cy), 255, 15)
                                self.drawing_points.append((cx, cy))
                            
                            # Draw hand landmarks
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
                    
                    # Update current frame for main thread to use
                    self.current_frame = frame

                # DO NOT use cv2.imshow/waitKey in a background thread on Windows.
            
        except Exception as e:
            print(f"VisionSystem Thread Error: {e}")
            traceback.print_exc()
        finally:
            self.running = False
            if hasattr(self, 'hand_landmarker'):
                try:
                    self.hand_landmarker.close()
                except:
                    pass
            if hasattr(self, 'cap'):
                self.cap.release()
            print("VisionSystem: Background thread stopped.")

    def _classify_gesture_locked(self):
        """Called inside lock."""
        if len(self.drawing_points) < 5:  # Slightly more lenient
            return

        try:
            # We use the canvas to get the bounding box of what was drawn
            pts = np.array(self.drawing_points)
            x, y, w, h = cv2.boundingRect(pts)
            
            # Add a small pad around the drawing to capture full strokes
            pad = 20
            # Clip to canvas boundaries
            y1, y2 = max(0, y-pad), min(self.h, y+h+pad)
            x1, x2 = max(0, x-pad), min(self.w, x+w+pad)
            
            # Crop the canvas (white drawing on black background)
            roi = self.canvas[y1:y2, x1:x2].copy()
            
            # If the ROI is valid, predict the gesture
            if roi.size > 0:
                spell, debug_img, raw_pred = predict_action(roi)
                
                # Update debug visualization (upscale for clearer window)
                self.debug_roi = cv2.resize(debug_img, (140, 140), interpolation=cv2.INTER_NEAREST)
                
                if spell is not None:
                    self._current_gesture = spell
                    if TURN_PREDICT_CONSOLE: print(f"SPELL DETECTED: {spell}")
                
        except Exception as e:
            print(f"Prediction Error: {e}")

    def get_gesture(self):
        with self.lock:
            g = self._current_gesture
            self._current_gesture = None
            return g

    def clear_gesture(self):
        with self.lock:
            self._current_gesture = None
            self.drawing_points = []
            self.is_drawing = False
            if hasattr(self, 'canvas'):
                self.canvas.fill(0)
        print("VisionSystem: Gesture buffer cleared.")

    def stop(self):
        self.running = False
        if hasattr(self, 'hand_landmarker'):
            try:
                self.hand_landmarker.close()
            except:
                pass
        if hasattr(self, 'cap'):
            self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    v = VisionSystem()
    try:
        while v.running:
            if v.current_frame is not None:
                cv2.imshow("Vision - Camera", v.current_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        v.stop()
