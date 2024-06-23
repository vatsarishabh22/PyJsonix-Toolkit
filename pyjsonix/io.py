from typing import Union, List, Dict
from .core import JSONFrame, get_structure, merge_structures
from .engines import Engine, SequentialEngine, ParallelEngine, CompiledEngine

def read_json(
        file_paths: Union[str, List[str]], 
        fields: List[str] = None, 
        raise_error: bool = False, 
        encoding: str = 'utf-8', 
        engine: str = 'sequential') -> JSONFrame:
    
    kwds = locals().copy()
    if isinstance(file_paths, str):
        kwds.update({"file_paths": [file_paths]})
    engine_instance = get_engine_instance(engine)
    
    return engine_instance.read(kwds)

def get_engine_instance(engine: str) -> Engine:
    if engine == 'sequential':
        return SequentialEngine()
    elif engine == 'parallel':
        return ParallelEngine()
    elif engine == 'compiled':
        return CompiledEngine()
    else:
        raise ValueError(f"Unknown engine type: {engine}")
