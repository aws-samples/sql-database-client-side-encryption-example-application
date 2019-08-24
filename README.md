## SQL Database Client-side Encryption Example Application

SQL Database Client-side Encryption Example Application

This is the sample AWS CloudFormation that sets up a multi-region Amazon Aurora MySQL database with AWS Fargate microservice. This is for the blog post blog post How to Perform SQL Database Client-Side Encryption Backed by KMS for Multi-Region High Availability.

You will need to ensure that the [AWS Serverless Application Model (SAM) Command Line Interface (CLI)](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) is installed.

[Quickstart using virtual env](https://github.com/awslabs/aws-sam-cli/issues/1266#issuecomment-510253729)

```
python3.7 -m venv samcli-venv
source samcli-venv/bin/activate
pip3 install --upgrade pip
pip3 install aws-sam-cli
sam --version
```

Create a AWS KMS key administrator role. Be sure that the key policy that you create allows the current user to [administer the CMK](https://aws.amazon.com/premiumsupport/knowledge-center/update-key-policy-future/).

For example, create a role named 'KeyAdministratorRole' with the following IAM Policy.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "kms:Create*",
                "kms:Describe*",
                "kms:Enable*",
                "kms:List*",
                "kms:Put*",
                "kms:Update*",
                "kms:Revoke*",
                "kms:Disable*",
                "kms:Get*",
                "kms:Delete*",
                "kms:ScheduleKeyDeletion",
                "kms:CancelKeyDeletion",
                "kms:TagResource",
                "kms:UntagResource"
            ],
            "Resource": "*",
            "Effect": "Allow"
        }
    ]
}
```

You will need to create an AWS CodeCommit repository named 'django-webapp' in the primary and secondary region in order for the AWS CodePipeline to build the Docker image. You can clone this repo and push to CodeCommit in each region.

If you are familiar with editing the .git/config file, you can use these as examples and substitute the corresponding region for REGION-HERE.

```
[remote "aws"]
    url = https://git-codecommit.REGION-HERE.amazonaws.com/v1/repos/django-webapp
    fetch = +refs/heads/*:refs/remotes/aws/*
[remote "aws2"]
    url = https://git-codecommit.REGION-HERE.amazonaws.com/v1/repos/django-webapp
    fetch = +refs/heads/*:refs/remotes/aws2/*
```

Then execute

```
git push aws master
git push aws2 master

```

Deploy the primary region.

Build the Lambda source code and generate deployment artifacts that target Lambda's execution environment.

```
sam build --template cfn.iamauthentication.yaml --build-dir ../tmp/iamauthentication-build-dir
sam build --template cfn.client-side-encryption-replica.yaml --build-dir ../tmp/client-side-encryption-replica-build-dir
```

Package the AWS CloudFormation nested template. Update the parameter for desired regions and the AWS CloudFormation user.

Input parameter |    Input parameter description
--- | ---
SecondaryRegion  |  Enter the secondary region for the Amazon Aurora Read Replicas.
KeyAdministratorRole  | This is the IAM Role that is managing the CMK.

Specify the Amazon S3 Bucket.

```
sam package \
--s3-bucket "$BUCKET" \
--output-template-file ../tmp/packaged-cfn.client-side-encryption-replica.yaml \
--template-file ../tmp/client-side-encryption-replica-build-dir/template.yaml
```

Then, deploy the nested AWS CloudFormation stack. Choose an appropriate name for the stack.

```
sam deploy \
--stack-name "$STACK_NAME" \
--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
--template-file ../tmp/packaged-cfn.client-side-encryption-replica.yaml
```

Deploy the secondary region after the first region has successfully deployed,

Build the Lambda source code and generate deployment artifacts that target Lambda's execution environment.

```
sam build --template cfn.iamauthentication.yaml --build-dir ../tmp/iamauthentication-build-dir
sam build --template cfn.client-side-encryption-replica.yaml --build-dir ../tmp/client-side-encryption-replica-build-dir #--use-container
```

Package the nested AWS CloudFormation template. Specify the Amazon S3 Bucket. Update the parameters for primary region, AWS CloudFormation user and the arn for the primary region Amazon Aurora cluster.

Input parameter  |  Input parameter description
--- | ---
PrimaryRegion  |  Enter the primary region where both reads and write are performed with Amazon Aurora.
KeyAdministratorRole  |  This is the IAM Role that is managing the CMK.
SourceDBInstanceIdentifier  |  Enter the primary region Amazon Aurora cluster arn. This value is located in the AWS CloudFormation outputs under the database stack value AuroraClusterArn. An Amazon Aurora cluster replica will be created in the secondary region.

```
sam package \
--s3-bucket "$BUCKET" \
--output-template-file ../tmp/packaged-cfn.client-side-encryption-replica.yaml \
--template-file ../tmp/client-side-encryption-replica-build-dir/template.yaml
```



Deploy the nested AWS CloudFormation stack. Choose an appropriate name for the stack.

```
sam deploy \
--stack-name "$STACK_NAME" \
--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
--template-file ../tmp/packaged-cfn.client-side-encryption-replica.yaml
```

After successfully deploying the secondary region, execute the Amazon Aurora credential rotation in the primary region. The primary region rotation will trigger a sync to the secondary region to ensure that the secondary region AWS Secrets Manager in the secondary region has matching credentials. The sync approach utilizes the the process described in [How to automate replication of secrets in AWS Secrets Manager across AWS Regions](https://aws.amazon.com/blogs/security/how-to-automate-replication-of-secrets-in-aws-secrets-manager-across-aws-regions/).


## License Summary

This sample code is made available under the MIT-0 license. See the LICENSE file.
