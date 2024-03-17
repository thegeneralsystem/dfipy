test_data = [
    (
        "Get all records. Normally a bad idea",
        # To support hyphens, use single quoted table names
        "select records from 'gs'.'big-data';",
        {
            "datasetId": "gs.big-data",
            "return": {"type": "records"},
        },
    ),
    (
        "Count all records",
        "select count from 'gs'.'big-data';",
        {
            "datasetId": "gs.big-data",
            "return": {"type": "count"},
        },
    ),
    (
        "Get all records that match a single filter field",
        "select records from 'gs'.'big-data' where signalStrength < 30;",
        {
            "datasetId": "gs.big-data",
            "filters": {
                "fields": {
                    "signalStrength": {"lt": 30},
                }
            },
            "return": {"type": "records"},
        },
    ),
    (
        "Count all records that match all filter fields",
        "select count "
        "from 'gs'.'big-data' "
        "where ip = '10.192.43.111' "
        "and signalStrength < 30 "
        "and source != NULL "
        ";",
        {
            "datasetId": "gs.big-data",
            "filters": {
                "fields": {
                    "ip": {"eq": "10.192.43.111"},
                    "signalStrength": {"lt": 30},
                    "source": {"neq": None},
                }
            },
            "return": {"type": "count"},
        },
    ),
    (
        "Handle operator with spaces",
        "select count from 'gs'.'big-data' where ip = '10.192.43.111';",
        {
            "datasetId": "gs.big-data",
            "filters": {
                "fields": {
                    "ip": {"eq": "10.192.43.111"},
                }
            },
            "return": {"type": "count"},
        },
    ),
    (
        "Handle operator without spaces",
        "select count from 'gs'.'big-data' where ip='10.192.43.111';",
        {
            "datasetId": "gs.big-data",
            "filters": {
                "fields": {
                    "ip": {"eq": "10.192.43.111"},
                }
            },
            "return": {"type": "count"},
        },
    ),
    (
        "Handle 'between'",
        "select count "
        "from 'gs'.'big-data' "
        "where accuracyInMeters between 50 and 75 "
        "and ip = '10.192.43.111' "
        ";",
        {
            "datasetId": "gs.big-data",
            "filters": {
                "fields": {
                    "accuracyInMeters": {"between": [50, 75]},
                    "ip": {"eq": "10.192.43.111"},
                }
            },
            "return": {"type": "count"},
        },
    ),
    # Expressed with WKT: https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
    (
        "Count all records in a polygon",
        "select records "
        "from 'gs'.'big-data' "
        "where POLYGON(("
        "-3.2018689 55.9478931, "
        "-3.2002789 55.9450483, "
        "-3.1739289 55.9504792, "
        "-3.1757763 55.9528911, "
        "-3.2018689 55.9478931"
        "))"
        ";",
        {
            "datasetId": "gs.big-data",
            "filters": {
                "geo": {
                    "coordinates": [
                        [-3.2018689, 55.9478931],
                        [-3.2002789, 55.9450483],
                        [-3.1739289, 55.9504792],
                        [-3.1757763, 55.9528911],
                        [-3.2018689, 55.9478931],
                    ],
                    "type": "Polygon",
                }
            },
            "return": {"type": "records"},
        },
    ),
    # (
    #     "Find the newest record for an id before this time",
    #     "select newest from 'gs'.'big-data' where time < '2023-02-28 23:59:59.999';",
    #     {
    #         "datasetId": "gs.big-data",
    #         "filters": {"only": "newest", "time": {"maxTime": "2023-02-28T23:59:59.999Z"}},
    #         "return": {"type": "records"},
    #     },
    # ),
    # (
    #     "Find the oldest record for an id after this time",
    #     "select oldest from 'gs'.'big-data' where time > '2023-02-28 23:59:59.999';",
    #     {
    #         "datasetId": "gs.big-data",
    #         "filters": {"only": "oldest", "time": {"minTime": "2023-02-28T23:59:59.999Z"}},
    #         "return": {"type": "records"},
    #     },
    # ),
    (
        "Find all records between two dates",
        "select records from 'gs'.'big-data' where time between '2023-01-01' and '2023-02-28';",
        {
            "datasetId": "gs.big-data",
            "filters": {"time": {"maxTime": "2023-02-28T00:00:00.000Z", "minTime": "2023-01-01T00:00:00.000Z"}},
            "return": {"type": "records"},
        },
    ),
    (
        "Find all records between two milliseconds",
        "select records "
        "from 'gs'.'big-data' "
        "where time between '2023-01-01 00:00:00.000' and '2023-02-28 23:59:59.999' "
        ";",
        {
            "datasetId": "gs.big-data",
            "filters": {"time": {"maxTime": "2023-02-28T23:59:59.999Z", "minTime": "2023-01-01T00:00:00.000Z"}},
            "return": {"type": "records"},
        },
    ),
    (
        "Find all records for an id",
        "select records from 'gs'.'big-data' where id='351ab753-d029-4412-81b8-e53eeee3d825';",
        {
            "datasetId": "gs.big-data",
            "filters": {"id": ["351ab753-d029-4412-81b8-e53eeee3d825"]},
            "return": {"type": "records"},
        },
    ),
    (
        "Return the metadataId for each record as well as the core fields",
        "select records, metadataId, fields "
        "from 'gs'.'big-data' "
        "where id='351ab753-d029-4412-81b8-e53eeee3d825'"
        ";",
        {
            "datasetId": "gs.big-data",
            "filters": {"id": ["351ab753-d029-4412-81b8-e53eeee3d825"]},
            "return": {"include": ["metadataId", "fields"], "type": "records"},
        },
    ),
    (
        "Return the metadataId and fields, different order",
        "select fields, records, metadataId "
        "from 'gs'.'big-data' "
        "where id='351ab753-d029-4412-81b8-e53eeee3d825'"
        ";",
        {
            "datasetId": "gs.big-data",
            "filters": {"id": ["351ab753-d029-4412-81b8-e53eeee3d825"]},
            "return": {"include": ["fields", "metadataId"], "type": "records"},
        },
    ),
    (
        "'Select *' is shorthand for 'select records, metadataId, fields'",
        "select * from 'gs'.'big-data' where id='351ab753-d029-4412-81b8-e53eeee3d825';",
        {
            "datasetId": "gs.big-data",
            "filters": {"id": ["351ab753-d029-4412-81b8-e53eeee3d825"]},
            "return": {"include": ["metadataId", "fields"], "type": "records"},
        },
    ),
    (
        "Time filter and Group by",
        "select count from 'gs'.'big-data' "
        "where time between '2023-01-01 00:00:00.000' and '2023-02-28 23:59:59.999' "
        "group by uniqueId;",
        {
            "datasetId": "gs.big-data",
            "filters": {"time": {"maxTime": "2023-02-28T23:59:59.999Z", "minTime": "2023-01-01T00:00:00.000Z"}},
            "return": {
                "type": "count",
                "groupBy": {
                    "type": "uniqueId"
                }, 
            },
        },
    ),
]
