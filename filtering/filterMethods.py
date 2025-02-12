import subprocess

ALT,QUAL,FILTER,INFO = 4,5,6,7
MIN_MAP_QUALITY = 0 
GT,AD,DP,GQ,PL = 0,1,2,3,4;
MIN_MUT_GQ = 20
HETZ,HOMZ='0/1','0/0'
CHROM=0
DELS = 5
MAX_DELS = 0.0
MAX_FREQ_ALT = 0.01
MIN_ALT_READS = 7

class filterMethods():


    def __init__(self,medianFileLoc,sampleCount):
        self.SAMPLE_MEDIANS = self.getSampleMedians(medianFileLoc)
        self.MIN_VALID_SAMPLES_DP = int(sampleCount*(2.0/3.0))

    def getSampleMedians(self,medianFileLoc):
        """
        Returns SAMPLE_MEDIANS a 2d list where each sublist 
            is the lower and upper DP bounds.
            SAMPLE_MEDIANS = [[5,15],[10,30]..]
        """
        medFile = open(medianFileLoc,"r")
        for i, line in enumerate(medFile):
            #print line
            if i == 1:
                SAMPLE_MEDIANS = [[float(i)*0.5,float(i)*1.5] for i in line.strip("\n").split(" ")]
        return SAMPLE_MEDIANS

    def validSampleDP(self,sample_idx,DP):
        """
        Returns whether the sample has a depth within the specified range
        """
        DP = float(DP)
        if DP >= self.SAMPLE_MEDIANS[sample_idx][0] and DP <= self.SAMPLE_MEDIANS[sample_idx][1]:
            return True
        return False

    def isDataLine(self,line):
        """
        Determines in line contains site data
        """
        if len(line) > 1:
            return line[0] != "#"

        return False
    
    def validInfoValue(self,tag,info,min_bound = None,max_bound = None):
        """
        Returns whether the specified info value is withen the given range
        If 'tag' is not found returns true
        """
        info_col = info.split(";")
        val = None
        val_pass = False

        for inf in info_col:
            if tag in inf:
               val = float(inf[inf.find("=") + 1:])
       
        if val == None:
            return True
 
        if min_bound != None and max_bound != None:
            return (val >= min_bound and val <= max_bound)

        else:
            if min_bound != None:
                return val >= min_bound
            if max_bound != None:
                return val <= max_bound
            else:
                return True 


    def siteFiltering(self,line_col):
        """
        Filters the site for:
            - on chromosome 'pseudo0'
            - presence of ALT base
            - no LowQual flag
        """
        if line_col[CHROM] == 'pseudo0':
            return False        

        if line_col[ALT] != ".":
            return float(line_col[QUAL]) >= MIN_MAP_QUALITY and \
                line_col[FILTER] != "LowQual" 
#                self.validInfoValue("Dels",line_col[INFO],None,None)#not necessary
        return False


    def sampleFiltering(self,samples):
        """
        For the site to pass samples must:
            - no missing samples
            - One Sample GT must be different than others
        """
        gt_counts={}
        numValidDP = 0
        hom_count  = len(samples) - 1
        het_count = 1
        

        for i in range(0,len(samples)):
            if "./." not in samples[i]:
                s_col = samples[i].split(":")

                if self.validSampleDP(i,s_col[DP]):
                    numValidDP += 1

                gt_counts[s_col[0]] = gt_counts.get(s_col[0],0) + 1
        
            else:
                #return false if missing sample is present
                return False

        if numValidDP < self.MIN_VALID_SAMPLES_DP:
            #less than 2/3 of samples passed DP filters
            return False

        if gt_counts.get(HETZ,0) == het_count and gt_counts.get(HOMZ,0) == hom_count:
            return self.filterMutant(gt_counts,samples) and self.filterGroup(samples)

        return False

    def filterGroup(self,samples):
        """
        Filters group samples:
            - No sample with MAX_FREQ_ALT of its reads being alternate
        """
        alt_count = 0
        ref_count = 0
    
        for s in samples:
            s_col = s.split(":")
            if s_col[GT] == HOMZ:
                #Do not add mutant to counts
                alt_count  += float(s_col[AD].split(",")[1])
                ref_count += float(s_col[AD].split(",")[0])

        return not (alt_count/ref_count > MAX_FREQ_ALT)

    def filterMutant(self,gt_counts,samples):
        """
        Filters on the odd GT individual
        """
        for key in gt_counts.keys():
            if gt_counts.get(key) == 1:
                break

        for i in range(0,len(samples)):
            if key in samples[i]:
                break
        splitSample = samples[i].split(":")
        if int(splitSample[GQ]) <= MIN_MUT_GQ:
            return False
 

        altReads = int(splitSample[AD].split(",")[1])
        refReads = int(splitSample[AD].split(",")[0])

        # Filter based on MIN_ALT_READS
        if altReads < MIN_ALT_READS:
            return False

        #print samples[i]
        #print refReads 
        #print altReads
 
        #binomResult = "TRUE" in str((subprocess.Popen("../r/binom.r " + str(altReads)\
        #     +" "+str(refReads),shell=True,stdout=subprocess.PIPE)).communicate()[0])
        #print binomResult
        
        return self.validSampleDP(i,samples[i].split(":")[DP]) #and binomResult
