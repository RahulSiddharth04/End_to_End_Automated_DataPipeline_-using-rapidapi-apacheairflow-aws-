import boto3
import json
import pandas as pd

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Extract S3 info
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    target_bucket = 'cleaned-data-zone-csv-bucket-dhrs'
    target_file_name = object_key[:-5]  # remove ".json" extension if present
    
    # Wait until the object exists
    waiter = s3_client.get_waiter('object_exists')
    waiter.wait(Bucket=source_bucket, Key=object_key)
    
    # Read JSON object from S3
    response = s3_client.get_object(Bucket=source_bucket, Key=object_key)
    raw_data = response['Body'].read().decode('utf-8')
    data = json.loads(raw_data)
    
    # Flatten the data
    flattened = []
    for item in data["data"]:
        flattened.append({
            "bathrooms": item.get("bathrooms"),
            "bedrooms": item.get("bedrooms"),
            "city": item.get("address", {}).get("city"),
            "state": item.get("address", {}).get("state"),
            "zipcode": item.get("address", {}).get("zipcode"),
            "livingArea": item.get("livingArea"),
            "price": item.get("price", {}).get("value"),
            "rentZestimate": item.get("estimates", {}).get("rentZestimate"),
            "propertyType": item.get("propertyType")
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(flattened)
    print(df.head())
    
    # Convert DataFrame to CSV
    csv_data = df.to_csv(index=False)
    
    # Upload CSV to target S3 bucket
    object_key_csv = f"{target_file_name}.csv"
    s3_client.put_object(Bucket=target_bucket, Key=object_key_csv, Body=csv_data)
    
    return {
        'statusCode': 200,
        'body': json.dumps('CSV conversion and S3 upload completed successfully')
    }
