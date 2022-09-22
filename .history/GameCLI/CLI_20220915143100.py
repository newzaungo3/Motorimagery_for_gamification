import requests
import keyboard
print('port 8003')
while True:
    condition = input("You want (left) or (right): ")
    print(condition)
    if condition == 'q' or condition =='exit':
        print("End Program")
        break
    else:
        requests.get(f"http://host.docker.internal:8003/JoyController?msg={condition}")
    
    
    