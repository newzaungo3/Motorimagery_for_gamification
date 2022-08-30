import requests
import keyboard
while True:
    condition = input("You want left or right: ")
    if condition == 'q' or condition =='exit':
        print("End Program")
        break
    else:
        requests.get(f"http://localhost/JoyController?msg={condition}")
    
    
    