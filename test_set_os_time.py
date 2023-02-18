# A script to simulate a day by mangling the system clock
import subprocess
from time import sleep

for hour in range(5, 23):
    for minute in range(2):
        subprocess.run(["sudo", "date", "+%T", "-s", "{}:{}:00".format(str(hour), str(30 if minute else 0))])
        sleep(5)
