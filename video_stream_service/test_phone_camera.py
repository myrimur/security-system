# import cv2
# import numpy as np
# import time
# # video = cv2.VideoCapture("http://100.64.130.214:8080/video")
# # skip_rate = 5
# # frame_no = 0
  
# # while True:
# #     ret = video.grab()
# #     frame_no += 1

# #     # if (frame_no % skip_rate == 0):
# #     status, frame = video.retrieve()
# #     # print(status)
# #     # print(frame)
# #     cv2.imshow("TEST", frame)
# #     if cv2.waitKey(1) == 27:
# #         break


# # video.release()  
# # cv2.destroyAllWindows()

# path = "/home/karyna/Pictures/profile_img.jpeg"
  
# # Reading an image in default mode
# image = cv2.imread(path)
# cv2.imshow("TEST", image)
# cv2.waitKey(100)


# Import essential libraries
import requests
import cv2
import numpy as np
import imutils
  
# Replace the below URL with your own. Make sure to add "/shot.jpg" at last.
url = "http://192.168.43.1:8080/shot.jpg"
  
# While loop to continuously fetching data from the Url
while True:
    img_resp = requests.get(url)
    img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
    img = cv2.imdecode(img_arr, -1)
    img = imutils.resize(img, width=1000, height=1800)
    cv2.imshow("Android_cam", img)
  
    # Press Esc key to exit
    if cv2.waitKey(1) == 27:
        break
  
cv2.destroyAllWindows()