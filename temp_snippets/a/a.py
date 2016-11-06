import datetime

import sqlite3.

m = {}
count = 0

lines = excel.read(f)

for line in lines:
    if line[5] in m:
        new_value = m[line[5]]
    else:
        count += 1
        new_value = "A%d" % count
        m[line[5]] = new_value
    line[5] = new_value

excel.write(lines)
