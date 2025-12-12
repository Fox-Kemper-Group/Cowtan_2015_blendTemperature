import sys, numpy, re

files = []
for i in range(1,len(sys.argv)):
  files.append(open(sys.argv[i]))

while(1):
  vals = []
  for i in range(len(files)):
    l = files[i].readline()
    if l:
      row = []
      try:
        for x in l.split():
          row.append(float(x))
      except:
        pass
    vals.append(row)
  if not l: break
  avals = numpy.array(vals)
  means = numpy.mean( avals, axis=0 )
  types = l.split()
  for i in range(len(means)):
    if "." in types[i]:
      print means[i],
    else:
      print int(means[i]),
  print

