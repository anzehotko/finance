from datetime import datetime

now = datetime.now()

current_time = now.strftime("%d/%m/%Y %H:%M:%S")
print("Current Time =", current_time)