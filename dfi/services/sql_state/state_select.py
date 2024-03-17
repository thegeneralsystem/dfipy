from dfi.services.sql_state.state import State, SQLQueryDocument
from dfi.services.sql_state.state_from import StateFrom


class StateSelect(State):
    state_map = {
        "from": StateFrom,
    }

    valid_columns = {
        "count": [("return", {"type": "count"})],
        "records": [("return", {"type": "records"})],
        "metadataId": [("return", {"include": ["metadataId"]})],
        "fields": [("return", {"include": ["fields"]})],
        "*": [
            ("return", {"type": "records", "include": ["metadataId", "fields"]})
        ],  # synonym for 'records, metadataId, fields',
        # "newest": [("filters", {"only": "newest"}), ("return", {"type": "records"})],
        # "oldest": [("filters", {"only": "oldest"}), ("return", {"type": "records"})],
    }

    def parse(self, doc: SQLQueryDocument, tokens: list[str]):
        columns = []

        # Look for next keyword
        for i, token in enumerate(tokens):
            if token not in StateSelect.state_map.keys():
                columns.append(token.replace(",", "").strip())
            else:
                break

        for column in columns:
            sub_dicts = StateSelect.valid_columns[column]

            for d in sub_dicts:
                sub_dict_name, sub_dict = d
                # include is a special case as its a list which may need extending
                if "include" in sub_dict and "include" in doc[sub_dict_name]:
                    doc[sub_dict_name]["include"].append(sub_dict["include"][0])
                else:
                    doc[sub_dict_name].update(sub_dict)

        self.read_next_token(doc, tokens[i:], StateSelect.state_map)
