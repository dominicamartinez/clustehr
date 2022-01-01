import numpy as np
import pandas as pd
import scipy
from sklearn import metrics
from FPMax import FPMax
from Apriori import Apriori
from MASPC import MASPC
import csv
from scipy.cluster.hierarchy import fcluster
from scipy.cluster.hierarchy import linkage
from optbinning import ContinuousOptimalBinning

# pd.set_option('display.max_colwidth', -1)
# pd.options.display.max_columns = None
pd.options.display.width = 0

class MASPC_Engine():

    def __init__(self, inputFileName, myMinAc=None, myMinOv=None, 
                myMinSup=None, myK=None,myContainsTemporal=False,
                myAutoDiscretize=False,myDiscretizeStrategy=None,myQ=4):
        print("inside maspc_engine constructor with "+inputFileName)
        self.inputFileName = inputFileName
        self.outputFileFolder = '/tmp/'
        self.sortedInputFile = self.outputFileFolder+'sortedInputFile.csv'
        self.myMinAc = myMinAc
        self.myMinOv = myMinOv
        self.myMinSup = myMinSup
        self.myK = myK
        self.myContainsTemporal = myContainsTemporal
        self.myAutoDiscretize = myAutoDiscretize
        self.myDiscretizeStrategy = myDiscretizeStrategy
        self.myQ = myQ

        # First thing we do is sort input file
        self.__sortInputFile(self.inputFileName)
        self.rtDataFrame = pd.read_csv(self.sortedInputFile, dtype=str)

        # remove any rows that may have empty diagnosis, sex, or age
        self.rtDataFrame.dropna(subset=['DX1', 'age', 'sex'], inplace=True)
        self.rtDataFrame.reset_index(drop=True, inplace=True)

        # Extract diagnoses for processing (Diagnosis DataFrame)
        rtDataFrameDiags = self.rtDataFrame.drop(['age', 'sex'], axis=1).copy()
        diagColumns = [str(i) for i in list(rtDataFrameDiags.columns.values) if i.startswith('D')]
        uvalues = list(pd.unique(self.rtDataFrame[diagColumns].values.ravel('K')))
        uniqueDiags = [x for x in uvalues if str(x) != 'nan']

        # process the list of unique diagnoses to update diagnosis dataframe and write file for fpmax and apriori
        self.__writeInputFile(uniqueDiags, rtDataFrameDiags)
        
        # # To do one hot encoding of sex:
        self.demographic = pd.get_dummies(self.rtDataFrame['sex'])
        self.rtDataFrame = self.rtDataFrame.drop('sex',axis=1)

        # This runs for when input values are just integers and needs to be discretized
        if (self.myAutoDiscretize):
            self.rtDataFrame = self.__autoDiscretize(self.rtDataFrame,self.myDiscretizeStrategy,self.myQ)

        # one hot encoding for age (This is assuming that the autodiscretization has already happened or
        # the data came pre-binned)
        one_hot = pd.get_dummies(self.rtDataFrame['age'])
        self.rtDataFrame = self.rtDataFrame.drop('age',axis=1)
        self.demographic = self.demographic.join(one_hot)

        # print(demographic)
        # Read dignosisCodes.txt as input for dignosis codes
        # dignosis = open('dignosisCodes.txt', 'r')
        # dignosisCodes = [line[:-2].split(' ') for line in dignosis.readlines()]

        # print(type(dignosisCodes))

        # this is for pandas 1.0.5 or versions that give ValueErrors for the next statement
        self.dignosisCodes = self.rtDataFrame.stack().groupby(level=0).apply(list).tolist()

        # this is for pandas 1.24.0+ I believe but will complain about different size lists
        # in other versions
        # dignosisCodes = rtDataFrame.T.apply(lambda x: x.dropna().tolist()).tolist()

        # print(dignosisCodes)

        # Check diagnosis codes
        # Each row is diagnosis codes of a patient 
        # print('all diagnosis codes')
        # for i in dignosisCodes:
        #     print(i)

    def processOneDiagPerLine(self):
        allRows = []
        maxNumOfDiagColumns = 0
        with open(self.inputFileName) as csvfile:
            fileReader = csv.reader(csvfile)
            header = next(fileReader)
            processingRow = []
            for row in fileReader:
                if (len(processingRow)):
                    if (row[0] == processingRow[0] and row[1] == processingRow[1]):
                        processingRow.append(row[2])
                    else:
                        allRows.append(processingRow)
                        if ((len(processingRow)-2) > maxNumOfDiagColumns):
                            maxNumOfDiagColumns = len(processingRow)-2
                        processingRow = []
                        for element in row:
                            processingRow.append(element)
                else:
                    for element in row:
                        processingRow.append(element)

            # for last element outside of loop
            allRows.append(processingRow)
            if ((len(processingRow)-2) > maxNumOfDiagColumns):
                maxNumOfDiagColumns = len(processingRow)-2

        # dynamically create diag columns from processed input
        allColumns = ['sex','age']
        for i in range(1, (maxNumOfDiagColumns+1)):
            allColumns.append('DX'+str(i))

        # use pandas dataframe from list of lists for easy output
        df = pd.DataFrame(allRows, columns = allColumns)
        df.to_csv(self.inputFileName,index=False)

    def processTemporal(self):
        self.rtDataFrame = pd.read_csv(self.inputFileName, dtype=str)
        for col in self.rtDataFrame.columns:
            if ('Date' in col):
                self.rtDataFrame.drop([col],axis=1,inplace=True)

        print(self.rtDataFrame)
        self.rtDataFrame.to_csv(self.inputFileName,index=False)

    def autogenerateParameters(self):
        accept = False
        numOfRecords = len(self.rtDataFrame.index)
        clusteredRecordsThreshold = .1
        self.myMinOv = 3
        temp_ms = (1-(1/numOfRecords))/10
        maspc1 = MASPC(self.demographic, self.dignosisCodes)
        maspc2 = MASPC(self.demographic, self.dignosisCodes)
        maspc3 = MASPC(self.demographic, self.dignosisCodes)

        while (not accept):
            print('trying ... '+str(temp_ms))
            run = []
            # run 3 all-confidence parameters
            maspc1.MAS(minSup=float(temp_ms),minAc=float(0.5),minOv=float(self.myMinOv))
            if (len(maspc1.MFAs) > 1):
                maspc1.PC(k=float(len(maspc1.MFAs)),method='average',metric='cosine')

                if (len(maspc1.binaryData.index)/numOfRecords > clusteredRecordsThreshold):
                    run.append({'mfa':len(maspc1.MFAs),'ac':0.5,'clustered':len(maspc1.binaryData.index)})

            maspc2.MAS(minSup=float(temp_ms),minAc=float(0.25),minOv=float(self.myMinOv))
            if (len(maspc2.MFAs) > 1):
                maspc2.PC(k=float(len(maspc2.MFAs)),method='average',metric='cosine')

                if (len(maspc2.binaryData.index)/numOfRecords > clusteredRecordsThreshold):
                    run.append({'mfa':len(maspc2.MFAs),'ac':0.25,'clustered':len(maspc2.binaryData.index)})

            maspc3.MAS(minSup=float(temp_ms),minAc=float(0.1),minOv=float(self.myMinOv))
            if (len(maspc3.MFAs) > 1):
                maspc3.PC(k=float(len(maspc3.MFAs)),method='average',metric='cosine')

                if (len(maspc3.binaryData.index)/numOfRecords > clusteredRecordsThreshold):
                    run.append({'mfa':len(maspc3.MFAs),'ac':0.1,'clustered':len(maspc3.binaryData.index)})


            # after 3 runs, check to see if one passed our threshold
            if (len(run) > 0):
                self.myMinSup = temp_ms
                self.myMinAc = run[0]['ac']
                self.myK = run[0]['mfa']
                accept = True
            else: # cycle
                temp_ms = temp_ms/10


        print('k = '+str(self.myK))
        print('minOv = '+str(self.myMinOv))
        print('minAc = '+str(self.myMinAc))
        print('minSup = '+str(self.myMinSup))
        print('num of records = '+str(numOfRecords))
        print('num clustered = '+str(run[0]['clustered']))


    def runAnalyzer(self):
        # Run MASPC
        # Input parameters for given dataset: minSup=0.33, minAc=0.5, minOv=3, k=3
        # method='average' and metric='cosine' are parameters for agglomerative average-linkage hierarchical clustering

        maspc = MASPC(self.demographic, self.dignosisCodes)
        maspc.MAS(minSup=float(self.myMinSup),minAc=float(self.myMinAc),minOv=float(self.myMinOv))

        # check number of MFAs before continuing processing
        if (len(maspc.MFAs) < 1):
            return False

        maspc.PC(k=float(self.myK),method='average',metric='cosine')

        # Check results of MASPC
        # Check MFAs
        # print("MFAs:")
        # print(maspc.MFAs)

        # Check clustering results
        # print("Cluster Results:")
        # print(maspc.ClusterResult)

        # Add label to binary representation
        maspc.binaryData['label']=maspc.ClusterResult
        maspc.binaryData['parameters'] = None
        maspc.binaryData['parameters'].iloc[0] = 'minOv = '+str(self.myMinOv)
        maspc.binaryData['parameters'].iloc[1] = 'minAc = '+str(self.myMinAc)
        maspc.binaryData['parameters'].iloc[2] = 'minSup = '+str(round(float(self.myMinSup), 2))
        maspc.binaryData['parameters'].iloc[3] = 'k = '+str(self.myK)

        #print(maspc.binaryData)
        maspc.binaryData.to_csv('/tmp/clusteringResults.csv',index=False)
        
        # print(maspc.binaryData.label.unique())
        # for i in range(1, len(maspc.binaryData.label.unique())+1):
        #     print('Cluster '+str(i))
        #     print(maspc.binaryData.groupby(['label']).get_group(i))


        # SI and CI

        # Get all unique diagnosis codes and build a binary representation for evaluation
        allUniqueCodes=[]
        for i in self.dignosisCodes:
            for j in i:
                allUniqueCodes.append(j)
        allUniqueCodes=list(set(allUniqueCodes))
        new_list = [allUniqueCodes[i:i+1] for i in range(0, len(allUniqueCodes), 1)]


        w, h = len(allUniqueCodes), len(self.dignosisCodes);
        atables=[[0 for x in range(w)] for y in range(h)] 

        # project maximum set of independent frequnet patterns 
        for i,j in enumerate(self.dignosisCodes):
            temp=set(j)
            #print temp
            for a,b in enumerate(new_list): 
                while(set(b)<=temp):
                    temp=temp.difference(set(b))
                    #print temp
                    atables[i][a]+=1  

        diga_codes=pd.DataFrame(atables, columns=[str(sublist) for sublist in allUniqueCodes])

        # Binary representation for evaluation
        testdata=pd.concat([self.demographic, diga_codes], axis=1, sort=False)

        # CI and SI
        # print('CI: '+str(metrics.calinski_harabasz_score(testdata.values, maspc.ClusterResult.tolist())))
        # print('SI: '+str(metrics.silhouette_score(testdata.values, maspc.ClusterResult.tolist(), metric='cosine')))

        return True

    def __writeInputFile(self, uniqueDiags, rtDataFrameDiags):
        #print(uniqueDiags)
        uniqueDiags.sort()
        print('# of unique diag values = '+str(len(uniqueDiags)))

        # # iterate through the values and put them into a format for the apriori
        diagHeaderFileName = "dignosisCodes.txt"
        diagHeaderFile = open(diagHeaderFileName, "w")
        print('@CONVERTED_FROM_TEXT',file=diagHeaderFile)
        itemCounter = 1
        for v in uniqueDiags:
            # print(str(v))
            # print(type(v))
            if (str(v) != 'nan'):
                print('@ITEM='+str(itemCounter)+'='+str(v), file=diagHeaderFile)
                rtDataFrameDiags.replace(v, str(itemCounter),inplace=True)
                itemCounter = itemCounter + 1
        diagHeaderFile.close()

        print('1/2 Apriori and FPMax input file written.')
        # we need to create the bottom half of the diagnosis file for the Apriori and FPMax 
        rtDataFrameDiags.to_csv('dignosisCodes2.txt',sep=' ',index=False, header=False)

        # append the diagnosesCodes2 to dignosisCodes
        f1 = open(diagHeaderFileName,'a+')
        f2 = open('dignosisCodes2.txt','r')
        f1.write(f2.read())
        f2.close()
        f1.close()

        print('2/2 Complete Apriori and FPMax input file written.')

    def __autoDiscretize(self,rtDataFrame,myDiscretizeStrategy,myQ):
        rtDataFrame["age"] = pd.to_numeric(rtDataFrame["age"])
        if ('optbin' == myDiscretizeStrategy):
            optb = ContinuousOptimalBinning(name='age',dtype='numerical')
            optb.fit(rtDataFrame.age.values,rtDataFrame.age.values)
            correspondingBins = optb.transform(rtDataFrame.age.values,metric='bins')
            newColumn = pd.DataFrame({'age':correspondingBins})
            rtDataFrame.drop(['age'], axis=1, inplace=True)
            rtDataFrame = pd.concat([rtDataFrame, newColumn], axis=1)
        elif ('pqcut' == myDiscretizeStrategy):
            rtDataFrame['age'] = pd.qcut(rtDataFrame.age, q=int(myQ))
            rtDataFrame.age.astype(str)

        # Combine original dataframe with replaced values of binning process
        # pandas.concat([df1, df2], axis=1)
        return rtDataFrame

    def __sortInputFile(self,inputFileName):
        with open(inputFileName) as csvfile:
            with open(self.sortedInputFile, 'w') as outputCSVFile:
                inputFileReader = csv.reader(csvfile)
                outputFileWriter = csv.writer(outputCSVFile)

                header = next(inputFileReader) # skipping header
                outputFileWriter.writerow(header)

                numOfColumns = len(header)

                for row in inputFileReader:
                    rowDiags = [ x for x in row[2:] if x != '' ]
                    rowDiags.sort()
                    listToWrite = row[:2]
                    listToWrite.extend(rowDiags)
                    # pad = numOfColumns-len(listToWrite)
                    # for i in range(0,pad):
                    #     listToWrite.append('')
                    outputFileWriter.writerow(listToWrite)