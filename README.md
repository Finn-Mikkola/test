![cover_page](./static/dataset-cover.jpg)

# Patient_AWS_pipe

### *Designing an ETL pipeline in AWS using S3, RDS, Lambda (Python), and Kaggle data*

**by: [Finn Mikkola](https://github.com/ChungoMungus), [Jason Fearnall](https://github.com/Fearnall-Jason) & [Max Ross](https://github.com/ImMaxRoss)**

- Using a dataset from Kaggle (csv in `data/` folder and link sourced below) we designed a pipeline so that when the csv file is put into an S3 bucket it triggers our first Lambda `pandas_clean_to_s3.py` which cleans the data using pandas and sends that two a second S3 bucket. The second S3 bucket is set to trigger our second Lambda `transfer_to_rds` which uses pymysql to connect to our MySQL RDS database and loads the data as a table.

- We also created an EC2 instance to showcase our findings in the form of a webpage with screenshots of our insights. All of which can be found in the `static/` folder. The site is no longer live but can be recreated using the html and corresponding image files found in the same folder.


[Kaggle Data Source](https://www.kaggle.com/datasets/sulianova/cardiovascular-disease-dataset)


## Screenshot of our EC2 hosted Webpage:
![webpage](./static/webpage.png)


### How To Recreate:

1. **AWS Free Tier account**
2. **Create a New VPC**:
    - Select VPC and more
    - unselect 'Auto-generate' name tag auto-generation and create a name for your vpc
    - keep the rest of the default settings
3. **Create a new security group**
    - name your security group
    - write a description like "temporary security group I'm creating so that I don't mess up the config of my default groups"
    - VPC: select the name of the VPC you created a step before
    - Add Inbound rule:
      - Type: All Traffic
      - Source: Anywhere IPv4
    - Add Outbound rule:
      - Type: All Traffic
      - Source: Anywhere IPv4
4. **Create RDS instance**:
    - MySQL engine v.8.0.3b set to free tier
    - Credential settings:
      - Master username: admin
      - Master password : (create a password)
    - Connectivity:
      - Select the VPC you created
      - Existing VPC security groups: unselect 'default' and select the security group you created.
      - Public Access Yes (optionally you can make this private but you'll have to take extra steps to configure a new private VPC with private subnets and an RDS proxy)
    - Additional configuration:
      - initial database name: CardioDB
    - (optional) unselect 'Enable automated backups' (optional, but can save you computation time when inserting into the DB)
    - Rest of the settings remain unchanged and kept on the default options
5. **Create a new Role in IAM**:
    - Trusted entity type: AWS service
    - Use case: Lambda
    - Permission Policies: AmazonRDSFullAccess, AmazonS3FullAccess, AWSLambda_FullAccess, AWSLambdaVPCAccessExecutionRole
    - role name: lambda_full_access (or whatever you'd like)
6. **Create Lambda Function 1**
    - Author from scratch
    - function name: pandas_clean_to_s3 (or whatever you'd like)
    - Runtime: Python 3.12
    - Architecture: x86_64
    - Execution role: select use an existing role and choose the role you created in the previous step
    - leave all advanced settings unchecked
    - create function
    - Copy all of the content in `pandas_clean_to_sr.py`, remove the content in lambda_function.py and/or paste over it.
    - Add the AWS Layer "AWSSDKPandas-Python312", we used version 1 but whatever is available should be fine.
    - Go to general configureation and edit the timeout to 2 minutes.
    - Deploy the function
7. **Create S3 Bucket 1**
    - Name your bucket something like "dirtydatabucket"
    - leave all default settings
    - after you create go to the bucket Event Notification in Properties
    - Create event notification
    - name your event something like "Panda Put Trigger"
    - Select 'Put' from Object creation
    - Choose from your Lambda Functions and select the Lambda created in the previous step and save changes
8. **Create Lambda Function 2**
    - On your local machine create a new folder and call it "lambda_dependencies"
    - Copy the `transfer_to_rds.py` file and paste it to this folder.
    - Rename `transfer_to_rds.py` to 'lambda_function.py'
    - Open up a command terminal and navigate to "lambda_dependencies"
    - run "pip install pymysql -t ."
    - You should now have pymysql package files and your function inside "lambda_dependencies" folder
    - Zip "lambda_dependencies"
    - Go back to AWS and create a new Lambda
    - Author from scratch
    - function name: pandas_clean_to_s3 (or whatever you'd like)
    - Runtime: Python 3.12
    - Architecture: x86_64
    - Execution role: select use an existing role and choose the role you created in the previous step
    - leave all advanced settings unchecked
    - After the function is created select 'Upload from' and select your zipped "lambda_dependencies"
    - Move the contents of the lambda_dependencies into the main directory of your code directory
    - Go to general configureation and edit the timeout to 10 minutes. (note: you have 750 hours of free compute a month and max time for function run is 15min)
    - In configuration edit Environment Variables and add the following:
      - key: RDS_DB  Value: CardioDB
      - key: RDS_HOST  Value: (go to the RDS database you've created, copy the RDS endpoint and paste it here)
      - key: RDS_USER  Value: admin
      - key: RDS_PASSWORD Value: (enter the Password you created for your RDS db)
9.  **Create S3 Bucket 2**
    - Name your bucket something like "cleandatabucket"
    - leave all default settings
    - after you create go to the bucket Event Notification in Properties
    - Create event notification
    - name your event something like "Pymysql Put Trigger"
    - Select 'Put' from Object creation
    - Choose from your Lambda Functions and select the Lambda you created in the previous step (`transfer_to_rds.py`) and save changes
10. **Upload the Kaggle csv into S3 Bucket 1**
    - Go to the first S3 bucket you created from step 7 ("dirtydatabucket") and upload your csv file
11. **Check S3 Bucket 2**
    - If you've done all of the previous steps you will now have a new csv file in your "cleandatabucket" and your data pipeline is complete
    - If you the csv file is not there go to Log Groups in CloudWatch and select the log for the "transfer_to_rds" lambda and then select the latest log for that group. So long as it's been more than 12 minutes (more or less depending on what you put for the Timeout configurations in the Lambdas) the report will tell if there was an error or the function timed out. If the function timed out delete the clean.csv from the cleandatabucket and adjust the Timeout configurations. If there is an error, you'll have to debug and most likely had something to do with your VPC/Security Group/Role-permissions configurations.
