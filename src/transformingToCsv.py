#input file
fin = open("./dataCoordinates/notFound.txt", "rt")
#output file to write the result to
fout = open("./dataCoordinates/notFound.csv", "wt")
#for each line in the input file
for line in fin:
	#read replace the string and write to output file
	fout.write(line.replace('[', '').replace(']',''))
#close input and output files
fin.close()
fout.close()