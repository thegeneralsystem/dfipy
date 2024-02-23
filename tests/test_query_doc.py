import json
import os
import unittest
import urllib.parse
from datetime import datetime
from pathlib import Path

from dfi.query_document_v0 import FilterOperator, QueryDocument
from dfi.validate import DFIInputValueError


def test_query_document_matches():
    new_document = QueryDocument()
    document_path = Path(os.getcwd(), "tests", "query_documents", "generic_doc.json")
    expected_document = json.load(open(document_path))

    time = (datetime(2023, 10, 26, 10, 46, 13, 439985), datetime(2023, 10, 26, 12, 46, 13, 439989))
    vertices = [[1.0, 2.0], [3.0, -1.0], [4.0, -2.0], [1.0, 2.0]]
    new_document.set_time_range(time_interval=time)
    new_document.set_polygon(vertices=vertices)

    new_document.set_id_filter(ids=["1234", "5678"])
    new_document.add_filter_field("creditCardProvider", FilterOperator.eq, "american_express")
    new_document.add_filter_field("transportationMode", "eq", "walking")
    assert expected_document == new_document.get_document()


def test_insert_multiple_filter_fields():
    new_doc = QueryDocument()

    to_insert = dict(creditCardProvider=dict(eq="american_express"), transportationMode=dict(eq="walking"))
    new_doc.add_filter_fields_from_dict(to_insert)
    expected = dict(creditCardProvider=dict(eq="american_express"), transportationMode=dict(eq="walking"))
    assert new_doc.get_document()["filters"]["fields"] == expected


class TestInvalidFilterFieldRaises(unittest.TestCase):
    def test_exception(self):
        new_doc = QueryDocument()
        with self.assertRaises(DFIInputValueError):
            new_doc.add_filter_field("creditCardProvider", "nonsense", "1")


def test_create_query_params_from_filter_fields():
    """For the migration period filter fields will sometimes have to be passed as query parameters to a url"""
    new_document = QueryDocument()
    new_document.add_filter_field("creditCardProvider", "eq", "american_express")
    new_document.add_filter_field("transportationMode", "eq", "walking")
    get_fields = new_document.filter_fields_url_encoding()
    expected = "creditCardProvider%5Beq%5D=%22american_express%22&transportationMode%5Beq%5D=%22walking%22"
    assert urllib.parse.urlencode(get_fields) == expected


def test_create_query_params_from_filter_fields_quote_spaces():
    new_document = QueryDocument()
    new_document.add_filter_field("creditCardProvider", "eq", "american_express")
    # Spaces and special characters in the url should be handled
    new_document.add_filter_field("transportationMode", "eq", 'wal"kin g')
    expected = "creditCardProvider%5Beq%5D=%22american_express%22&transportationMode%5Beq%5D=%22wal%5C%22kin+g%22"
    assert urllib.parse.urlencode(new_document.filter_fields_url_encoding()) == expected
