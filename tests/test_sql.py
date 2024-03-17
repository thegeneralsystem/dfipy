# Input: SQL query statement
# Output: DFI query doc

import pytest
import pprint
from dfi.services.sql import QueryDocumentBuilder
from tests.test_sql_data import test_data


@pytest.mark.parametrize("test_name,sql_statement,expected_query_doc", test_data)
def test_query_document_builder(test_name: str, sql_statement: str, expected_query_doc: dict):
    print("-" * 80)
    print(test_name)
    builder = QueryDocumentBuilder(sql_statement)
    actual = builder.build()

    pprint.pprint(actual)
    print("-" * 80)
    pprint.pprint(expected_query_doc)

    assert actual == expected_query_doc
