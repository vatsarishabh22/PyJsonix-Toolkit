from typing import List, Dict, Union

def value_counts(data: List[dict], fields: List[str], dropna: bool = False, normalize: bool = False, ascending: bool = False) -> Dict[str, int]:
    value_counts_map = {}
    for record in data:
        if len(fields) > 1:

            col_values = tuple(record.get(field) for field in fields)
            if dropna and all(val is None for val in col_values):
                continue
            col_values_str = " <=> ".join(map(str, col_values))
            if col_values_str in value_counts_map:
                value_counts_map[col_values_str] += 1
            else:
                value_counts_map[col_values_str] = 1

        else:

            col_value = record.get(fields[0])
            if dropna and col_value is None:
                continue
            if col_value in value_counts_map:
                value_counts_map[col_value] += 1
            else:
                value_counts_map[col_value] = 1

    if normalize:
        total_count = sum(value_counts_map.values())
        value_counts_map = {k: v / total_count for k, v in value_counts_map.items()}

    return dict(sorted(value_counts_map.items(), key=lambda x: x[1], reverse=not ascending))
