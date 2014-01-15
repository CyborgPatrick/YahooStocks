#avgs is a list of moving averages
#std is a list of standard deviations of the avgs list
#avgtbil is an integer equal to the period used for calc. moving average.

def bollinger(avgs,std,avgtbil):
 upperb = []
 lowerb = []
 
 if avgs == [] or std == [] :
  return [],[]
 


 '''With a 20-day SMA and 20-day Standard Deviation, 
 	the standard deviation multiplier is set at 2. 
 	Bollinger suggests increasing the standard deviation 
 	multiplier to 2.1 for a 50-period SMA 
 	and decreasing the standard deviation 
 	multiplier to 1.9 for a 10-period SMA.
 	http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:bollinger_bands'''
 
 if avgtbil < 10:
  k = 1.9
 elif avgtbil > 50:
  k = 2.1
 else:
  k = 2.0
 
 for n in range(len(avgs)):
  upperb.append(avgs[n] + k*std[n])
  lowerb.append(avgs[n] - k*std[n])

 #Last Inner bollinger bands with k=1
 lastupper = avgs[0] + std[0]
 lastlower = avgs[0] - std[0]

 
 return (upperb,lowerb,lastupper,lastlower)