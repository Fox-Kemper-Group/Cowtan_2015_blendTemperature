import sys, numpy
cols = 4*[[228,26,28],
          [55,126,184],
          [77,175,74],
          [152,78,163],
          [255,127,0],
          [191,191,0],
          [166,86,40],
          [247,129,191],
          [153,153,153]]
lins = 9*[[]]+9*[[6,1]]+9*[[3,1]]+9*[[5,1,1,1]]

cols = [[x/255.0 for x in rgb] for rgb in cols]

x = []
y = []
m = []
for f in sys.argv[1:]:
  data = numpy.genfromtxt(f)
  x = data[:,0]
  y.append( data[:,3] )
  m.append( f.split('_')[1] )

mlist = sorted(list(set(m)))
print mlist, len(mlist)

import matplotlib.pyplot as plt
plt.xlim([int(min(x)-1),int(max(x)+1)])
plt.ylim([-0.1,0.1])
plt.ylabel(r'Temperature anomaly ($^\circ$C)')
plt.xlabel(r'Year')
lines = [None for i in mlist]
for i in range(len(y)):
  j = mlist.index(m[i])
  lines[j], = plt.plot(x,y[i],'-',c=cols[j],dashes=lins[j],lw=0.75)
plt.axhline(color='k')
plt.legend(lines,mlist,loc='lower left',frameon=False,ncol=4,prop={'size':8})
plt.savefig("rcp85-bias.eps")
plt.show()

