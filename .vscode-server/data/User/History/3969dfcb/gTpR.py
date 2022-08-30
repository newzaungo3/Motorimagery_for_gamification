import requests
condition = input("You want left or right: ")

requests.get(f"http://localhost:5020/JoyController?msg={condition}")