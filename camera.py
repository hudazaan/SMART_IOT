from iot_control import IOTConnection
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HandTracker(IOTConnection):

    def __init__(self, mode=False, max_hands=2, detection_con=0.5, model_complexity=1, track_con=0.5):
        super().__init__()          # parent's init 
        self.mode = mode            # variables 
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.model_complexity = model_complexity
        self.track_con = track_con

        base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO if not mode else vision.RunningMode.IMAGE,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )
        self.hands = vision.HandLandmarker.create_from_options(options)
        
        self.command = None
        self.prev_command = None
        self.results = None
        self.frame_timestamp = 0

        self.hand_connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),             # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),             # Index
            (5, 9), (9, 10), (10, 11), (11, 12),        # Middle
            (9, 13), (13, 14), (14, 15), (15, 16),      # Ring
            (13, 17), (17, 18), (18, 19), (19, 20),     # Pinky
            (0, 17)                                     # Palm
        ]


    def _hand_finder(self, image, draw=True):
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)                      # Process frame with timestamp for VIDEO mode
        self.results = self.hands.detect_for_video(mp_image, self.frame_timestamp)
        self.frame_timestamp += 1

        if self.results.hand_landmarks:
            for hand_landmarks in self.results.hand_landmarks:
                if draw:
                    h, w, _ = image.shape                                                        # Draw landmarks and connections manually
                    
                    for connection in self.hand_connections:                                     # Draw connections
                        start_idx, end_idx = connection
                        start = hand_landmarks[start_idx]
                        end = hand_landmarks[end_idx]
                        
                        start_point = (int(start.x * w), int(start.y * h))
                        end_point = (int(end.x * w), int(end.y * h))
                        
                        cv2.line(image, start_point, end_point, (0, 255, 0), 2)
                    
                    for landmark in hand_landmarks:                                              # Draw landmarks
                        cx, cy = int(landmark.x * w), int(landmark.y * h)
                        cv2.circle(image, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        
        return image


    def _position_finder(self, image, hand_no=0, draw=True):
        self.lm_list = []
        if self.results.hand_landmarks:
            if hand_no < len(self.results.hand_landmarks):
                hand = self.results.hand_landmarks[hand_no]
                h, w, _ = image.shape
                
                for id, lm in enumerate(hand):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.lm_list.append([id, cx, cy])
                    
                    if id == 0 and draw:
                        cv2.circle(image, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
                

    def _finger_down(self, fingers=[]):
        """
        Returns True if fingers are down relative to the palm [0]
        """
        heights = []
        for finger in fingers:
            if finger == 4:
                heights.append(True if abs(self.lm_list[finger][2] - self.lm_list[0][2]) < 100 else False)
            else:
                heights.append(True if abs(self.lm_list[finger][2] - self.lm_list[0][2]) < 90 else False)

        return heights
    

    def _gesture_command(self):
        """
        Gets the command from the position of tips relative to 0.
        Relate to README file for command ilustration.
        """
        if self.lm_list:
            # Turn Bedroom light on (index finger only)
            if abs(self.lm_list[8][2] - self.lm_list[0][2]) >= 150:
                h = self._finger_down(fingers=[20, 16, 12, 4])
                if len(set(h)) == 1 and h[0] == True:
                    self.command = "BL1"                                     #print("Bedroom Light ON")

            # Turn Bedroom light off (all fingers down)
            if len(set(self._finger_down(fingers=[4, 8, 12, 16, 20]))) == 1 and self._finger_down(fingers=[4, 12, 16, 20])[0] == True:
                self.command = "BL0"                                          #print("Bedroom Light OFF")

            # turn garage light on ("2" with index and middle)
            if abs(self.lm_list[12][2] - self.lm_list[0][2]) >= 200:
                h = self._finger_down(fingers=[20, 16, 4])
                if len(set(h)) == 1 and h[0] == True:
                    self.command = "GL1"                                      #print("Garage Light ON")

            # turn garage light off (only pinky)
            if abs(self.lm_list[20][2] - self.lm_list[0][2]) >= 135:
                h = self._finger_down(fingers=[8, 16, 12, 4])
                if len(set(h)) == 1 and h[0] == True:  
                    self.command = "GL0"                                      #print("Garage Light OFF")

            # clockwise servo (garage door open) (spiderman hand)
            if abs(self.lm_list[8][2] - self.lm_list[0][2]) >= 150 and abs(self.lm_list[20][2] - self.lm_list[0][2]) >= 135:
                h = self._finger_down(fingers=[12, 16])
                if len(set(h)) == 1 and h[0] == True:
                    self.command = "GD1"                                      #print("Garage Door Open")
            
            # anticlockwise servo (garage door close) (only thumb)
            if abs(self.lm_list[4][2] - self.lm_list[0][2]) >= 100:
                h = self._finger_down(fingers=[12, 16])
                if len(set(h)) == 1 and h[0] == True:
                    self.command = "GD0"                                      #print("Garage Door Close")

            if self.command != self.prev_command:                             # check if command is not repeated
                self.prev_command = self.command
                print(self.command)                                           # send command here
                self._send_to_topic(self.command)                           # send message to broker 

    
    def main(self, show=True):
        """
        Main command that runs the class and tracks hands with 
        helper methods.
        """
        cap = cv2.VideoCapture(0)

        while True:
            success, frame = cap.read()
            if not success:
                break
            frame = self._hand_finder(frame)                                              # detect & draw landmarks
            self._position_finder(frame)                                                  # update landmark list 
            self._gesture_command()                                                       # print command if detected    

            if show:                                                                      # show if true
                cv2.imshow("Hand Tracking", frame) 
            if cv2.waitKey(1) & 0xFF == ord('q'):                                         # close when pressed q
                break


        # destroy windows
        cap.release()
        cv2.destroyAllWindows()
        

if __name__ == "__main__":
    tracker = HandTracker()
    tracker.main()