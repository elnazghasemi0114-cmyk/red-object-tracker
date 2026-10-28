import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0)


MAX_LOST = 20
MAX_DISTANCE = 100

objects = {}
next_id = 1

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("COULD NOT ACCESS CAMERA!")
            break
        current_time = time.perf_counter()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        lower_red1 = np.array([0,100,100])
        upper_red1 = np.array([10,255,255])

        lower_red2 = np.array([170,100,100])
        upper_red2 = np.array([179,255,255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        mask = mask1 | mask2

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        new_objects = {}
        matched_old_ids = set()

        for object_id in objects:
            objects[object_id]["lost"] += 1

        for contour in contours:
            area = cv2.contourArea(contour)

            if area <1000:
                continue

            x,y,w,h = cv2.boundingRect(contour)

            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue
                
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            matched_id = None
            min_distance = float("inf")

            for old_id, old_data in objects.items():
                
                if old_id in matched_old_ids:
                    continue

                old_cx, old_cy = old_data["center"]

                distance = np.sqrt(
                    (cx - old_cx) ** 2 +
                    (cy - old_cy) ** 2
                )
                if distance < min_distance:
                    min_distance = distance
                    matched_id = old_id
                 
            

            if matched_id is not None and min_distance < MAX_DISTANCE:
                object_id = matched_id
                matched_old_ids.add(object_id)
            else:
                object_id = next_id
                next_id += 1

            speed = 0.0
            if object_id in objects and object_id == matched_id:
                position_history = objects[object_id].get(
                    "position_history", []
                ).copy()
            else:
                position_history = []
            
            position_history.append((current_time, cx, cy))

            position_history = [
                p for p in position_history
                if current_time - p[0] <= 1.5
            ]

            target_time = current_time - 0.25
            
            past_position = [
                p for p in position_history
                if p[0] <= target_time
            ]

            if past_position:
                old_time, old_cx, old_cy = past_position[-1]

                elapsed_time = current_time - old_time

                distance = np.sqrt(
                    (cx - old_cx) ** 2 +
                    (cy - old_cy) ** 2
                )

                if distance < 4:
                    distance = 0
            
                if elapsed_time > 0:
                    speed = distance / elapsed_time

            if object_id in objects:
                history = objects[object_id]["history"]
            else:
                history = []
            history.append((cx,cy))
            if len(history) > 30:
                history.pop(0)

            if object_id in objects and object_id == matched_id:
                speed_history =objects[object_id].get(
                    "speed_history", []
                ).copy()
            else:
                speed_history = []

            speed_history.append(speed)

            if len(speed_history) > 5:
                speed_history.pop(0)

            smooth_speed = sum(speed_history) / len(speed_history)

            if smooth_speed < 8:
                smooth_speed = 0
                
            new_objects[object_id] = {
                "center" : (cx, cy),
                "lost": 0,
                "history" : history,
                "timestamp" : current_time,
                "speed_history" : speed_history,
                "position_history": position_history
            }

            cv2.rectangle(
                frame,
                (x,y),
                (x + w,y + h),
                (0, 0, 255),
                2
            )

            cv2.circle(
                frame,
                (cx,cy),
                5,
                (0, 0, 0),
                -1
            )

            for i in range(1,len(history)):
                cv2.line(
                    frame,
                    history[i - 1],
                    history[i],
                    (0,0,0),
                    2
                )

            cv2.putText(
                frame,
                f"Object {object_id}",
                (x, y + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 0),
                2
            )

            cv2.putText(
                frame,
                f"Speed: {smooth_speed:.2f} px/s",
                (x, y+50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255,0,0),
                2
            )

        for object_id, object_data in objects.items():
            if object_id not in matched_old_ids:
                if object_data["lost"] <= MAX_LOST:
                    new_objects[object_id] = object_data

        objects = new_objects

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()