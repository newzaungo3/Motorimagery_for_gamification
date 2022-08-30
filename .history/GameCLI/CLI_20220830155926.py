import requests
import keyboard
while True:
    condition = input("You want left or right: ")

    requests.get(f"http://localhost/JoyController?msg={condition}")
    
    if condition == 'q' or condition =='exit':
        print("End Program")
        break
    