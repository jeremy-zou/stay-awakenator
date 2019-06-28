import imutils
import dlib
import cv2
import drowsiness_detector_config as cfg
from scipy.spatial import distance as dist
from imutils import face_utils
from imutils.video import VideoStream


def main():
    # initialize dlib's facial detector
    face_detector = dlib.get_frontal_face_detector()

    # create face shape detector
    shape_predictor = dlib.shape_predictor("./models/shape_predictor_68_face_landmarks.dat")

    # grab the indexes of the facial landmarks for the left and right eye
    (l_start, l_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (r_start, r_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    # start the video stream
    print("[INFO] starting video stream thread...")
    print("[INFO] press q to quit")
    vs = VideoStream()rc=cfg.VIDEO_CAMERA.start()

    closed_frames = 0
    while True:
        # get frame from video stream
        frame = vs.read()
        # resize frame
        frame = imutils.resize(frame, width=500)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # detect faces
        faces = face_detector(gray_frame, 0)

        for count, face in enumerate(faces):
            # find facial landmarks
            shape = shape_predictor(gray_frame, face)
            # convert landmark locations to numpy array
            shape = face_utils.shape_to_np(shape)

            # get coordinates for eyes
            left_eye = shape[l_start:l_end]
            right_eye = shape[r_start:r_end]

            # get convex hull for eyes and draw on frame
            left_eye_hull = cv2.convexHull(left_eye)
            right_eye_hull = cv2.convexHull(right_eye)
            cv2.drawContours(frame, [left_eye_hull], -1, (255, 0, 0), 1)
            cv2.drawContours(frame, [right_eye_hull], -1, (255, 0, 0), 1)

            # get EAR for both eyes
            left_eye_aspect_ratio = eye_aspect_ratio(left_eye)
            right_eye_aspect_ratio = eye_aspect_ratio(right_eye)
            ear = (left_eye_aspect_ratio + right_eye_aspect_ratio) / 2.0

            # if eyes are smaller than threshold
            if ear < cfg.EYE_ASPECT_RATIO_THRESHOLD:
                closed_frames += 1
                # if eyes are smaller than threshold for longer than predefined amount of frames
                if closed_frames >= cfg.CLOSED_EYE_FRAMES_THRESHOLD:
                    cv2.putText(frame, "DETECTED DROWSINESS", (10, 30), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 255), 2)
            # if eyes are larger than threshold
            else:
                closed_frames = 0

            cv2.putText(frame, "Eye Aspect Ratio: {:.2f}".format(ear), (300, 30), cv2.FONT_HERSHEY_PLAIN, 1.0,
                        (0, 255, 0), 2)

        # show each frame for 1ms
        cv2.imshow("Frame", frame)
        keypress = cv2.waitKey(1)
        if keypress == ord('q'):
            break


def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    a = dist.euclidean(eye[1], eye[5])
    b = dist.euclidean(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    c = dist.euclidean(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (a + b) / (2.0 * c)

    # return the eye aspect ratio
    return ear


if __name__ == '__main__':
    main()