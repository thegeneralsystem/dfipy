from abc import ABC, abstractmethod
from datetime import datetime


class SQLQueryDocument(dict):
    def __init__(self) -> None:
        super().__setitem__("return", {})
        super().__setitem__("filters", {})


class State(ABC):
    @abstractmethod
    def parse(self, doc: SQLQueryDocument, tokens: list[str]):
        pass

    @staticmethod
    def read_next_token(doc: SQLQueryDocument, tokens: list[str], state_map: dict):
        if not tokens:
            return

        token = tokens[0].lower()

        if token in state_map:
            state = state_map[token]()
            state.parse(doc, tokens[1:])
        else:
            for state_name, state_cls in state_map.items():
                if token.startswith(state_name):
                    state = state_cls()
                    state.parse(doc, tokens[1:])
                    return

            raise RuntimeError(f"Unknown keyword: {token}")

    @staticmethod
    def strip_quotes(s: str):
        return s.replace('"', "").replace("`", "").replace("'", "")

    def strip_punctuation(s: str):
        return s.replace(",", "").replace(";", "")

    @staticmethod
    def cleanup_type(rhs: str) -> int | float | str | None:
        if rhs.lower() == "null":
            return None

        rhs = State.strip_punctuation(rhs)

        # Numeric?
        try:
            if "." in rhs:
                return float(rhs)
            else:
                return int(rhs)
        except:
            # Its a bit stringy
            rhs = State.strip_quotes(rhs)

            # Date?
            try:
                rhs: datetime = datetime.strptime(rhs, "%Y-%m-%d")
                return rhs.isoformat(timespec="milliseconds") + "Z"
            except:
                pass

            # Datetime?
            try:
                rhs: datetime = datetime.strptime(rhs, "%Y-%m-%d %H:%M:%S")
                return rhs.isoformat(timespec="milliseconds") + "Z"
            except:
                pass

            # Datetime with milliseconds?
            try:
                rhs: datetime = datetime.strptime(rhs, "%Y-%m-%d %H:%M:%S.%f")
                return rhs.isoformat(timespec="milliseconds") + "Z"
            except:
                pass

            # Ok, its definitely just a normal str
            return rhs

    @staticmethod
    def prep_filter_dict(doc: SQLQueryDocument, filter_name: str):
        if filter_name not in doc["filters"]:
            doc["filters"][filter_name] = {}
