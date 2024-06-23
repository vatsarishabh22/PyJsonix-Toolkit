from dataclasses import dataclass
from typing import List, Dict, Union
from .analysis import value_counts

@dataclass
class JSONFrame:
    shape: tuple
    skeleton: dict
    fields: List[str]
    data: List[dict]

    def __getitem__(self, fields: Union[str, List[str]]):
        if isinstance(fields, str):
            fields = [fields]
        filtered_data = []
        for record in self.data:
            filtered_record = {}
            for field in fields:
                value = self._access_value(record, field)
                if value is not None:
                    self._set_value(filtered_record, field, value)
            filtered_data.append(filtered_record)
        return JSONFrame(
            shape=(len(filtered_data), self._max_depth(filtered_data), self._max_width(filtered_data)),
            skeleton=self.skeleton,
            fields=fields,
            data=filtered_data
        )

    def value_counts(self):
        return value_counts(self.data, self.fields)

    def _access_value(self, record: dict, column: str) -> Union[dict, list, int, float, str, bool, None]:
        col_ref = column.split(".")
        for ref in col_ref:
            if isinstance(record, dict):
                record = record.get(ref)
            else:
                return None
        return record

    def _set_value(self, record: dict, column: str, value) -> None:
        col_ref = column.split(".")
        for ref in col_ref[:-1]:
            if ref not in record:
                record[ref] = {}
            record = record[ref]
        record[col_ref[-1]] = value

    def _max_depth(self, data: List[dict]) -> int:
        def depth(d, level=1):
            if isinstance(d, dict) and d:
                return max(depth(v, level + 1) for v in d.values())
            return level
        return max(depth(d) for d in data) if data else 0

    def _max_width(self, data: List[dict]) -> int:
        def width(d):
            if isinstance(d, dict):
                return len(d)
            return 0
        return max(width(d) for d in data) if data else 0

def get_data_type(value):
    if isinstance(value, int):
        return 'int'
    elif isinstance(value, float):
        return 'float'
    elif isinstance(value, str):
        return 'str'
    elif isinstance(value, bool):
        return 'bool'
    elif value is None:
        return 'null'
    elif isinstance(value, dict):
        return 'dict'
    elif isinstance(value, list):
        return 'list'
    else:
        return 'unknown'


def merge_structures(struct1: dict, struct2: dict) -> dict:
    for key, value in struct2.items():
        if key not in struct1:
            struct1[key] = value
        else:
            if isinstance(value, dict) and isinstance(struct1[key], dict):
                struct1[key] = merge_structures(struct1[key], value)
            elif get_data_type(struct1[key]) != get_data_type(value):
                struct1[key] = get_data_type(value)
    return struct1


def get_structure(data: Union[dict, list, int, float, str, bool, None]) -> Union[dict, str]:
    if isinstance(data, dict):
        return {key: get_structure(value) for key, value in data.items()}
    return get_data_type(data)
