"""Unit tests for Ingest construction classes."""

from dfi.services.ingest import AWSCredentials, BatchS3Files, BatchURLFiles, CSVFormat


def test_aws_credentials_builder() -> None:
    role_arn = "arn:aws:s3:::example_bucket/example_key"
    aws_credentials = AWSCredentials(role_arn).build()

    expected = {"RoleArn": "arn:aws:s3:::example_bucket/example_key"}

    assert aws_credentials == expected


def test_batch_url_files_builder() -> None:
    urls = ["www.example-0.com", "www.example-1.com", "www.example-2.com", "www.example-3.com"]
    batch_url_files = BatchURLFiles(urls).build()

    expected = {"urls": ["www.example-0.com", "www.example-1.com", "www.example-2.com", "www.example-3.com"]}

    assert batch_url_files == expected


def test_batch_s3_files_builder() -> None:
    role_arn = "arn:aws:s3:::example_bucket/example_key"
    credentials = AWSCredentials(role_arn)
    bucket = "s3://bucket-name"
    glob = "*.csv"
    prefix = "sample-data"

    batch_s3_files = BatchS3Files(bucket, credentials, glob, prefix).build()

    expected = {
        "s3": {
            "bucket": "s3://bucket-name",
            "credentials": {"RoleArn": "arn:aws:s3:::example_bucket/example_key"},
            "glob": "*.csv",
            "prefix": "sample-data",
        }
    }

    assert batch_s3_files == expected


def test_csv_format_builder() -> None:
    # required fields
    entity_id = 0
    timestamp = 1
    longitude = 2
    latitude = 3

    # extra fields
    ipv4 = 4
    age = 5
    home_ipv4 = 6
    route_id = 7
    credit_card_provider = 8
    transportation_mode = 9

    csv_format = CSVFormat(
        entity_id=entity_id,
        timestamp=timestamp,
        longitude=longitude,
        latitude=latitude,
        ipv4=ipv4,
        age=age,
        home_ipv4=home_ipv4,
        route_id=route_id,
        credit_card_provider=credit_card_provider,
        transportation_mode=transportation_mode,
    ).build()

    expected = {
        "csv": {
            "entityId": 0,
            "timestamp": 1,
            "longitude": 2,
            "latitude": 3,
            "ipv4": 4,
            "age": 5,
            "home_ipv4": 6,
            "route_id": 7,
            "credit_card_provider": 8,
            "transportation_mode": 9,
        }
    }

    assert csv_format == expected
