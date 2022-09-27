import  cv2
a = cv2.VideoCapture('C:/Users/Admin/Desktop/Motorimagery_for_gamification/EEG_recording/video/left.mp4')

while(True):
    ret, frame = a.read()
    cv2.imshow('show',frame)
    #cv2.waitKey(1) == ord('q')
    #cv2.destroyWindow('show')