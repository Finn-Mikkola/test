import json
import csv
import pymysql
import boto3
import os
import urllib

rds_host = os.environ['RDS_HOST']
rds_user = os.environ['RDS_USER']
rds_password = os.environ['RDS_PASSWORD']
rds_db = os.environ['RDS_DB']
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Connect to the RDS database
    connection = pymysql.connect(
        host= rds_host,
        user= rds_user,
        password= rds_password,
        db= rds_db,
        connect_timeout = 500
    )
    print('Connecting')
    
    # Get the S3 object info from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf=8')
    print('Getting object')
    
    # Get the CSV file from S3
    s3 = boto3.client('s3')
    print('boto boto')
    
    
    csv_file_object = s3.get_object(Bucket=bucket_name, Key=file_key)
    print('object recieved')
    
    lines = csv_file_object['Body'].read().decode('utf-8').splitlines()
    
    print('got da lines')
    csv_data = csv.reader(lines, delimiter=',')
    print('csv made')
    
    # Extract headers from the CSV
    headers = next(csv_data)
    print('extracting headers')
    
    with connection.cursor() as cursor:
        # Create a table if it does not exist
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS Patients (
            id INT  PRIMARY KEY,
            age INT, gender INT, height INT,
            weight FLOAT, ap_hi INT, ap_lo INT,
            cholesterol INT, gluc INT, smoke INT,
            alco INT, active INT, cardio INT, age_in_years INT
        )"""
        cursor.execute(create_table_sql)
        print('table created')
        
        # Prepare the INSERT statement
        insert_stmt = (
            f"INSERT INTO Patients ({', '.join(headers)}) "
            f"VALUES ({', '.join(['%s'] * len(headers))})")
        print('inserting values')
        
        # Execute the INSERT statement for each row in the CSV
        for row in csv_data:
            cursor.execute(insert_stmt, row)
        connection.commit()
    
    print('data entered')
    
    # Close the database connection
    connection.close()
    
    print('done')
    
    # return for testing and logging
    return {
        'statusCode': 200,
        'body': f'Successfully inserted CSV data from {file_key}'
    }