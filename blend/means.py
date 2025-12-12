import sys

import numpy

files = []
for i in range(1, len(sys.argv)):
  files.append(open(sys.argv[i]))

while True:
  vals = []
  l = None
  for handle in files:
    l = handle.readline()
    row = []
    if l:
      try:
        for x in l.split():
          row.append(float(x))
      except Exception:
        pass
    vals.append(row)
  if not l:
    break
  avals = numpy.array(vals)
  means = numpy.mean(avals, axis=0)
  types = l.split()
  out = []
  for i in range(len(means)):
    if "." in types[i]:
      out.append(str(means[i]))
    else:
      out.append(str(int(means[i])))
  print(" ".join(out))

