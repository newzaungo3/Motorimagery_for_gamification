import requests
import keyboard
print('port 8000')
while True:
    condition = input("You want (left) or (right): ")
    print(condition)
    if condition == 'q' or condition =='exit':
        print("End Program")
        break
    else:
        requests.get(f"http://0.0.0.0:8000/JoyController?msg={condition}")
        #requests.get(f"http://localhost:8000/JoyController?msg={condition}")
    
    