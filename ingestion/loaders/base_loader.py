from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseLoader(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def load(self, source: str, metadata: Optional[Dict[str, Any]]=None, **kwargs) -> Dict[str, Any]:
        pass

    def merge_metadata(self, old_metadata: Optional[Dict[str, Any]], new_metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not old_metadata:
            return new_metadata
        if not new_metadata:
            return old_metadata
        metadata = {}
        for key in old_metadata.keys():
            if key in new_metadata:
                if isinstance(old_metadata[key], list) and isinstance(new_metadata[key], list):
                    metadata[key] = old_metadata[key] + new_metadata[key]
                elif isinstance(old_metadata[key], list):
                    metadata[key] = old_metadata[key] + [new_metadata[key]]
                elif isinstance(new_metadata[key], list):
                    metadata[key] = [old_metadata[key]] + new_metadata[key]
                else:
                    metadata[key] = [old_metadata[key], new_metadata[key]]
            else:
                metadata[key] = old_metadata[key]
        
        for key in new_metadata.keys():
            if key not in old_metadata.keys():
                metadata[key] = new_metadata[key]

        return metadata