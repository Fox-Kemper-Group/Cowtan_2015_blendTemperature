import sys

lines = sys.stdin.readlines()

date = []
vals = []
for i in range(len(lines)):
  words = lines[i].split()
  if len(words) > 1:
    dat = float(words[0])
    val = (len(words) - 1) * [None]
    for j in range(len(val)):
      try:
        val[j] = float(words[j + 1])
      except Exception:
        pass
    if None not in val:
      date.append(dat)
      vals.append(val)

newdate = []
newvals = []
for i in range(0, len(vals) - 11, 12):
  newdate.append(int(date[i]) + 0.5)
  yvals = vals[i:i + 12]
  newrow = []
  for c in range(len(yvals[0])):
    s = 0.0
    for j in range(len(yvals)):
      s += yvals[j][c] / len(yvals)
    newrow.append(s)
  newvals.append(newrow)

for i in range(len(newvals)):
  s = "%8.4f" % newdate[i]
  for j in range(len(newvals[i])):
    s += " %7.4f" % newvals[i][j]
  print(s)
