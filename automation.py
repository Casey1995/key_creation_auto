import os
import boto3

kms = boto3.client('kms')
ssm = boto3.client('ssm')
#Desc = 'Development key108'            Input via postman
#usage = 'ENCRYPT_DECRYPT'              Input via postman
#Alias_Name = 'alias/projectKey108'     Input via postman

def send_sns():
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:372957966260:NOTIFY_ON_KEY_CREATION')
    response = topic.publish(Message='A key with name: {} was recently created on your account. \nKindly review and modify key policy.'.format(Desc))
    return response

def lambda_handler(event, context):
    
    def get_parameters():
        global key_policy
        try:
            #Retrieve key policy from secret manager parameter store.
            response = ssm.get_parameters(
                Names=['keypolicy'],WithDecryption=False
            )
            for key, value in response.items():
                key_policy = value[0].get('Value')
        except IndexError:
            print('Retrieved value not valid')
            
    get_parameters()
    try:
        #Creating KMS key
        key = kms.create_key(
            Description=Desc,
            KeyUsage=usage
            )
        key_id = key["KeyMetadata"]["KeyId"]
        
        #Creating key alias
        alias = kms.create_alias(
            AliasName=Alias_Name,
            TargetKeyId=str(key_id)
            )
            
        #insert key policy from parameter store.
        keypolicy = kms.put_key_policy(
            KeyId=key_id,
            PolicyName='default',
            Policy=key_policy
            )
    except:
            print("An error has occured")
    #send notification to crypto admin
    send_sns()
