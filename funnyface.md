
## Bucket 생성

```
$ aws s3 mb --region ap-northeast-2 s3://funnyfaces
make_bucket: funnyfaces

# lifecycle
$ aws s3api put-bucket-lifecycle --bucket funnyfaces \
--lifecycle-configuration '{
    "Rules": [{
        "Status": "Enabled",
        "Prefix": "",
        "Expiration": {
            "Days": 1
        }
    }]
}'

# public
$ aws s3api put-bucket-policy --bucket funnyfaces \
--policy '{
    "Version": "2008-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": { "AWS": "*" },
        "Action": ["s3:GetObject"],
        "Resource": ["arn:aws:s3:::funnyfaces/*" ]
    }]
}'
```
## IAM

**Create IAM Role**

```
$ aws iam create-role --role-name funnyfaces-role \
--assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": { "Service": "lambda.amazonaws.com" },
        "Action": "sts:AssumeRole"
    }]
}'

#output
{
    "Role": {
        "AssumeRolePolicyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    }
                }
            ]
        },
        "RoleId": "AROAJMXP5ZDJVMAXFDNJ2",
        "CreateDate": "2017-01-08T07:55:13.956Z",
        "RoleName": "funnyfaces-role",
        "Path": "/",
        "Arn": "arn:aws:iam::550931752661:role/funnyfaces-role"
    }
}

$ aws iam put-role-policy \
--role-name funnyfaces-role \
--policy-name FunnyFacesS3FullAccess \
--policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": "s3:*",
        "Resource": "arn:aws:s3:::funnyfaces/*"
    }]
}'

$ aws iam attach-role-policy \
--policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
--role-name funnyfaces-role
```

## Lambda Code Packaging

```
$ rm -f pakcages.zip
$ pip install cognitive_face -t packages
$ pushd packages;zip -r ../packages.zip *;popd
$ zip packages.zip funnyfaces.py
```

## Lambda

**Create Lambda Function**

```
$ aws lambda create-function \
    --region ap-northeast-2 \
    --runtime python2.7 \
    --role arn:aws:iam::550931752661:role/funnyfaces-role \
    --descript 'funnyfaces function' \
    --timeout 10 \
    --memory-size 128 \
    --handler funnyfaces.lambda_handler \
    --zip-file fileb://funnyfaces.zip  \
    --function-name GetFaceRecognition \
    --environment Variables='{
        "FACE_API_KEY": "d6bbd77fe1e5421f907035c131855b49"
    }'

#output
{
    "CodeSha256": "MiutpXwgj3QPu9n1Oc3n9OE16I7MRIeYyh+1ynrbD8g=",
    "FunctionName": "GetFaceRecognition",
    "CodeSize": 615,
    "MemorySize": 128,
    "FunctionArn": "arn:aws:lambda:ap-northeast-2:550931752661:function:GetFaceRecognition",
    "Version": "$LATEST",
    "Role": "arn:aws:iam::550931752661:role/funnyfaces-role",
    "Timeout": 10,
    "LastModified": "2017-01-08T16:15:56.503+0000",
    "Handler": "funnyfaces.handler",
    "Runtime": "python2.7",
    "Description": "funnyfaces function"
}
```

**Update Lambda Function**

```
$ aws lambda update-function-code \
    --function-name GetFaceRecognition \
    --zip-file fileb://funnyfaces.zip

#output
{
    "CodeSha256": "EVBe00gzJsyzE6xD617J8hzK4ywR1SWVF+YVjCaQ4T0=",
    "FunctionName": "GetFaceRecognition",
    "CodeSize": 610,
    "MemorySize": 128,
    "FunctionArn": "arn:aws:lambda:ap-northeast-2:550931752661:function:GetFaceRecognition",
    "Version": "$LATEST",
    "Role": "arn:aws:iam::550931752661:role/funnyfaces-role",
    "Timeout": 10,
    "LastModified": "2017-01-08T16:22:59.521+0000",
    "Handler": "funnyfaces.handler",
    "Runtime": "python2.7",
    "Description": "funnyfaces function"
}
```

**Update Permission**

```
$ aws lambda add-permission \
--function-name GetFaceRecognition \
--statement-id 1 \
--action "lambda:InvokeFunction" \
--principal s3.amazonaws.com \
--source-arn arn:aws:s3:::funnyfaces

#output
{
    "Statement": "{\"Sid\":\"1\",\"Resource\":\"arn:aws:lambda:ap-northeast-2:550931752661:function:GetFaceRecognition\",\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"s3.amazonaws.com\"},\"Action\":[\"lambda:InvokeFunction\"],\"Condition\":{\"ArnLike\":{\"AWS:SourceArn\":\"arn:aws:s3:::funnyfaces\"}}}"
}
```

**Lambda Test**

```
emulambda -v funnyfaces.handler event.json
```

## S3 Event 등록

```
$ aws s3api put-bucket-notification-configuration \
--bucket funnyfaces \
--notification-configuration '{
    "LambdaFunctionConfigurations": [{
        "Id": "funnyfaces-lambda",
        "Events": [ "s3:ObjectCreated:*" ],
        "LambdaFunctionArn": "arn:aws:lambda:ap-northeast-2:550931752661:function:GetFaceRecognition"
    }]
}'
```


## RDB

```
aws rds create-db-instance \
    --db-instance-identifier FunnyFacesInstance \
    --db-instance-class db.t2.micro \
    --engine MySQL \
    --allocated-storage 5 \
    --no-publicly-accessible \
    --db-name funnyfaces \
    --master-username funnyfaces \
    --master-user-password funnyfaces \
    --backup-retention-period 0 \
    --publicly-accessible

#output
{
    "DBInstance": {
        "PubliclyAccessible": false,
        "MasterUsername": "funnyfaces",
        "MonitoringInterval": 0,
        "LicenseModel": "general-public-license",
        "VpcSecurityGroups": [
            {
                "Status": "active",
                "VpcSecurityGroupId": "sg-dc4b68b5"
            }
        ],
        "CopyTagsToSnapshot": false,
        "OptionGroupMemberships": [
            {
                "Status": "in-sync",
                "OptionGroupName": "default:mysql-5-6"
            }
        ],
        "PendingModifiedValues": {
            "MasterUserPassword": "****"
        },
        "Engine": "mysql",
        "MultiAZ": false,
        "DBSecurityGroups": [],
        "DBParameterGroups": [
            {
                "DBParameterGroupName": "default.mysql5.6",
                "ParameterApplyStatus": "in-sync"
            }
        ],
        "AutoMinorVersionUpgrade": true,
        "PreferredBackupWindow": "17:58-18:28",
        "DBSubnetGroup": {
            "Subnets": [
                {
                    "SubnetStatus": "Active",
                    "SubnetIdentifier": "subnet-8bb6d2e2",
                    "SubnetAvailabilityZone": {
                        "Name": "ap-northeast-2a"
                    }
                },
                {
                    "SubnetStatus": "Active",
                    "SubnetIdentifier": "subnet-b3db01fe",
                    "SubnetAvailabilityZone": {
                        "Name": "ap-northeast-2c"
                    }
                }
            ],
            "DBSubnetGroupName": "default",
            "VpcId": "vpc-6a9d0103",
            "DBSubnetGroupDescription": "default",
            "SubnetGroupStatus": "Complete"
        },
        "ReadReplicaDBInstanceIdentifiers": [],
        "AllocatedStorage": 5,
        "DBInstanceArn": "arn:aws:rds:ap-northeast-2:550931752661:db:funnyfacesinstance",
        "BackupRetentionPeriod": 0,
        "DBName": "funnyfaces",
        "PreferredMaintenanceWindow": "sat:14:39-sat:15:09",
        "DBInstanceStatus": "creating",
        "EngineVersion": "5.6.27",
        "DomainMemberships": [],
        "StorageType": "standard",
        "DbiResourceId": "db-VS2HKQHNLZ7EPABBK4ZDAUXGPA",
        "StorageEncrypted": false,
        "DBInstanceClass": "db.t2.micro",
        "DbInstancePort": 0,
        "DBInstanceIdentifier": "funnyfacesinstance"
    }
}
```

**Lambda를 VPC에 넣어야 RDB접속이 가능한데 VPC에 넣을 경우에 인터넷 사용을 위해서는 NAT gateway를 사용해야한다.**

> When you enable VPC, your Lambda function will lose default internet access. If you require external internet access for your function, ensure that your security group allows outbound connections and that your VPC has a NAT gateway.

테스트 용이니 RDB의 Inbound를 모두 허용한다.​

**EndPoint**

```
$ aws rds describe-db-instances --query "DBInstances[0].Endpoint.Address"
```

## SQL

**Create Table**

```
CREATE TABLE funnyfaces.faces_tbl (
	id INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	face_id varchar(50) NOT NULL,
	smile SMALLINT(3) UNSIGNED NOT NULL,
	age TINYINT(3) UNSIGNED NOT NULL,
    male BOOL DEFAULT FALSE,
    female BOOL DEFAULT FALSE,
	img_url varchar(100) NOT NULL,
	created_at DATETIME DEFAULT NOW() NOT NULL,
	PRIMARY KEY(ID)
)
ENGINE=MyISAM
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci;
```

**Age/Smile Time**

```
SELECT CONVERT_TZ(FROM_UNIXTIME(UNIX_TIMESTAMP(created_at) - UNIX_TIMESTAMP(created_at) MOD 60), @@session.time_zone, '+9:00') as dt,
	   ROUND(AVG(smile/10)) as avg_smile,
	   ROUND(AVG(age)) as avg_age,
	   ROUND(SUM(male)) as male_count,
	   ROUND(SUM(female)) as female_count,
	   COUNT(*) as total_count
FROM funnyfaces.faces_tbl
WHERE DATE_ADD(created_at, INTERVAL 9 HOUR) >= '2017-01-10 23:00:00'
GROUP BY UNIX_TIMESTAMP(created_at) DIV 60
```

**Age**

```
SELECT '0-10' label, count(CASE WHEN age BETWEEN 0 AND 10 THEN 1 END) from faces_tbl
UNION ALL
SELECT '10-20' label, count(CASE WHEN age BETWEEN 10 AND 20 THEN 1 END) value from faces_tbl
UNION ALL
SELECT '20-30' label, count(CASE WHEN age BETWEEN 21 AND 30 THEN 1 END) value from faces_tbl
UNION ALL
SELECT '30-40' label, count(CASE WHEN age BETWEEN 31 AND 40 THEN 1 END) value from faces_tbl
UNION ALL
SELECT '40-50' label, count(CASE WHEN age BETWEEN 41 AND 50 THEN 1 END) value from faces_tbl
UNION ALL
SELECT '50-60' label, count(CASE WHEN age BETWEEN 51 AND 60 THEN 1 END) value from faces_tbl
UNION ALL
SELECT '60-70' label, count(CASE WHEN age BETWEEN 61 AND 70 THEN 1 END) value from faces_tbl
UNION ALL
SELECT 'over 70' label, count(CASE WHEN age > 70 THEN 1 END) value from faces_tbl
```

**Gender**

```
SELECT 'Male' label, SUM(male) count from faces_tbl
UNION ALL
SELECT 'Female' label, SUM(female) count from faces_tbl
```
