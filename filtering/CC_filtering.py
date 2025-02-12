import sys
from filterMethods import filterMethods

CC3_3Midx = 11
REMOVE_CC3_3M = True

if __name__ == "__main__":
    file_loc,out_name = sys.argv[1],sys.argv[2]
    outFile = open(out_name,'w')
    sampleMediansLoc = "/data/daniel.cole/spirodela/data/rerun/CC3-3/indMedDP.txt"

    filterManager = filterMethods(sampleMediansLoc,12)

    with open(file_loc) as f:
        for line in f:
            if filterManager.isDataLine(line):
                line_col = str.split(line)
                if filterManager.siteFiltering(line_col):
                    if filterManager.sampleFiltering(line_col[9:21]):
                        #Site passed filters
                        outFile.write(line)

            #Write header info        
            else:
                outFile.write(line)

    outFile.close()
    f.close()

