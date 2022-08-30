import requests
import keyboard
while True:
    condition = input("You want left or right: ")

    requests.get(f"http://localhost/JoyController?msg={condition}")
    
    if keyboard.is_pressed('q'):
                print("End of experiment")
                break
    