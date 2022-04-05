import requests
condition = input("You want left or right Isus")

requests.get(f"http://localhost/JoyController?msg={condition}")