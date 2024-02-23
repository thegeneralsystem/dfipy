(importing-data-from-aws-s3)=

# From AWS S3

You can ingest large amounts of data securely and efficently from an AWS S3 bucket. Let's assume that you
have a set of CSV files stored in an AWS S3 bucket.

These are the key steps: 

1. Get the AWS Trust Policy that is associated with your General System account
2. Create a new AWS Role in your AWS account, or select an existing Role
3. Attach the AWS Trust Policy from Step 1 to the Role chosen in Step 2
4. Set up the ingestion job

## 1. Getting the AWS Trust Policy
When importing data from AWS S3, we need to assume a role in your AWS account to be able to scan and
download data. You can get a copy of this trust policy with the `get_aws_trust_policy` method. 

::::{tab-set}

:::{tab-item} dfipy
:sync: dfipy

```python
from dfi import Client

dfi = Client(<token>, <url>)
dfi.ingest.get_aws_trust_policy()
```

This method will return an output similar to the following: 

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Condition": {"StringEquals": {"sts:ExternalId": "test_data"}},
            "Principal": {"AWS": "arn:aws:iam::123456789012:role/dfi/dfi-eks-import-api-12345678901234567890123456"},
        }
    ],
}
 ```
:::
::::

Store the output into a file, e.g. `my_trust_policy.json`.


## 2. Selecting An AWS Role

You need to create or select a Role that has access to the data to be ingested. Specifically, that Role requires an AWS IAM policy to `ListBucket`, `GetObject` and `GetBucketLocation` for the bucket that stores your data.

## 3. Attaching the AWS Trust Policy to a Role

Finally you need to apply the AWS Trust Policy to your Role. Let's assume your Role is `my_role` and the AWS Trust Policy from Step 1 is saved in the file `my_trust_policy.json`. 

As an example, from a Terminal in the Linux Operaing System, the following command will apply the policy to your Role: 

```
aws iam update-assume-role-policy --role-name my_role --policy-document my_trust_policy.json
```

You may want to refer to the following AWS guides for further information: 

- [Editing the trust relationship for an existing role](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/edit_trust.html)
- [Creating an IAM role using a custom trust policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-custom.html)

```{attention}
Once the AWS Trust Policy is attached to your AWS Role, the GS Platform has access to the data that your Role has access to. 
To remove access, the AWS Trust Policy needs to be removed from your AWS Role. 
```

```{attention}
Prior to ingesting any data, the System performs checks to verify that the AWS Trust Policy has been applied correctly. This is to foster good security practices, e.g. the System will not read data from publicly available buckets and files.
```

## 4. Setting up an Ingestion Job

In this example, we're ingesting CSV files in AWS S3 located in `s3://my_bucket/my_path`. Each file has the same schema and the field order is:

`[entity_id, timestamp, longitude, latitude, ipv4, age, home_ipv4, route_id, credit_card_provider, transportation_mode]`

Here is a sample from one file:

```text
aca5597c-8666-43bf-9c85-0b575ece58ed,1640995676000,51.54191120617028,-0.1136967540230455,,,,0,,dwelling
aca5597c-8666-43bf-9c85-0b575ece58ed,1640995690000,51.54201796566859,-0.1135628381946958,,,,0,,dwelling
aca5597c-8666-43bf-9c85-0b575ece58ed,1640995694000,51.54185742565869,-0.1136623400329315,,,,0,,dwelling
aca5597c-8666-43bf-9c85-0b575ece58ed,1640995697000,51.542017930249976,-0.1135929190644742,,,,0,,dwelling
aca5597c-8666-43bf-9c85-0b575ece58ed,1640995700000,51.54181738011452,-0.1136776509308499,,,,0,,dwelling
```


::::{tab-set}

:::{tab-item} dfipy
:sync: dfipy

```python
from dfi.services.ingest import BatchS3Files, CSVFormat, AWSCredentials

role_arn = "<arn of your AWS Role from Step 2"
credentials = AWSCredentials(role_arn)
bucket = "my_bucket"
glob = "*.csv"
prefix = "my_path"

source = BatchS3Files(bucket, credentials, glob, prefix)

csv_format = CSVFormat(
    entity_id=0,
    timestamp=1,
    longitude=2,
    latitude=3,
    ipv4=4,
    age=5,
    home_ipv4=6,
    route_id=7,
    credit_card_provider=8,
    transportation_mode=9,
)
report = dfi.ingest.put_batch(
    dataset_id=<dataset_id>,
    source=source,
    file_format=csv_format,
    dry_run=False
)
```

Example response:

```python
{
    "id": "6f6dcbb3-9746-4722-a642-6aeccdb2ad4f",
    "datasetId": "gs.dataset-1",
    "format": {
        "csv": {
            "age": 5,
            "ipv4": 4,
            "entityId": 0,
            "latitude": 3,
            "route_id": 7,
            "home_ipv4": 6,
            "longitude": 2,
            "timestamp": 1,
            "transportation_mode": 9,
            "credit_card_provider": 8,
        }
    },
    "source": {
        "s3": {
            "glob": "*.csv",
            "bucket": "my_bucket",
            "prefix": "my_path",
            "credentials": {"RoleArn": "arn:aws:iam::123456789123:role/test-import-api-role"},
        }
    },
    "status": "created",
    "insertCount": 0,
    "invalidCount": 0,
    "log": None,
    "addedAt": "2024-01-17T12:27:41.411Z",
    "deletedAt": None
}
```

:::
::::

:::{note}
`prefix` is an optional property. If it is omitted, the System will ingest the entire bucket.
:::