"""Unit tests for Ingest S3URLPresigner"""
import os

import pytest

from dfi.services.ingest import S3URLPresigner

TEST_DATASET_S3_BUCKET = "dev-ta-platform-dev-datasets"
TEST_DATASET_S3_PREFIX = "test/integration-tests/100k_with_filter_fields_epoc_2023-11-08"
TEST_DATASET_S3_REGION = "eu-west-2"
AWS_PROFILE = os.environ["AWS_PROFILE"]  # TODO change this once dev-ops have enabled AWS SSO access


@pytest.fixture(name="s3_presigner", scope="module")
def get_s3_presigner() -> str:
    return S3URLPresigner(TEST_DATASET_S3_BUCKET, TEST_DATASET_S3_REGION, AWS_PROFILE)


def test_find_files(s3_presigner: S3URLPresigner) -> None:
    files = s3_presigner.find_files(TEST_DATASET_S3_PREFIX, ".csv")
    assert len(files) == 9


def test_generate_presigned_url(s3_presigner: S3URLPresigner) -> None:
    object_key = (
        TEST_DATASET_S3_PREFIX + "part-00000-tid-5340177895144353459-94c97a44-a2b7-4587-99f9-80b3dcbda512-26-1-c000.csv"
    )
    signed_url = s3_presigner.generate_presigned_url(object_key, expiration=1)
    assert isinstance(signed_url, str)


def test_generate_presigned_urls(s3_presigner: S3URLPresigner) -> None:
    signed_urls = s3_presigner.generate_presigned_urls(TEST_DATASET_S3_PREFIX, ".csv", expiration=1)
    assert len(signed_urls) == 9
