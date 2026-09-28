from time import perf_counter, sleep
import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from flask import Flask, render_template, Response, jsonify
import threading

app = Flask(__name__)

# Binary tree representation of Morse code
letters = ['', 'E', 'T', 'I', 'A', 'N', 'M', 'S', 'U', 'R', 'W', 'D', 'K', 'G', 'O', 'H', 'V', 'F', '', 'L', '', 'P',
           'J', 'B', 'X', 'C', 'Y', 'Z', 'Q', '', '']


def choose_letter(dots):
    if len(dots) > 4:
        return 'TOO BIG'
    trace = 1
    for dot in dots:
        if dot == 0:
            trace = 2 * trace
        else:
            trace = (2 * trace) + 1
    return letters[int(trace - 1)]


# Global state
start_flag = False
is_paused = False
letter = []
word = ''
morse = ''
startTime = 0
notBlinking = 0
blinking = 0

dList = []
horList = []
r_list = []
avg_d = []

# Thread lock for camera access
camera_lock = threading.Lock()


# Initialize camera
def initialize_camera():
    for index in range(10):
        try:
            cap = cv2.VideoCapture(index)
            cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            # Give camera time to initialize
            sleep(0.5)

            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    print(f"✅ Camera opened at index {index}")
                    return cap
                cap.release()
        except Exception as e:
            print(f"Camera {index} error: {e}")
            continue

    raise RuntimeError("No working camera found")


try:
    video = initialize_camera()
    sleep(1)  # Extra initialization time
    detector = FaceMeshDetector(maxFaces=1)
except RuntimeError as e:
    print(f"❌ {e}")
    video = None
    detector = None


# Routes
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/morse', strict_slashes=False)
def morse_interface():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def start_detection():
    global start_flag
    start_flag = True
    return jsonify({'status': 'started'})


@app.route('/reset', methods=['POST'])
def reset_detection():
    global letter, word, morse, start_flag, is_paused
    letter = []
    word = ''
    morse = ''
    start_flag = False
    is_paused = False
    return jsonify({'status': 'reset'})


@app.route('/toggle_pause', methods=['POST'])
def toggle_pause():
    global is_paused
    is_paused = not is_paused
    return jsonify({'paused': is_paused})


@app.route('/status')
def get_status():
    return jsonify({
        'word': word,
        'morse': morse,
        'active': start_flag,
        'paused': is_paused
    })


# Video streaming
def gen_frames():
    global start_flag, letter, word, morse, startTime, notBlinking, blinking
    global dList, horList, r_list, avg_d, is_paused

    if not video or not detector:
        print("❌ Camera or detector not initialized")
        return

    frame_skip_count = 0

    while True:
        try:
            with camera_lock:
                success, img = video.read()

            # Validate frame
            if not success or img is None or img.size == 0:
                frame_skip_count += 1
                if frame_skip_count > 10:
                    print("❌ Camera disconnected, attempting restart...")
                    frame_skip_count = 0
                continue

            frame_skip_count = 0

            # Flip horizontally for mirror effect
            img = cv2.flip(img, 1)

            img, faces = detector.findFaceMesh(img, draw=False)

            if faces and start_flag:
                face = faces[0]

                # Get eye landmarks
                leftUp = face[159]
                leftDown = face[23]
                leftLeft = face[130]
                leftRight = face[243]
                rightUp = face[386]
                rightDown = face[374]
                rightLeft = face[398]
                rightRight = face[359]

                # Calculate distances
                distanceVert, _ = detector.findDistance(leftUp, leftDown)
                distanceHor, _ = detector.findDistance(leftLeft, leftRight)
                distanceVertR, _ = detector.findDistance(rightUp, rightDown)
                distanceHorR, _ = detector.findDistance(rightLeft, rightRight)

                if not is_paused:
                    # Average horizontal distance
                    horList.append((distanceHor + distanceHorR) / 2)
                    if len(horList) > 1:
                        horList.pop(0)
                    distanceHor = sum(horList) / len(horList)

                    # Average vertical distance
                    dList.append((distanceVert + distanceVertR) / 2)
                    if len(dList) > 2:
                        dList.pop(0)
                    distanceVert = sum(dList) / len(dList)

                    # Compute ratio
                    ratio = (distanceVert / distanceHor) * 100
                    r_list.append(ratio)
                    if len(r_list) > 2:
                        r_list.pop(0)
                    ratio = sum(r_list) / len(r_list)

                    # Running average
                    avg_d.append(ratio)
                    if len(avg_d) > 200:
                        avg_d.pop(0)
                    avg_ratio = sum(avg_d) / len(avg_d)

                    # Blink detection
                    if avg_ratio - ratio > 3:
                        if blinking == 0:
                            startTime = perf_counter()
                            blinking = 1
                    else:
                        if blinking == 1:
                            howLong = perf_counter() - startTime
                            notBlinking = perf_counter()
                            if howLong < 0.28:  # Short blink = dot
                                letter.append(0)
                                morse += '.'
                            elif howLong < 2:  # Long blink = dash
                                letter.append(1)
                                morse += '_'

                        # Decode letter after 1 second of no blink
                        if perf_counter() - notBlinking >= 1:
                            if len(letter) < 5:
                                decoded = choose_letter(letter)
                                word += decoded
                            letter = []
                            morse = ''
                        blinking = 0

                # Show pause indicator
                if is_paused:
                    cvzone.putTextRect(img, "PAUSED", (50, 100),
                                       colorR=(0, 0, 255), scale=2, thickness=2)

            ret, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ret:
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        except Exception as e:
            print(f"Frame processing error: {e}")
            continue


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)