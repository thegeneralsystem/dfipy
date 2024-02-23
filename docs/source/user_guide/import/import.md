(importing-data)=

# Importing Data

You can create and manage data import jobs using the API. The key steps are:

1. Map the relevant fields in your data to the [dataset's schema](#dataset-schema-retrieval) registered with the DFI
2. Verify the import with a [dry run](#import-dry-run)
3. Start an import job either [from URLs](#importing-data-from-urls) or [from AWS S3](#importing-data-from-aws-s3)
4. Monitor the [status](#import-status) of the import
5. [Abort](#aborting-an-import) a running import if needed

There are two options for importing data from external sources: [from URLs](#importing-data-from-urls) and [from AWS S3](#importing-data-from-aws-s3). When importing data from URLs, the URLs should be publicly accessible. When importing from S3, the import service will need to be configured with access to the S3 bucket.

## Time Ordered Ingestion

To achieve optimal query performance, the data to be ingested should be in roughly time
order. Data is typically available in this form from streaming sources and, more generally,
from sensor-generated data. Ingestion speed is unaffected by time-ordering.

:::{hint}

- records within a file should be in increasing timestamp order
- if ingesting via a list of URLs, the URLs should be passed into the API in time order
  :::

```{toctree}
:hidden:
mapping_fields.md
dry_run.md
urls/urls.md
<!-- aws_s3.md -->
batch_info.md
batch_status.md
aborting.md
```
