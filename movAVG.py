
import numpy
import math

# place = Determines the length of the output lists.
# delta = Period of days for SMA (simple moving avegerage)
# listi = A list of values for open days in the selected period of days + delta days
#         back in time (to calculate moving average for the first day) 

def AVG(listi,place,delta):
 avglist = []
 stdlist = []
 
 if listi == [] or place == 0 or delta == 0 or len(listi)<place:
  return [],[]
 
 #Calculates moving average

 for i in range(place):
  devlist = []
  avg = numpy.mean(listi[i:i+delta])
  avglist.append(avg)
  

  '''Standard deviation for a population - 
      http://stockcharts.com/school/doku.php?id=chart_school:
      technical_indicators:standard_deviation'''
  for n in range(i,i+delta):
   try:
    dev = numpy.square(avg-listi[n])
    devlist.append(dev)
   except:
    pass
    
  stdlist.append(numpy.sqrt((sum(devlist)/len(devlist))))

 return avglist,stdlist
