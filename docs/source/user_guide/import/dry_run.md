(import-dry-run)=

# Verifying with a Dry Run

Before kicking off an import, it can be useful to verify if everything is setup properly. This is especially useful when importing a large dataset because one ill-formatted file can cause some headaches when an import has been running for a few hours already. To alleviate any concerns about formatting, we can do a dry run of the import to verify each file in the batch. When performing an import dry run, the first 100 rows of each file will be verified against the dataset schema being imported to.

**Error Reporting:**

- Per row errors will be collected in a report: for each column all rows are listed for which that column is invalid.
- If there is a problem with the schema itself, an 'error' will be listed in the report but no invalid rows, this is because if there is a problem with the schema, then it is not possible to determine which rows are valid or not.
- If there is a schema error, there will be an error listed for each batch.

**Common Errors:**

- Input csv columns specify a column index that is out of bounds for the data.
- Column value does not match schema field type.
- Null value in non-nullable field.

:::{attention}
During an import, if a bad row is found, it is skipped and reported. If a corrupt or ill-formatted file is attempted to be imported, the import service will fail, even after it has successfully processed a large number of files. When this happens, the data ingested successfully prior to the failure is not rolled back.
:::

## Example I: Success

::::{tab-set}

:::{tab-item} dfipy
:sync: dfipy

```python
urls = [
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
report = dfi.ingest.put_batch(
    dataset_id=<dataset_id>,
    source=source,
    file_format=csv_format,
    dry_run=False,
    log_metrics=False
)
print(report)
```

```python
{
    "status": "success",
    "report": "Valid rows: 100\nInvalid rows dropped: 0\n\nErrors:\n\n\nValid rows: 100\nInvalid rows dropped: 0\n\nErrors:\n\n\nValid rows: 100\nInvalid rows dropped: 0\n\nErrors:\n",
    "log": "2024-01-25T08:34:49.113Z INFO Starting dry run\n2024-01-25T08:34:49.118Z INFO Using 3 parallel streams\n2024-01-25T08:34:49.133Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-000.csv\n2024-01-25T08:34:49.135Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-001.csv\n2024-01-25T08:34:49.136Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-002.csv\n2024-01-25T08:34:49.693Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-003.csv\n2024-01-25T08:34:49.767Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-004.csv\n2024-01-25T08:34:49.808Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-005.csv\n2024-01-25T08:34:49.986Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-006.csv\n2024-01-25T08:34:50.082Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-007.csv\n2024-01-25T08:34:50.281Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-008.csv",
}
```

:::
::::

To read the dry run report, we can print and format it.

::::{tab-set}
:::{tab-item} dfipy
:sync: dfipy

```python
print(report["report"])
```

```text
Valid rows: 100
Invalid rows dropped: 0

Errors:


Valid rows: 100
Invalid rows dropped: 0

Errors:


Valid rows: 100
Invalid rows dropped: 0

Errors:
```

:::
::::

There were 3 imports used to check the files. The first 100 rows of each file were checked and found to be valid for the dataset's schema. We could now kick off the full import with confidence that the files are the correct schema.

:::{note}
The dry run only checks the first 100 rows bye default, it does not check every record that will be ingested. If a record is attempted to be ingested during the import, but does not match the schema (e.g. a wild null value appears in a non-nullable field) the record will be skipped, the incident logged, and the import will keep calm and carry on.
:::

## Example II: Error

In this example, we've added a `broken.csv` to the batch of files files to be imported. The file is broken because there is a missing value in the timestamp field on the second row:

```text
aca5597c-8666-43bf-9c85-0b575ece58ed,1640995676000,51.54191120617028,-0.1136967540230455,,,,0,,dwelling
aca5597c-8666-43bf-9c85-0b575ece58ed,,51.54201796566859,-0.1135628381946958,,,,0,,dwelling
aca5597c-8666-43bf-9c85-0b575ece58ed,1640995694000,51.54185742565869,-0.1136623400329315,,,,0,,dwelling
aca5597c-8666-43bf-9c85-0b575ece58ed,1640995697000,51.542017930249976,-0.1135929190644742,,,,0,,dwelling
aca5597c-8666-43bf-9c85-0b575ece58ed,1640995700000,51.54181738011452,-0.1136776509308499,,,,0,,dwelling
```

- explain what checks / validation are done during dryrun
  - field types match dataset schema
  - checks first 100 rows
- what gets reported
- success / failure / other?

::::{tab-set}

:::{tab-item} dfipy
:sync: dfipy

```python
report = dfi.ingest.put_batch(..., dry_run=True)
print(report)
```

```python
{
    "status": "error",
    "report": "Valid rows: 100\nInvalid rows dropped: 1\n\nErrors:\n\nDropped Rows:\n\n* Rows dropped with invalid column timestamp\n\nuid,timestamp,longitude,latitude,ipv4,age,home_ipv4,route_id,credit_card_provider,transportation_mode\naca5597c-8666-43bf-9c85-0b575ece58ed,,51.54201796566859,-0.1135628381946958,,,,0,,dwelling\n\n\nValid rows: 100\nInvalid rows dropped: 0\n\nErrors:\n\n\nValid rows: 100\nInvalid rows dropped: 0\n\nErrors:\n",
    "log": "2024-01-25T13:29:12.944Z INFO Starting dry run\n2024-01-25T13:29:12.949Z INFO Using 3 parallel streams\n2024-01-25T13:29:12.980Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/broken.csv\n2024-01-25T13:29:12.986Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-000.csv\n2024-01-25T13:29:12.987Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-001.csv\n2024-01-25T13:29:13.620Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-002.csv\n2024-01-25T13:29:13.648Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-003.csv\n2024-01-25T13:29:13.653Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-004.csv\n2024-01-25T13:29:13.833Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-005.csv\n2024-01-25T13:29:13.842Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-006.csv\n2024-01-25T13:29:13.949Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-007.csv\n2024-01-25T13:29:13.965Z INFO Fetching url https://datasets.s3.amazonaws.com/1B_with_filter_fields/file-008.csv",
}
```

The `report` explains the errors found during the dry run.

```python
print(report["report"])
```

```text
Valid rows: 100
Invalid rows dropped: 1

Errors:

Dropped Rows:

* Rows dropped with invalid column timestamp

uid,timestamp,longitude,latitude,ipv4,age,home_ipv4,route_id,credit_card_provider,transportation_mode
aca5597c-8666-43bf-9c85-0b575ece58ed,,51.54201796566859,-0.1135628381946958,,,,0,,dwelling


Valid rows: 100
Invalid rows dropped: 0

Errors:


Valid rows: 100
Invalid rows dropped: 0

Errors:
```

```python
print(report["log"])
```

```text
2024-01-25T13:29:12.944Z INFO Starting dry run
2024-01-25T13:29:12.949Z INFO Using 3 parallel streams
2024-01-25T13:29:12.980Z INFO Fetching url https://dev-ta-platform-dev-datasets.s3.amazonaws.com/1B_with_filter_fields/broken.csv
2024-01-25T13:29:12.986Z INFO Fetching url https://dev-ta-platform-dev-datasets.s3.amazonaws.com/1B_with_filter_fields/file-000.csv
2024-01-25T13:29:12.987Z INFO Fetching url https://dev-ta-platform-dev-datasets.s3.amazonaws.com/1B_with_filter_fields/file-001.csv
2024-01-25T13:29:13.620Z INFO Fetching url https://dev-ta-platform-dev-datasets.s3.amazonaws.com/1B_with_filter_fields/file-002.csv
2024-01-25T13:29:13.648Z INFO Fetching url https://dev-ta-platform-dev-datasets.s3.amazonaws.com/1B_with_filter_fields/file-003.csv
2024-01-25T13:29:13.653Z INFO Fetching url https://dev-ta-platform-dev-datasets.s3.amazonaws.com/1B_with_filter_fields/file-004.csv
2024-01-25T13:29:13.833Z INFO Fetching url https://dev-ta-platform-dev-datasets.s3.amazonaws.com/1B_with_filter_fields/file-005.csv
2024-01-25T13:29:13.842Z INFO Fetching url https://dev-ta-platform-dev-datasets.s3.amazonaws.com/1B_with_filter_fields/file-006.csv
2024-01-25T13:29:13.949Z INFO Fetching url https://dev-ta-platform-dev-datasets.s3.amazonaws.com/1B_with_filter_fields/file-007.csv
2024-01-25T13:29:13.965Z INFO Fetching url https://dev-ta-platform-dev-datasets.s3.amazonaws.com/1B_with_filter_fields/file-008.csv
```

:::
::::
