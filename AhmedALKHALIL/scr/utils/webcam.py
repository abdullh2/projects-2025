import cv2
from deepface import DeepFace

def start_emotion_recognition():
    # This OpenCV function opens the webcam (0 is the index for the first camera)
    cap = cv2.VideoCapture(0)
    print("🎥 Press 'q' to quit")

    # to keep the camera running and taking frames
    while True:
        # read a frame from the webcam
        ret, frame = cap.read()
        if not ret:
            break

        # here it will read the frame with the deepface library and analyze it to recognize the emotion
        try:
            result = DeepFace.analyze(
                img_path=frame,
                actions=["emotion"],
                enforce_detection=False  # this prevents the code from raising up an error if t here's no face detected
            )
            emotion = result[0]['dominant_emotion']
        except:
            emotion = "No face"

        # to write the expression detected on the displayed frame
        cv2.putText(
            frame,
            f'Emotion: {emotion}',
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,  # green color font
            (0, 255, 0),  # Green text
            2
        )

        # define the display window name, and send the frame captured to the display function
        cv2.imshow("Facial Emotion Recognition - Press q to exit", frame)

        # allows the user to close the displaying window when he presses Q
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
