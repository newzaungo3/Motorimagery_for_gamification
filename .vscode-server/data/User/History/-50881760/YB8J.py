import requests
import keyboard
print('port 8001')
while True:
    condition = input("You want (left) or (right): ")
    print(condition)
    if condition == 'q' or condition =='exit':
        print("End Program")
        break
    else:
        requests.get(f"http://127.0.0.1:8001/JoyController?msg={condition}")
        #requests.get(f"http://localhost:8000/JoyController?msg={condition}")
    
    