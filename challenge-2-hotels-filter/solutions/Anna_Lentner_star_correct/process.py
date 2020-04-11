import pandas as pd
import json
from joblib import load
import numpy as np
sample_df = pd.read_pickle('filtered.pkl')

input_df = pd.read_json('inputs.json')
df_order = []
answers = [{"missing": True}] * len(input_df)


for i in range(input_df.shape[0]):
    star=input_df.loc[i][2]
    if star in sample_df.index.values:
        
        df=sample_df.loc[star, 'data'].copy()
        select_indices=list(np.where((df["price"] >= input_df.loc[i,'min_price']) &
                                     (df["price"] <= input_df.loc[i,'max_price']))[0])
        
        df=df.iloc[select_indices]
        if len(df)==0:
            
            continue
        else:
            df['distance']=df.apply(lambda x: ( (x['lat']-input_df.loc[i,'lat'])**2+(x['lon']-input_df.loc[i,'lon'])**2), axis=1 )
            answer = df[df['distance']==df['distance'].min()]

    
        if not answer.empty:
            answers[i] = answer[["lon", "lat", "name", "stars", "price"]].to_dict('records')[0]

                                
    else:
        continue

json.dump(answers, open("outputs.json", "w"))
