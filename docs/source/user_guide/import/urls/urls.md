(importing-data-from-urls)=

# From URLs

## Example

In this example, we're ingesting 9 CSV files in AWS S3 located in `s3://1B_with_filter_fields/datasets`. It's a small batch of files, and we haven't yet setup the Import service with the appropriate AWS credentials, so instead we generate presigned URLs for each file and pass the URLs as a list to the Import service.

Each file has the same schema and the field order is:

- `[entity_id, timestamp, longitude, latitude, ipv4, age, home_ipv4, route_id, credit_card_provider, transportation_mode]`

Here is a sample from one file:

```text
aca5597c-8666-43bf-9c85-0b575ece58ed,1640995676000,51.54191120617028,-0.1136967540230455,,,,0,,dwelling
aca5597c-8666-43bf-9c85-0b575ece58ed,1640995690000,51.54201796566859,-0.1135628381946958,,,,0,,dwelling
aca5597c-8666-43bf-9c85-0b575ece58ed,1640995694000,51.54185742565869,-0.1136623400329315,,,,0,,dwelling
aca5597c-8666-43bf-9c85-0b575ece58ed,1640995697000,51.542017930249976,-0.1135929190644742,,,,0,,dwelling
aca5597c-8666-43bf-9c85-0b575ece58ed,1640995700000,51.54181738011452,-0.1136776509308499,,,,0,,dwelling
```

The following code block uses the `default` AWS profile to generate presigned URLs for every file in the prefix with the suffix `.csv`. We then describe which fields in the CSVs map to fields described in the `gs.dataset-1` dataset's schema. Once the import is kicked off, we receive a report (the same report returned by [Import Information](#import-information) ) describing the import and it's current status. We can checkin with the import see it's full history in [Import Status](#import-status).
::::{tab-set}

:::{tab-item} dfipy
:sync: dfipy

```python
from dfi import Client
from dfi.services.ingest import BatchURLFiles, CSVFormat, S3URLPresigner

dfi = Client(<token>, <url>)

dataset_id = "gs.dataset-1"
bucket = "datasets"
prefix = "1B_with_filter_fields"
region = "eu-west-2"
profile= "default"

s3_presigner = S3URLPresigner(bucket, region, profile)
signed_urls = s3_presigner.generate_presigned_urls(PREFIX, ".csv", expiration=5)
source = BatchURLFiles(signed_urls)

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

dfi.ingest.put_batch(
    dataset_id=<dataset_id>,
    source=source,
    file_format=csv_format,
    dry_run=False,
)
```

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
        "urls": [
            "https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-000.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAZXWHO2DFCXZI6L74%2F20240124%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240124T152931Z&X-Amz-Expires=30&X-Amz-SignedHeaders=host&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEMD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJHMEUCIQD9umkGW4y8w9KflH99hmyCp9mbt5kTM8kPBMnZFOr3SQIgB%2BVRQgWjb2BBXVOK2aUqpW3%2FzQyyQqYQBNnziECms3EqxgMIeRADGgw2NjkzNTk0NjA1NTQiDNXvTxeLQL3cPRKr2iqjAzo55V1HYNQyU6FNc3B%2BT91R9%2F63AInTHPwkQFyHJh1vODo%2BN31hYTB754N2iZgSMx%2BKh0bBFmfSmc%2BSe6rfrFXugDmYQELqETmRMBxAtqcYlK11MJHpgk9u2WwNINLafj5LhzCvknyGmQG27uOAGvLLITk6SpTSB6gcsSMF56VuGZ4Wi3yrM6ThiDGxsRsJj0UwFRUZ9nQAkqlrKYAAkLO8rpuo575dWaDSzZIlR4zuC3IZPH2kIUKdJ0PvhVlhT0L2GJ%2FC94lcaHOJ29G%2FtzwXEnDhm9bE51eb%2FZrpGGN8feemKUc0RDhuAUPxNYFptHf0RfVVdwnkwrR9I%2BexISdmiGtZn%2BENrKVObCSN4W1mEfxL1LRme9iDeph9HS51ztXj%2B0XRtO1PU9ZfZVvmAznzSrxj2LLB4Ilx6wP5IONCXXg7o9k36lghYNYwWkNDsKUBaEGqvzcoxUTquJbwSgWzChQ97zBzVI2v7RD9ewsHVHpj46mR7TBeTRpFYQZPvFrCQo7QHVVj3%2BlT1g6ZsMnVGAm3QlPfo4jE1IteKMsZdTIlMNfZxK0GOqYBlzVaPWurlITUQ9fD6qPRfkmQf7fDz6E3SeZmJL1Th7AsCeqrc7FcfXTlPiKuN0bdyQTzvuBqLXz8VePM3uFvkJ7YKHX%2FpJVbneAr6roSNkdeCfQWUVMarQbx5VGTpcFm5OL90UKA70%2FRZwNqTSh4fMrPX67K2CHVvAjfJRMYWtxgh3pyy3zBhlYVr1Cznvb9B7a4CAya6cWpH6or4sygNr9N%2F3j5Cg%3D%3D&X-Amz-Signature=dd4ac5a3f191646900516b3c270018c89d9a63a6f214de62a8b0e4c71bf86a8e",
            "https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-001.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAZXWHO2DFCXZI6L74%2F20240124%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240124T152931Z&X-Amz-Expires=30&X-Amz-SignedHeaders=host&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEMD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJHMEUCIQD9umkGW4y8w9KflH99hmyCp9mbt5kTM8kPBMnZFOr3SQIgB%2BVRQgWjb2BBXVOK2aUqpW3%2FzQyyQqYQBNnziECms3EqxgMIeRADGgw2NjkzNTk0NjA1NTQiDNXvTxeLQL3cPRKr2iqjAzo55V1HYNQyU6FNc3B%2BT91R9%2F63AInTHPwkQFyHJh1vODo%2BN31hYTB754N2iZgSMx%2BKh0bBFmfSmc%2BSe6rfrFXugDmYQELqETmRMBxAtqcYlK11MJHpgk9u2WwNINLafj5LhzCvknyGmQG27uOAGvLLITk6SpTSB6gcsSMF56VuGZ4Wi3yrM6ThiDGxsRsJj0UwFRUZ9nQAkqlrKYAAkLO8rpuo575dWaDSzZIlR4zuC3IZPH2kIUKdJ0PvhVlhT0L2GJ%2FC94lcaHOJ29G%2FtzwXEnDhm9bE51eb%2FZrpGGN8feemKUc0RDhuAUPxNYFptHf0RfVVdwnkwrR9I%2BexISdmiGtZn%2BENrKVObCSN4W1mEfxL1LRme9iDeph9HS51ztXj%2B0XRtO1PU9ZfZVvmAznzSrxj2LLB4Ilx6wP5IONCXXg7o9k36lghYNYwWkNDsKUBaEGqvzcoxUTquJbwSgWzChQ97zBzVI2v7RD9ewsHVHpj46mR7TBeTRpFYQZPvFrCQo7QHVVj3%2BlT1g6ZsMnVGAm3QlPfo4jE1IteKMsZdTIlMNfZxK0GOqYBlzVaPWurlITUQ9fD6qPRfkmQf7fDz6E3SeZmJL1Th7AsCeqrc7FcfXTlPiKuN0bdyQTzvuBqLXz8VePM3uFvkJ7YKHX%2FpJVbneAr6roSNkdeCfQWUVMarQbx5VGTpcFm5OL90UKA70%2FRZwNqTSh4fMrPX67K2CHVvAjfJRMYWtxgh3pyy3zBhlYVr1Cznvb9B7a4CAya6cWpH6or4sygNr9N%2F3j5Cg%3D%3D&X-Amz-Signature=3e2eb141ee7202997e22a70eafe20fbdba9eb4a4153238c3082a8b46166d62d1",
            "https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-002.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAZXWHO2DFCXZI6L74%2F20240124%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240124T152931Z&X-Amz-Expires=30&X-Amz-SignedHeaders=host&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEMD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJHMEUCIQD9umkGW4y8w9KflH99hmyCp9mbt5kTM8kPBMnZFOr3SQIgB%2BVRQgWjb2BBXVOK2aUqpW3%2FzQyyQqYQBNnziECms3EqxgMIeRADGgw2NjkzNTk0NjA1NTQiDNXvTxeLQL3cPRKr2iqjAzo55V1HYNQyU6FNc3B%2BT91R9%2F63AInTHPwkQFyHJh1vODo%2BN31hYTB754N2iZgSMx%2BKh0bBFmfSmc%2BSe6rfrFXugDmYQELqETmRMBxAtqcYlK11MJHpgk9u2WwNINLafj5LhzCvknyGmQG27uOAGvLLITk6SpTSB6gcsSMF56VuGZ4Wi3yrM6ThiDGxsRsJj0UwFRUZ9nQAkqlrKYAAkLO8rpuo575dWaDSzZIlR4zuC3IZPH2kIUKdJ0PvhVlhT0L2GJ%2FC94lcaHOJ29G%2FtzwXEnDhm9bE51eb%2FZrpGGN8feemKUc0RDhuAUPxNYFptHf0RfVVdwnkwrR9I%2BexISdmiGtZn%2BENrKVObCSN4W1mEfxL1LRme9iDeph9HS51ztXj%2B0XRtO1PU9ZfZVvmAznzSrxj2LLB4Ilx6wP5IONCXXg7o9k36lghYNYwWkNDsKUBaEGqvzcoxUTquJbwSgWzChQ97zBzVI2v7RD9ewsHVHpj46mR7TBeTRpFYQZPvFrCQo7QHVVj3%2BlT1g6ZsMnVGAm3QlPfo4jE1IteKMsZdTIlMNfZxK0GOqYBlzVaPWurlITUQ9fD6qPRfkmQf7fDz6E3SeZmJL1Th7AsCeqrc7FcfXTlPiKuN0bdyQTzvuBqLXz8VePM3uFvkJ7YKHX%2FpJVbneAr6roSNkdeCfQWUVMarQbx5VGTpcFm5OL90UKA70%2FRZwNqTSh4fMrPX67K2CHVvAjfJRMYWtxgh3pyy3zBhlYVr1Cznvb9B7a4CAya6cWpH6or4sygNr9N%2F3j5Cg%3D%3D&X-Amz-Signature=eb7dcebb994d9be233a2803883df0ee768a7a97741d1d752641f51b0d51250aa",
            "https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-003.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAZXWHO2DFCXZI6L74%2F20240124%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240124T152931Z&X-Amz-Expires=30&X-Amz-SignedHeaders=host&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEMD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJHMEUCIQD9umkGW4y8w9KflH99hmyCp9mbt5kTM8kPBMnZFOr3SQIgB%2BVRQgWjb2BBXVOK2aUqpW3%2FzQyyQqYQBNnziECms3EqxgMIeRADGgw2NjkzNTk0NjA1NTQiDNXvTxeLQL3cPRKr2iqjAzo55V1HYNQyU6FNc3B%2BT91R9%2F63AInTHPwkQFyHJh1vODo%2BN31hYTB754N2iZgSMx%2BKh0bBFmfSmc%2BSe6rfrFXugDmYQELqETmRMBxAtqcYlK11MJHpgk9u2WwNINLafj5LhzCvknyGmQG27uOAGvLLITk6SpTSB6gcsSMF56VuGZ4Wi3yrM6ThiDGxsRsJj0UwFRUZ9nQAkqlrKYAAkLO8rpuo575dWaDSzZIlR4zuC3IZPH2kIUKdJ0PvhVlhT0L2GJ%2FC94lcaHOJ29G%2FtzwXEnDhm9bE51eb%2FZrpGGN8feemKUc0RDhuAUPxNYFptHf0RfVVdwnkwrR9I%2BexISdmiGtZn%2BENrKVObCSN4W1mEfxL1LRme9iDeph9HS51ztXj%2B0XRtO1PU9ZfZVvmAznzSrxj2LLB4Ilx6wP5IONCXXg7o9k36lghYNYwWkNDsKUBaEGqvzcoxUTquJbwSgWzChQ97zBzVI2v7RD9ewsHVHpj46mR7TBeTRpFYQZPvFrCQo7QHVVj3%2BlT1g6ZsMnVGAm3QlPfo4jE1IteKMsZdTIlMNfZxK0GOqYBlzVaPWurlITUQ9fD6qPRfkmQf7fDz6E3SeZmJL1Th7AsCeqrc7FcfXTlPiKuN0bdyQTzvuBqLXz8VePM3uFvkJ7YKHX%2FpJVbneAr6roSNkdeCfQWUVMarQbx5VGTpcFm5OL90UKA70%2FRZwNqTSh4fMrPX67K2CHVvAjfJRMYWtxgh3pyy3zBhlYVr1Cznvb9B7a4CAya6cWpH6or4sygNr9N%2F3j5Cg%3D%3D&X-Amz-Signature=804d474415924407fad0c2d3f0752d1fcfb41233b1e137e3a7fc877d4b31afd3",
            "https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-004.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAZXWHO2DFCXZI6L74%2F20240124%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240124T152931Z&X-Amz-Expires=30&X-Amz-SignedHeaders=host&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEMD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJHMEUCIQD9umkGW4y8w9KflH99hmyCp9mbt5kTM8kPBMnZFOr3SQIgB%2BVRQgWjb2BBXVOK2aUqpW3%2FzQyyQqYQBNnziECms3EqxgMIeRADGgw2NjkzNTk0NjA1NTQiDNXvTxeLQL3cPRKr2iqjAzo55V1HYNQyU6FNc3B%2BT91R9%2F63AInTHPwkQFyHJh1vODo%2BN31hYTB754N2iZgSMx%2BKh0bBFmfSmc%2BSe6rfrFXugDmYQELqETmRMBxAtqcYlK11MJHpgk9u2WwNINLafj5LhzCvknyGmQG27uOAGvLLITk6SpTSB6gcsSMF56VuGZ4Wi3yrM6ThiDGxsRsJj0UwFRUZ9nQAkqlrKYAAkLO8rpuo575dWaDSzZIlR4zuC3IZPH2kIUKdJ0PvhVlhT0L2GJ%2FC94lcaHOJ29G%2FtzwXEnDhm9bE51eb%2FZrpGGN8feemKUc0RDhuAUPxNYFptHf0RfVVdwnkwrR9I%2BexISdmiGtZn%2BENrKVObCSN4W1mEfxL1LRme9iDeph9HS51ztXj%2B0XRtO1PU9ZfZVvmAznzSrxj2LLB4Ilx6wP5IONCXXg7o9k36lghYNYwWkNDsKUBaEGqvzcoxUTquJbwSgWzChQ97zBzVI2v7RD9ewsHVHpj46mR7TBeTRpFYQZPvFrCQo7QHVVj3%2BlT1g6ZsMnVGAm3QlPfo4jE1IteKMsZdTIlMNfZxK0GOqYBlzVaPWurlITUQ9fD6qPRfkmQf7fDz6E3SeZmJL1Th7AsCeqrc7FcfXTlPiKuN0bdyQTzvuBqLXz8VePM3uFvkJ7YKHX%2FpJVbneAr6roSNkdeCfQWUVMarQbx5VGTpcFm5OL90UKA70%2FRZwNqTSh4fMrPX67K2CHVvAjfJRMYWtxgh3pyy3zBhlYVr1Cznvb9B7a4CAya6cWpH6or4sygNr9N%2F3j5Cg%3D%3D&X-Amz-Signature=29461639d7c9b99d2882bf320edf74bb9eb339bc83960efcb091137cde072fc1",
            "https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-005.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAZXWHO2DFCXZI6L74%2F20240124%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240124T152931Z&X-Amz-Expires=30&X-Amz-SignedHeaders=host&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEMD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJHMEUCIQD9umkGW4y8w9KflH99hmyCp9mbt5kTM8kPBMnZFOr3SQIgB%2BVRQgWjb2BBXVOK2aUqpW3%2FzQyyQqYQBNnziECms3EqxgMIeRADGgw2NjkzNTk0NjA1NTQiDNXvTxeLQL3cPRKr2iqjAzo55V1HYNQyU6FNc3B%2BT91R9%2F63AInTHPwkQFyHJh1vODo%2BN31hYTB754N2iZgSMx%2BKh0bBFmfSmc%2BSe6rfrFXugDmYQELqETmRMBxAtqcYlK11MJHpgk9u2WwNINLafj5LhzCvknyGmQG27uOAGvLLITk6SpTSB6gcsSMF56VuGZ4Wi3yrM6ThiDGxsRsJj0UwFRUZ9nQAkqlrKYAAkLO8rpuo575dWaDSzZIlR4zuC3IZPH2kIUKdJ0PvhVlhT0L2GJ%2FC94lcaHOJ29G%2FtzwXEnDhm9bE51eb%2FZrpGGN8feemKUc0RDhuAUPxNYFptHf0RfVVdwnkwrR9I%2BexISdmiGtZn%2BENrKVObCSN4W1mEfxL1LRme9iDeph9HS51ztXj%2B0XRtO1PU9ZfZVvmAznzSrxj2LLB4Ilx6wP5IONCXXg7o9k36lghYNYwWkNDsKUBaEGqvzcoxUTquJbwSgWzChQ97zBzVI2v7RD9ewsHVHpj46mR7TBeTRpFYQZPvFrCQo7QHVVj3%2BlT1g6ZsMnVGAm3QlPfo4jE1IteKMsZdTIlMNfZxK0GOqYBlzVaPWurlITUQ9fD6qPRfkmQf7fDz6E3SeZmJL1Th7AsCeqrc7FcfXTlPiKuN0bdyQTzvuBqLXz8VePM3uFvkJ7YKHX%2FpJVbneAr6roSNkdeCfQWUVMarQbx5VGTpcFm5OL90UKA70%2FRZwNqTSh4fMrPX67K2CHVvAjfJRMYWtxgh3pyy3zBhlYVr1Cznvb9B7a4CAya6cWpH6or4sygNr9N%2F3j5Cg%3D%3D&X-Amz-Signature=7ce49c9dca390e5facd4de6f43f9fcab93312b488e9dd11deb839023565f0cc9",
            "https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-006.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAZXWHO2DFCXZI6L74%2F20240124%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240124T152931Z&X-Amz-Expires=30&X-Amz-SignedHeaders=host&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEMD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJHMEUCIQD9umkGW4y8w9KflH99hmyCp9mbt5kTM8kPBMnZFOr3SQIgB%2BVRQgWjb2BBXVOK2aUqpW3%2FzQyyQqYQBNnziECms3EqxgMIeRADGgw2NjkzNTk0NjA1NTQiDNXvTxeLQL3cPRKr2iqjAzo55V1HYNQyU6FNc3B%2BT91R9%2F63AInTHPwkQFyHJh1vODo%2BN31hYTB754N2iZgSMx%2BKh0bBFmfSmc%2BSe6rfrFXugDmYQELqETmRMBxAtqcYlK11MJHpgk9u2WwNINLafj5LhzCvknyGmQG27uOAGvLLITk6SpTSB6gcsSMF56VuGZ4Wi3yrM6ThiDGxsRsJj0UwFRUZ9nQAkqlrKYAAkLO8rpuo575dWaDSzZIlR4zuC3IZPH2kIUKdJ0PvhVlhT0L2GJ%2FC94lcaHOJ29G%2FtzwXEnDhm9bE51eb%2FZrpGGN8feemKUc0RDhuAUPxNYFptHf0RfVVdwnkwrR9I%2BexISdmiGtZn%2BENrKVObCSN4W1mEfxL1LRme9iDeph9HS51ztXj%2B0XRtO1PU9ZfZVvmAznzSrxj2LLB4Ilx6wP5IONCXXg7o9k36lghYNYwWkNDsKUBaEGqvzcoxUTquJbwSgWzChQ97zBzVI2v7RD9ewsHVHpj46mR7TBeTRpFYQZPvFrCQo7QHVVj3%2BlT1g6ZsMnVGAm3QlPfo4jE1IteKMsZdTIlMNfZxK0GOqYBlzVaPWurlITUQ9fD6qPRfkmQf7fDz6E3SeZmJL1Th7AsCeqrc7FcfXTlPiKuN0bdyQTzvuBqLXz8VePM3uFvkJ7YKHX%2FpJVbneAr6roSNkdeCfQWUVMarQbx5VGTpcFm5OL90UKA70%2FRZwNqTSh4fMrPX67K2CHVvAjfJRMYWtxgh3pyy3zBhlYVr1Cznvb9B7a4CAya6cWpH6or4sygNr9N%2F3j5Cg%3D%3D&X-Amz-Signature=719d35a1cb73a68a2cfd9c36a03ab25c8196822dbcdafdc5379b003f6bf30890",
            "https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-007.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAZXWHO2DFCXZI6L74%2F20240124%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240124T152931Z&X-Amz-Expires=30&X-Amz-SignedHeaders=host&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEMD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJHMEUCIQD9umkGW4y8w9KflH99hmyCp9mbt5kTM8kPBMnZFOr3SQIgB%2BVRQgWjb2BBXVOK2aUqpW3%2FzQyyQqYQBNnziECms3EqxgMIeRADGgw2NjkzNTk0NjA1NTQiDNXvTxeLQL3cPRKr2iqjAzo55V1HYNQyU6FNc3B%2BT91R9%2F63AInTHPwkQFyHJh1vODo%2BN31hYTB754N2iZgSMx%2BKh0bBFmfSmc%2BSe6rfrFXugDmYQELqETmRMBxAtqcYlK11MJHpgk9u2WwNINLafj5LhzCvknyGmQG27uOAGvLLITk6SpTSB6gcsSMF56VuGZ4Wi3yrM6ThiDGxsRsJj0UwFRUZ9nQAkqlrKYAAkLO8rpuo575dWaDSzZIlR4zuC3IZPH2kIUKdJ0PvhVlhT0L2GJ%2FC94lcaHOJ29G%2FtzwXEnDhm9bE51eb%2FZrpGGN8feemKUc0RDhuAUPxNYFptHf0RfVVdwnkwrR9I%2BexISdmiGtZn%2BENrKVObCSN4W1mEfxL1LRme9iDeph9HS51ztXj%2B0XRtO1PU9ZfZVvmAznzSrxj2LLB4Ilx6wP5IONCXXg7o9k36lghYNYwWkNDsKUBaEGqvzcoxUTquJbwSgWzChQ97zBzVI2v7RD9ewsHVHpj46mR7TBeTRpFYQZPvFrCQo7QHVVj3%2BlT1g6ZsMnVGAm3QlPfo4jE1IteKMsZdTIlMNfZxK0GOqYBlzVaPWurlITUQ9fD6qPRfkmQf7fDz6E3SeZmJL1Th7AsCeqrc7FcfXTlPiKuN0bdyQTzvuBqLXz8VePM3uFvkJ7YKHX%2FpJVbneAr6roSNkdeCfQWUVMarQbx5VGTpcFm5OL90UKA70%2FRZwNqTSh4fMrPX67K2CHVvAjfJRMYWtxgh3pyy3zBhlYVr1Cznvb9B7a4CAya6cWpH6or4sygNr9N%2F3j5Cg%3D%3D&X-Amz-Signature=3a17b28f637d04becf05aa30630e513c35963920486b906b2c0533e700f7c6fd",
            "https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-008.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAZXWHO2DFCXZI6L74%2F20240124%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20240124T152931Z&X-Amz-Expires=30&X-Amz-SignedHeaders=host&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEMD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMiJHMEUCIQD9umkGW4y8w9KflH99hmyCp9mbt5kTM8kPBMnZFOr3SQIgB%2BVRQgWjb2BBXVOK2aUqpW3%2FzQyyQqYQBNnziECms3EqxgMIeRADGgw2NjkzNTk0NjA1NTQiDNXvTxeLQL3cPRKr2iqjAzo55V1HYNQyU6FNc3B%2BT91R9%2F63AInTHPwkQFyHJh1vODo%2BN31hYTB754N2iZgSMx%2BKh0bBFmfSmc%2BSe6rfrFXugDmYQELqETmRMBxAtqcYlK11MJHpgk9u2WwNINLafj5LhzCvknyGmQG27uOAGvLLITk6SpTSB6gcsSMF56VuGZ4Wi3yrM6ThiDGxsRsJj0UwFRUZ9nQAkqlrKYAAkLO8rpuo575dWaDSzZIlR4zuC3IZPH2kIUKdJ0PvhVlhT0L2GJ%2FC94lcaHOJ29G%2FtzwXEnDhm9bE51eb%2FZrpGGN8feemKUc0RDhuAUPxNYFptHf0RfVVdwnkwrR9I%2BexISdmiGtZn%2BENrKVObCSN4W1mEfxL1LRme9iDeph9HS51ztXj%2B0XRtO1PU9ZfZVvmAznzSrxj2LLB4Ilx6wP5IONCXXg7o9k36lghYNYwWkNDsKUBaEGqvzcoxUTquJbwSgWzChQ97zBzVI2v7RD9ewsHVHpj46mR7TBeTRpFYQZPvFrCQo7QHVVj3%2BlT1g6ZsMnVGAm3QlPfo4jE1IteKMsZdTIlMNfZxK0GOqYBlzVaPWurlITUQ9fD6qPRfkmQf7fDz6E3SeZmJL1Th7AsCeqrc7FcfXTlPiKuN0bdyQTzvuBqLXz8VePM3uFvkJ7YKHX%2FpJVbneAr6roSNkdeCfQWUVMarQbx5VGTpcFm5OL90UKA70%2FRZwNqTSh4fMrPX67K2CHVvAjfJRMYWtxgh3pyy3zBhlYVr1Cznvb9B7a4CAya6cWpH6or4sygNr9N%2F3j5Cg%3D%3D&X-Amz-Signature=9844fd6ff0b437858a71f3c8a404e7c96a330d68c86fdf2e11cc4b00d7f27e76",
        ]
    },
    "status": "created",
    "insertCount": 0,
    "invalidCount": 0,
    "log": None,
    "addedAt": "2024-01-17T12:27:41.411Z",
    "deletedAt": None,
}
```

:::
::::

```{toctree}
:hidden:
aws_s3_signing.md
```
