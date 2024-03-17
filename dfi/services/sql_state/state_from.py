from dfi.services.sql_state.state import State, SQLQueryDocument
from dfi.services.sql_state.state_where import StateWhere
from dfi.services.sql_state.state_group_by import StateGroupBy


class StateFrom(State):
    state_map = {
        "where": StateWhere,
        "group": StateGroupBy,
    }

    def parse(self, doc: SQLQueryDocument, tokens: list[str]):
        doc.dataset_id = self.strip_quotes(tokens[0])

        # Skip the table/dataset
        self.read_next_token(doc, tokens[1:], StateFrom.state_map)
