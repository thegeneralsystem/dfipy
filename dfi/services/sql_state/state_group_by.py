from dfi.services.sql_state.state import State, SQLQueryDocument


class StateGroupBy(State):
    def parse(self, doc: SQLQueryDocument, tokens: list[str]):
        if tokens[1].lower() != "uniqueid":
            raise RuntimeError("Only uniqueId is valid for group by")
        
        doc["return"].update({
            "groupBy": {
                "type": "uniqueId",
            }
        })
