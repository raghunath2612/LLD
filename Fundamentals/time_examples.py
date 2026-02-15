import time
from datetime import datetime, timedelta

# Initializing datetime variables

time1: datetime = datetime.now()
time2: datetime = datetime.now() - timedelta(days=1)

time3: timedelta = time1 - time2

diff_in_mins = time3.total_seconds() // 60

print(diff_in_mins)
print(type(diff_in_mins))