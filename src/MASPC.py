import numpy as np
import pandas as pd
import scipy
from sklearn import metrics
from FPMax import FPMax
from Apriori import Apriori
from scipy.cluster.hierarchy import fcluster
from scipy.cluster.hierarchy import linkage

# MASPC algorithm
class MASPC():
    def __init__(self,demographic,dignosisCodes):
        self.demographic = demographic
        self.dignosisCodes = dignosisCodes

    def MAS(self,minSup,minAc,minOv):
        # Run FPMax to get MFI 
        fpmax = FPMax()
        fpmax.encode_input([])
        fpmax.run(minSup)
        
        # Running Apriori is a preparatory step for getting MFA
        apriori = Apriori()
        apriori.encode_input([])
        apriori.run(minSup)
        
        # This assumes input to be the output of the spmf.jar file
        list_1 = []
        for i in apriori.decode_output():
            if len(i)==3:
                list_1.append(i)

        # Get MFA
        all_con=self.get_all_allconfidence(list_1,fpmax.decode_output(),minAc)
        all_con.sort(key=lambda x: x[-1],reverse=True)

        all_con_withoutSUP=[]
        for i in all_con:
            all_con_withoutSUP.append([x for x in i[:len(i)-2]])
        
        all_con_target = []
        for i in all_con_withoutSUP:  
            flag = 0
            for j in all_con_target:
                if (set(i) & set(j) != set()):
                    number = 0
                    for k in self.dignosisCodes:  
                        if ( ( set(k) & (set(i)|set(j)) ) == (set(i)|set(j)) ): 
                            number = number + 1  
                    if number <= minOv:  
                        flag = 1
                        break
            if flag == 0:      
                all_con_target.append(i)
                
        all_con_target_without1=[]

        for i in all_con_target:
            if len(i) != 1:
                all_con_target_without1.append(i)

        # save MFAs
        self.MFAs = all_con_target_without1

    # Input a list of MFIs
    # Return MFIs whose All_confidence is above minAc
    def get_all_allconfidence(self,list_1,list_all_max,threshhold):
        all_max=[]
        for i in list_all_max:
            temp_allconfidence = self.allconfidence(list_1,i)
            if temp_allconfidence >= threshhold:
                i[-1] = temp_allconfidence
                all_max.append(i)
        return all_max

    def allconfidence(self,list_1,list_max):
        # Compute All_confidence of an itemset
        b=[]
        for i in list_max[:len(list_max)-2]:
            for j in list_1:
                if i==j[0]:
                    b.append(int(j[2]))
        return int(list_max[-1])/max(b)

    def PC(self,k,method,metric):
        w, h = len(self.MFAs), len(self.dignosisCodes);
        all_con_tables_without1=[[0 for x in range(w)] for y in range(h)] 

        # project maximum set of independent frequnet patterns 
        for i,j in enumerate(self.dignosisCodes):
            temp=set(j)
            
            l=len(temp)
            for a,b in enumerate(self.MFAs): 
                while(set(b)<=temp):
                    temp=temp.difference(set(b))
                    
                    all_con_tables_without1[i][a]+=1    

        # build a dataframe
        all_con_part_2_without1=pd.DataFrame(all_con_tables_without1, columns=[str(sublist) for sublist in self.MFAs])    
        all_con_final_t_without1=self.demographic.join(all_con_part_2_without1)
        # delete the data that not be subscribed
        all_con_delete_without1= [sum(i) for i in all_con_tables_without1]
        all_con_delete_idex_without1=[i for i, e in enumerate(all_con_delete_without1) if e == 0]
        all_con_final_t_without1.drop(all_con_delete_idex_without1,inplace=True)
        self.binaryData=all_con_final_t_without1
        # do clustering
        all_con_cos_ave_without1 = linkage(all_con_final_t_without1.values, method, metric)
        self.ClusterResult=fcluster(all_con_cos_ave_without1, k, criterion='maxclust')



















