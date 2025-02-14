import boto3
import botocore.config
import json
from datetime import datetime

def blog_generate_using_bedrock(message:str) -> str:
    prompt = f""" <s>[INST]Human: Write a 200 words blog on the topic {message}
    Assistant:[/INST]
    """

    body={
        "prompt":prompt,
        "max_gen_len":512,
        "temperature":0.5,
        "top_p":0.9
    }

    try:
        bedrock = boto3.client("bedrock-runtime",region_name="us-east-1",config=botocore.config.Config(read_timeout=300,retries={'max_attempts':3}))
        
        response = bedrock.invoke_model(body=json.dumps(body),modelId='')
        
        response_content = response.get('body').read()
        
        response_data = json.loads(response_content)

        print(response_data)

        blog_details = response_data['generation']

        return blog_details
    
    except Exception as e:
        print(f"Error generating the blog {e}")

def save_blog_details_s3(s3_key,s3_bucket,generate_blog):
    s3 = boto3.client('s3')

    try:
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body = generate_blog)
        print("code saved to s3")

    except Exception as e:
        print("Error when saving the blog to s3")


def lambda_handler(event,context):
   event = json.loads(event['body'])
   blogtopic = event["blog"]

   generate_blog = blog_generate_using_bedrock(message=blogtopic)

   if generate_blog:
       current_time = datetime.now().strftime('%H%M%S')
       s3_key = f"blog-output/{current_time}.txt"
       s3_bucket = 'aws_bedrock_course1'
       save_blog_details_s3(s3_key,s3_bucket,generate_blog)

   else:
       print("No Blogwas generated")

   return{
       'statusCode':200,
       'body':json.dumps('Blog Generation is completed')
   }
       