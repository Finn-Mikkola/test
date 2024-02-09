import json
import pandas as pd
import urllib
import boto3
from io import StringIO  

s3 = boto3.client('s3')


def lambda_handler(event, context):
    
    
    try: 
        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        s3_file_name = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf=8')
        resp = s3.get_object(Bucket=bucket_name, Key=s3_file_name)

        df = pd.read_csv(resp['Body'], sep=';')
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        df['age_in_years'] = round(df['age'] / 365)
        
        df = df.drop(df[(df['ap_lo'] > df['ap_hi']) | 
                (df['ap_lo'] > 220) | 
                (df['ap_hi'] > 220) | 
                (df['ap_lo'] < 25) | 
                (df['ap_hi'] < 25)].index)
        
        
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        bucket_name2 = 'peptwo-bucket-clean'  
        s3.put_object(Bucket=bucket_name2, Key='clean.csv', Body=csv_buffer.getvalue())

    except Exception as err:
        print(err)