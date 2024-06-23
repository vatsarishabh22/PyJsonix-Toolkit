import json
import os

from typing import List, Dict, Union
from pyjsonix.core import JSONFrame, get_structure, merge_structures

class Engine:
    def read(self, kwds: Dict) -> List[Dict]:
        raise NotImplementedError("This method should be overridden by subclasses")

class SequentialEngine(Engine):
    def read(self, kwds: Dict) -> JSONFrame:

        combined_structure = {}
        max_depth = 0
        max_width = 0
        records = []
        all_fields = set()

        for file_path in kwds.get('file_paths', []):
            if not os.path.isfile(file_path):
                if kwds.get('raise_error', False):
                    raise FileNotFoundError(f"The file at {file_path} does not exist or is not accessible.")
                else:
                    print(f"Warning: The file at {file_path} does not exist or is not accessible.")
                    continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        all_fields.update(get_all_fields(data))
                        if kwds.get('fields'):
                            data = self._filter_fields_data(data, kwds)
                        records.append(data)
                    except json.JSONDecodeError as e:
                        if kwds.get('raise_error', False):
                            raise e
                        else:
                            print(f"Warning: JSON decode error in file {file_path}: {e}")
        
        combined_structure = self._compute_combined_structure(records)
        max_depth = self._compute_max_depth(records)
        max_width = self._compute_max_width(records)

        json_frame = JSONFrame(
            shape=(len(records), max_depth, max_width),
            skeleton=combined_structure,
            fields=kwds.get('fields') if kwds.get('fields') else list(all_fields),
            data=records
        )

        return json_frame
    
    def _filter_fields_data(self, data, kwds):
        fields = kwds.get('fields')
        filtered_data = {}
        for field in fields:
            value = _access_value(data, field)
            if value is not None:
                _set_value(filtered_data, field, value)
        return filtered_data

    def _compute_combined_structure(self, records: List[dict]) -> dict:
        combined_structure = {}
        for data in records:
            data_structure = get_structure(data)
            combined_structure = merge_structures(combined_structure, data_structure)
        return combined_structure

    def _compute_max_depth(self, records: List[dict]) -> int:
        max_depth = 0
        for data in records:
            max_depth = max(max_depth, _max_depth([data]))  
        return max_depth

    def _compute_max_width(self, records: List[dict]) -> int:
        max_width = 0
        for data in records:
            max_width = max(max_width, _max_width([data]))
        return max_width

class ParallelEngine(Engine):
    def read(self, kwds: Dict) -> List[Dict]:
        raise NotImplementedError("This method will be implemented in the future.")

class CompiledEngine(Engine):
    def read(self, kwds: Dict) -> List[Dict]:
        raise NotImplementedError("This method will be implemented in the future.")

def _max_depth(data: List[dict]) -> int:
    def depth(d, level=0):
        if isinstance(d, dict) and d:
            return max(depth(v, level + 1) for v in d.values())
        return level
    return max(depth(d) for d in data) if data else 0

def _max_width(data: List[dict]) -> int:
    def width(d):
        if isinstance(d, dict):
            return len(d)
        return 0
    return max(width(d) for d in data) if data else 0

def _access_value(record: dict, column: str) -> Union[dict, list, int, float, str, bool, None]:
    col_ref = column.split(".")
    for ref in col_ref:
        if isinstance(record, dict):
            record = record.get(ref)
        else:
            return None
    return record

def _set_value(record: dict, column: str, value) -> None:
    col_ref = column.split(".")
    for ref in col_ref[:-1]:
        if ref not in record:
            record[ref] = {}
        record = record[ref]
    record[col_ref[-1]] = value

def get_all_fields(data, parent_key=''):
    fields = set()
    if isinstance(data, dict):
        for k, v in data.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            fields.add(new_key)
            if isinstance(v, dict):
                fields.update(get_all_fields(v, new_key))
            elif isinstance(v, list):
                for item in v:
                    fields.update(get_all_fields(item, new_key))
    elif isinstance(data, list):
        for item in data:
            fields.update(get_all_fields(item, parent_key))
    return fields
