import pandas as pd
from dfi.services.query import Query
from dfi.errors import InvalidQueryDocument

from dfi.services.sql_state.state import SQLQueryDocument
from dfi.services.sql_state.state_select import StateSelect
from dfi.services.sql_state.state_insert import StateInsert


class QueryDocumentBuilder:
    state_map = {
        "select": StateSelect,
        "insert": StateInsert,
    }

    def __init__(self, sql: str):
        self.document = SQLQueryDocument()

        statements = sql.split(";")
        if len(statements) > 1 and len(statements[1]):
            raise RuntimeError("Only a single sql statement is supported")

        self._tokenise(statements[0])
        self._parse()

    def _tokenise(self, statement: str):
        self.tokens = statement.strip().split()
        self._group_quoted_strings()

    def _group_quoted_strings(self):
        tokens = []
        while self.tokens:
            token = self.tokens.pop(0)
            quote_count = token.count("'")
            if quote_count == 1:
                next_token = self.tokens.pop(0)
                tokens.append(f"{token} {next_token}")
            else:
                tokens.append(token)

        self.tokens = tokens

    def _parse(self):
        token = self.tokens[0].lower()
        if token in QueryDocumentBuilder.state_map:
            state = QueryDocumentBuilder.state_map[token]()
            state.parse(self.document, self.tokens[1:])
        else:
            raise RuntimeError(f"Unknown first keyword: {token}")

    def __validate(self):
        return self.document.dataset_id is not None

    def build(self):
        if not self.__validate():
            raise InvalidQueryDocument("SQL Query has not generated a valid query document")

        query_document = {
            "datasetId": self.document.dataset_id,
        }

        if len(self.document["return"]):
            query_document["return"] = self.document["return"]
        if len(self.document["filters"]):
            query_document["filters"] = self.document["filters"]

        return query_document


class Sql:
    def __init__(self, query: Query):
        self.__q = query

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    def __str__(self) -> str:
        return f"""Instance of dfi.{self.__class__.__name__}"""

    def query(self, sql: str) -> pd.DataFrame:
        builder = QueryDocumentBuilder(sql)
        query_document = builder.build()
        return self.__q.raw_request(query_document)
