import requests
import keyboard
print('port 80')
while True:
    condition = input("You want (left) or (right): ")
    print(condition)
    if condition == 'q' or condition =='exit':
        print("End Program")
        break
    else:
        requests.get(f"http://localhost:2040/JoyController?msg={condition}")
    
    
    