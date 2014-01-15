
#Reads a txt file line by line and returns a list of lists
#with the inner lists being each line of the text file splitted at each occurence of | .

def readsymbols(filename):
 file = open(filename)
 lines = []
 splitted = []
 
 while 1:
  
  line = file.readline()
  if not line:
   break
  splitted = line.split('|')
  lines.append(splitted)

 return lines
 