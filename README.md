# IRIS — Computer Vision Assistive Communication System

IRIS is an assistive communication prototype that uses real-time computer vision and eye-blink detection to convert intentional blink patterns into Morse code and decoded text.

The project explores how common camera-enabled devices can provide an alternative communication interface for users with limited motor control.

## Live Demo

Try the interactive IRIS blink-to-Morse simulation:

**(https://maximilian0817.github.io/IRIS-Assistive-Communication/)**

The simulation includes:

- Interactive blink-duration testing
- A–Z Morse alphabet guide
- Blink instructions for every letter
- Automatic SOS, HELLO, and IRIS demonstrations
- Morse decoding visualization
- Timing-boundary testing

## How IRIS Works

IRIS processes a camera feed and tracks facial landmarks around the user's eyes.

Intentional eye closures are measured by duration and converted into Morse symbols:

**Quick blink (< 0.28 seconds) → Dot `.`**

**Long blink (0.28–<2.00 seconds) → Dash `-`**

After approximately one second without another blink, IRIS interprets the Morse sequence as a completed letter.

For example:

```text
A = .-
Quick blink → Long blink

B = -...
Long blink → Quick → Quick → Quick

C = -.-.
Long → Quick → Long → Quick

D = -..
Long → Quick → Quick
```

## Technology Stack

**Python** — Core application logic  
**OpenCV** — Camera capture and image processing  
**MediaPipe / cvzone** — Facial landmark and eye tracking  
**Flask** — Backend and web application  
**NumPy** — Numerical processing  
**HTML / CSS / JavaScript** — User interface and interactive simulation

## System Architecture

```text
Camera Input
     ↓
Facial Landmark Detection
     ↓
Eye / Blink Detection
     ↓
Blink Duration Measurement
     ↓
Dot / Dash Classification
     ↓
Morse Sequence
     ↓
Character Decoder
     ↓
Text Output
```

## Interactive Simulation

The GitHub Pages simulation reproduces the Morse decoding logic without requiring a webcam or Python backend.

Users can select any letter from A–Z and see exactly how the letter should be performed using short and long blinks.

Example:

```text
S = ...
Quick → Quick → Quick

O = ---
Long → Long → Long

SOS = ... --- ...
```

## Simulation Testing

The decoding logic was tested using complete words and threshold boundary cases.

```text
SOS   → SOS
HELLO → HELLO
IRIS  → IRIS
TEST  → TEST
```

Timing boundary tests include:

```text
0.27 s → Dot
0.28 s → Dash
1.99 s → Dash
2.00 s → Ignored
```

## Web Interface

The Flask application includes:

- Live camera stream
- Current Morse sequence
- Decoded text output
- Start detection control
- Pause / Resume control
- Decoder reset
- A–Z Morse reference dictionary

## Project Structure

```text
IRIS-Assistive-Communication/
│
├── index.html
├── app.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── home.html
│   ├── index.html
│   └── base.html
│
├── simulation/
│   ├── iris_simulator.py
│   └── simulation_results.csv
│
└── docs/
    └── IRIS_Project_Report.docx
```

## Running the Computer Vision Application

Clone the repository:

```bash
git clone https://github.com/YOURUSERNAME/IRIS-Assistive-Communication.git
```

Move into the project directory:

```bash
cd IRIS-Assistive-Communication
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the Flask application:

```bash
python app.py
```

Then open the local address displayed by Flask in your browser.

A webcam is required for the computer-vision implementation.

## Motivation

IRIS was created to explore accessible human-computer interaction for individuals who may have limited conventional input options.

Instead of requiring specialized hardware, the prototype investigates whether standard cameras and computer vision can recognize intentional eye movements and translate them into digital communication.

## Current Limitations

The current prototype uses fixed timing thresholds for blink classification. Performance may vary based on lighting, camera position, user blink patterns, glasses, facial orientation, and involuntary blinking.

The browser simulation validates the timing and Morse-decoding logic but does not measure the accuracy of real-world facial landmark detection.

## Future Improvements

Future development could include:

- Personalized blink calibration
- Natural-blink filtering
- Adaptive timing thresholds
- Text-to-speech output
- Word prediction and autocomplete
- Faster communication methods
- Improved accessibility controls
- Mobile deployment
- More extensive real-user testing

## Author

Developed as a computer vision and assistive-technology project exploring accessible human-computer interaction.
