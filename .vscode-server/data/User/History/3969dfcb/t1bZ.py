import requests
condition = input("You want left or right: ")

requests.get(f"http://localhost/JoyController?msg={condition}")