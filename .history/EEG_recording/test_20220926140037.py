import  cv2
a = cv2.VideoCapture('C:/Users/Admin/Desktop/Motorimagery_for_gamification/EEG_recording/video/left.mp4')

ret, frame = a.read()
cv2.imshow('show',frame)