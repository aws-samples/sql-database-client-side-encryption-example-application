import os
import json
import aws_encryption_sdk
import boto3

from codecompose.settings import AWS_PRIMARY_REGION, AWS_SECONDARY_REGION, COLUMN_ENCRYPTION_KEY_ALIAS

#https://aws.amazon.com/blogs/security/new-aws-encryption-sdk-for-python-simplifies-multiple-master-key-encryption/
def build_multiregion_kms_master_key_encryption_provider():
    regions = (AWS_PRIMARY_REGION,AWS_SECONDARY_REGION)
    alias = COLUMN_ENCRYPTION_KEY_ALIAS
    arn_template = 'arn:aws:kms:{region}:{account_id}:{alias}'

    # Create AWS KMS master key provider
    kms_master_key_provider = aws_encryption_sdk.key_providers.kms.KMSMasterKeyProvider()

    # Find your AWS account ID
    account_id = boto3.client('sts').get_caller_identity()['Account']

    # Add the KMS alias in each region to the master key provider
    for region in regions:
        kms_master_key_provider.add_master_key(arn_template.format(
            region=region,
            account_id=account_id,
            alias=alias
        ))
    return kms_master_key_provider

def build_thisregion_kms_master_key_decryption_provider():
    #on AWS Fargate get the region running in
    region = os.environ['AWS_REGION']
    arn_template = 'arn:aws:kms:{region}:{account_id}:key/{key_id}'

    kms=boto3.client('kms', region_name=region)
    aliases=kms.list_aliases()['Aliases']
    found_alias=next(item for item in aliases if item["AliasName"] == COLUMN_ENCRYPTION_KEY_ALIAS)
    key_id=found_alias['TargetKeyId']

    # Find your AWS account ID
    account_id = boto3.client('sts').get_caller_identity()['Account']

    kms_arn=arn_template.format(
        region=region,
        account_id=account_id,
        key_id=key_id
    )

    # Create AWS KMS master key provider
    kms_master_key_provider = aws_encryption_sdk.key_providers.kms.KMSMasterKey(key_id=kms_arn)

    return kms_master_key_provider

master_key_encryption_provider = build_multiregion_kms_master_key_encryption_provider()
master_key_decryption_provider = build_thisregion_kms_master_key_decryption_provider()
