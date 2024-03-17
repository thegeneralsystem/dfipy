(sql-interface)=

# DFISQL (Alpha)

> **Note** - This is offered as a prototypical capability and is unsupported

SQL support is limited and uses a custom dialect.

* Supported (at least partially): `SELECT`, `FROM`, `WHERE`, `GROUP BY` (`uniqueId` only)
* Operators: `=`, `!=`, `<>`, `<`, `>`, `<=`, `>=`, `between`, `outside` (non-standard)    
* Not supported: `JOIN`, `INSERT`, `ORDER BY`

A finite state machine translates a single SQL statement into a DFI Query Document, then uses `dfi.query.raw_request` to perform the query.

Since the DFI always fetches all columns, we use `SELECT <columns>` to indicate the type of response we're interested in. Valid `columns` are:

* `count`: get a count of how many records there are
* `records`: get a list of full records.
* `metadataId`: return the metadataId field for each record as well as the core fields
* `fields`: return the filter field values for each record as well as the core fields.
* `*`: equivalent to using all of `records, metadataId, fields`

## Geometric queries
Polygons are described using the [Well Known Text](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry) representation of geometry

## Datasets
DFI datasets are loosely mapped to SQL tables. Its recommended to use single quotes around the namespace and dataset name, eg  `'gs'.'big-data'`.

## Examples:
```sql
-- Get all records. Normally a bad idea
SELECT records FROM 'gs'.'big-data';

-- Count all records
SELECT count FROM 'gs'.'big-data';

-- Get all records that match a single filter field
SELECT records FROM 'gs'.'big-data' WHERE signalStrength < 30;

-- Count all records that match all filter fields
SELECT count 
FROM 'gs'.'big-data'
WHERE ip='10.192.43.111'
AND signalStrength < 30
AND source != NULL;

-- Count records with a filter field BETWEEN two values
SELECT count
FROM 'gs'.'big-data'
WHERE accuracyInMeters BETWEEN 50 AND 75;
        
-- Count all records in a polygon using WKT syntax
SELECT records
FROM 'gs'.'big-data'
WHERE POLYGON((
    -3.2018689 55.9478931,
    -3.2002789 55.9450483,
    -3.1739289 55.9504792,
    -3.1757763 55.9528911,
    -3.2018689 55.9478931
));
       
-- Find all records BETWEEN two datetimes
SELECT records
FROM 'gs'.'big-data'
WHERE time BETWEEN '2023-01-01 00:00:00.000' AND '2023-02-28 23:59:59.999';

-- Find all records for an id
SELECT records FROM 'gs'.'big-data' WHERE id='351ab753-d029-4412-81b8-e53eeee3d825';

-- Return the metadataId for each record as well as the core fields
SELECT records, metadataId, fields
FROM 'gs'.'big-data'
WHERE id='351ab753-d029-4412-81b8-e53eeee3d825';

-- 'SELECT *' is shorthAND for 'SELECT records, metadataId, fields'
SELECT * FROM 'gs'.'big-data' WHERE id='351ab753-d029-4412-81b8-e53eeee3d825';
```