def BuyOrSell(currentvalue,openvalue,UpInnerBollinger,DownInnerBollinger):

#Checks whether in Buy zone above the Moving average
#between the outer bollinger band with stdDev = 2 and inner bollinger band with stdDev=1)
#To leave the Buy zone the whole candle (open-close/current price) or
#or 75% of a red candle (open price > close/current price) must have moved into the No mans land zone 
#(between the higher and lower inner standard deviation bands)
#Read more: http://www.stock-options-made-easy.com/trading-bollinger-bands.html


 if currentvalue > UpInnerBollinger:
 	return "BUY"
 elif openvalue < UpInnerBollinger and abs(currentvalue-UpInnerBollinger)/(abs(currentvalue-UpInnerBollinger)+abs(openvalue-UpInnerBollinger)) >= 0.75:
  return "BUY"

#Checks whether in Sell zone below the Moving average and 
#between the outer bollinger band with stdDev = 2 and inner bollinger band with stdDev=1)
#To leave the Buy zone the whole candle (open-close/current price) or
#or 75% of a red candle (open price > close/current price) must have moved into the No mans land zone 
#(between the higher and lower inner standard deviation bands)
#Read more: http://www.stock-options-made-easy.com/trading-bollinger-bands.html
 if currentvalue < DownInnerBollinger:
  	return "SELL"
 elif openvalue < DownInnerBollinger and abs(currentvalue-DownInnerBollinger)/(abs(currentvalue-DownInnerBollinger)+abs(openvalue-DownInnerBollinger)) >= 0.75:
  return "SELL"

 #Neither a good buy or sell period. No man's land
 return "NEUTRAL"