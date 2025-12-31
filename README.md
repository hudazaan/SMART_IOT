# Major League Hacking (MLH)- Global Hack Week: AI/ML (December'25) 
## Working Agenda: 
- SMART IoT - Hand Gesture Controlled IoT Simulation using MediaPipe and MQTT by Buly. 

A real-time hand gesture recognition system that controls IoT devices using computer vision and MQTT protocol. This project uses MediaPipe for hand tracking and allows you to control lights, garage doors, and other IoT devices with simple gestures.


## Features & Architecture 

- **Real-time Hand Gesture Recognition**: Uses MediaPipe hand landmarker for accurate hand tracking from webcam feed (refer to: https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)
- **Gesture Recognition**: Custom algorithm analyzes finger positions relative to palm
- **Command Generation**: Specific finger configurations map to device commands
- **ESP32 Simulation**: Compatible with Wokwi ESP32 simulator
- **IoT Integration**: MQTT protocol for seamless communication with IoT devices (commands published to MQTT broker) 
- **Device Control**: ESP32 subscribes to topic and executes commands to control different devices with distinct hand gestures 

**Architecture:** Camera Feed → MediaPipe → Hand Landmarks → Gesture Recognition → 
MQTT Publish → Broker → ESP32 Subscribe → Device Control


## Supported Gestures & Commands

 ☝️ | Index finger only -> `BL1` ( Turn Bedroom Light ON ) <br>
 ✊ | All fingers down -> `BL0` ( Turn Bedroom Light OFF ) <br>
 ✌️ | Index & Middle fingers -> `GL1` ( Turn Garage Light ON ) <br>
 🤙 | Pinky only -> `GL0` ( Turn Garage Light OFF ) <br>
 🤟 | Spiderman hand (Index, Pinky) -> `GD1` ( Open Garage Door ) <br>
 👍 | Thumb only -> `GD0` ( Close Garage Door ) <br> 


## Prerequisites

- Python 3.10+ 
- Webcam/Camera
- Internet connection (for MQTT broker)
- Working configuration for quick setup:           
   - python==3.10.8         
   - opencv-python==4.12.0.88
   - mediapipe==0.10.31
   - paho-mqtt==2.1.0


## Setup Guide 

```bash
git clone <url>            # clone this repo 
cd SMART_IoT
```

```bash
py -3.10 -m venv iot-env    # create and virtual environment
iot-env\Scripts\activate
```

```bash                   
pip install opencv-python  # install dependencies
pip install mediapipe
pip install paho-mqtt
```

This will download the `hand_landmarker.task` model file required for hand tracking: 
```bash
python download_model.py    # Download MediaPipe Model
```

## Usage

### Running the Hand Gesture Controller 
```bash
python camera.py
```
This will:
1. Open your webcam
2. Start detecting hand gestures
3. Display the hand tracking visualization
4. Send commands to the MQTT broker when gestures are detected
Press `q` to quit the application.

### Testing MQTT Communication
```bash
python subscriber.py    # Terminal 1- Start Subscriber 
python publisher.py     # Terminal 2- Start Publisher
```
The subscriber will receive messages published by the publisher or the gesture controller.

### ESP32 Integration
This project includes ESP32 support for controlling IoT devices. You can simulate the ESP32 using Wokwi:
**Wokwi Simulation Link:** [](https://wokwi.com/projects/451864629933455361) 

Steps: 
1. Open the Wokwi project link above (or simulate your own)
2. The ESP32 will subscribe to the MQTT topic `home/central`
3. Run `camera.py` on your computer
4. Perform hand gestures to control the simulated devices 

### MQTT Broker Settings
Default configuration uses HiveMQ public broker:
- Broker: `broker.hivemq.com`
- Port: `1883`
- Topic: `home/central`
To change the broker or topic, modify the constants in `iot_control.py`

### Issues
- Ensure good lighting conditions
- Keep hand within camera frame
- Try adjusting `detection_con` and `track_con` value


