import json
from pyspark.sql import SQLContext
sqlContext = SQLContext(sc)
import pandas as pd
import pandas
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
import os
import glob
mydir="/home/cloudera/streamData/output*"

#Running the program continuously
while(True):
#     mydir="file:/home/cloudera/streamData/output*"
    output_files = [file for file in glob.glob(os.path.join(mydir, 'part-*'))]
    output_files.sort(key=os.path.getmtime,reverse=True)
    
    #Reading the most rececntly modified file while plotting 
    myrdd1 = sc.wholeTextFiles('file:'+output_files[0])
    print('file:'+output_files[0])
    
    #Converting to spark DataFrame
    dataDF=myrdd1.toDF()
    dataDF=dataDF.toPandas()
    dataDF.columns=["filename","cities"]
    
    #Filtering the empty cities
    dataDF=dataDF[dataDF['cities']!=""]
    dataDF=dataDF[dataDF['filename']!=""]
    if not dataDF.empty:
        newDF=dataDF
    
        if newDF.shape[0]!=0:
            location=pd.DataFrame(newDF['cities'][0].split('\n'))
            location.columns=['cities']
            location["cities"]=location["cities"].astype(str)
            splitDF=location['cities'].apply(lambda x: pd.Series(x.split(',')))
            splitDF.columns=['cities','counts']
            splitDF['counts']=splitDF['counts'].map(lambda x: str(x).replace(')',''))
            splitDF=splitDF[splitDF["cities"]!='nan']
            splitDF=splitDF[splitDF["counts"]!='nan']
    
            splitDF['counts']=pd.to_numeric(splitDF['counts'])
            splitDF['cities']=splitDF['cities'].map(lambda x: str(x).replace('(u',''))
            
            #Sorting the city based on city counts 
            aggregated_df=splitDF.groupby("cities")["counts"].sum()
            aggregated_df=aggregated_df.sort_values(ascending=False)
            aggregated_df=aggregated_df.head(10)
            aggregated_df.plot(kind='bar')
            plt.show()