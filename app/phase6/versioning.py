from __future__ import annotations

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

from app.config import settings


@dataclass
class DataVersion:
    """Data version information."""
    version: str
    dataset_id: str
    commit_hash: Optional[str]
    download_url: Optional[str]
    record_count: int
    checksum: str
    created_at: datetime
    description: str


class DataVersionManager:
    """Manager for dataset versioning and reproducibility."""
    
    def __init__(self):
        self.versions_dir = Path("data/versions")
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.current_version_file = self.versions_dir / "current.json"
        self.version_history_file = self.versions_dir / "history.json"
    
    def get_current_version(self) -> Optional[DataVersion]:
        """Get current dataset version."""
        if not self.current_version_file.exists():
            return None
        
        try:
            with open(self.current_version_file, 'r') as f:
                data = json.load(f)
                data['created_at'] = datetime.fromisoformat(data['created_at'])
                return DataVersion(**data)
        except Exception:
            return None
    
    def pin_dataset_version(self, version_info: Dict[str, Any]) -> DataVersion:
        """Pin a specific dataset version."""
        version = DataVersion(
            version=version_info.get('version', '1.0.0'),
            dataset_id=version_info.get('dataset_id', settings.zomato_dataset_id),
            commit_hash=version_info.get('commit_hash'),
            download_url=version_info.get('download_url'),
            record_count=version_info.get('record_count', 0),
            checksum=version_info.get('checksum', ''),
            created_at=datetime.now(),
            description=version_info.get('description', '')
        )
        
        # Save current version
        with open(self.current_version_file, 'w') as f:
            json.dump(asdict(version), f, indent=2, default=str)
        
        # Add to history
        self._add_to_history(version)
        
        return version
    
    def validate_data_integrity(self, catalog_data: List[Any]) -> Dict[str, Any]:
        """Validate the integrity of catalog data."""
        if not catalog_data:
            return {
                "valid": False,
                "error": "Empty catalog",
                "record_count": 0
            }
        
        # Basic validation
        required_fields = ['id', 'name', 'city', 'cuisines', 'cost_band', 'rating']
        missing_fields = set()
        
        for i, record in enumerate(catalog_data[:100]):  # Check first 100 records
            record_dict = record.model_dump() if hasattr(record, 'model_dump') else record
            for field in required_fields:
                if field not in record_dict or record_dict[field] is None:
                    missing_fields.add(field)
        
        if missing_fields:
            return {
                "valid": False,
                "error": f"Missing required fields: {missing_fields}",
                "record_count": len(catalog_data)
            }
        
        # Calculate checksum
        data_str = json.dumps([
            record.model_dump() if hasattr(record, 'model_dump') else record
            for record in catalog_data[:1000]  # First 1000 for checksum
        ], sort_keys=True, default=str)
        
        checksum = hashlib.sha256(data_str.encode()).hexdigest()
        
        # Compare with stored version if available
        current_version = self.get_current_version()
        checksum_match = True
        if current_version and current_version.checksum:
            checksum_match = checksum == current_version.checksum
        
        return {
            "valid": True,
            "record_count": len(catalog_data),
            "checksum": checksum,
            "checksum_match": checksum_match,
            "sample_records_checked": min(100, len(catalog_data)),
            "missing_fields": list(missing_fields) if missing_fields else []
        }
    
    def get_version_history(self) -> List[DataVersion]:
        """Get version history."""
        if not self.version_history_file.exists():
            return []
        
        try:
            with open(self.version_history_file, 'r') as f:
                data = json.load(f)
                return [
                    DataVersion(
                        **item,
                        created_at=datetime.fromisoformat(item['created_at'])
                    )
                    for item in data
                ]
        except Exception:
            return []
    
    def _add_to_history(self, version: DataVersion):
        """Add version to history."""
        history = self.get_version_history()
        history.append(version)
        
        # Keep only last 50 versions
        history = history[-50:]
        
        with open(self.version_history_file, 'w') as f:
            json.dump([asdict(v) for v in history], f, indent=2, default=str)
    
    def create_version_snapshot(self, catalog_data: List[Any], description: str = "") -> DataVersion:
        """Create a snapshot version from current catalog."""
        # Calculate checksum
        data_str = json.dumps([
            record.model_dump() if hasattr(record, 'model_dump') else record
            for record in catalog_data
        ], sort_keys=True, default=str)
        
        checksum = hashlib.sha256(data_str.encode()).hexdigest()
        
        version_info = {
            "version": f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "dataset_id": settings.zomato_dataset_id,
            "record_count": len(catalog_data),
            "checksum": checksum,
            "description": description or f"Snapshot with {len(catalog_data)} records"
        }
        
        return self.pin_dataset_version(version_info)
    
    def rollback_to_version(self, version: str) -> bool:
        """Rollback to a specific version (metadata only)."""
        history = self.get_version_history()
        
        for v in history:
            if v.version == version:
                with open(self.current_version_file, 'w') as f:
                    json.dump(asdict(v), f, indent=2, default=str)
                return True
        
        return False
    
    def export_version_info(self) -> Dict[str, Any]:
        """Export complete version information."""
        current = self.get_current_version()
        history = self.get_version_history()
        
        return {
            "current": asdict(current) if current else None,
            "history": [asdict(v) for v in history],
            "export_timestamp": datetime.now().isoformat(),
            "total_versions": len(history)
        }


# Global version manager
version_manager = DataVersionManager()


def get_data_version() -> Optional[DataVersion]:
    """Get current dataset version."""
    return version_manager.get_current_version()


def pin_dataset_version(version_info: Dict[str, Any]) -> DataVersion:
    """Pin a dataset version."""
    return version_manager.pin_dataset_version(version_info)


def validate_data_integrity(catalog_data: List[Any]) -> Dict[str, Any]:
    """Validate catalog data integrity."""
    return version_manager.validate_data_integrity(catalog_data)


def create_version_snapshot(catalog_data: List[Any], description: str = "") -> DataVersion:
    """Create a version snapshot."""
    return version_manager.create_version_snapshot(catalog_data, description)


def get_version_history() -> List[DataVersion]:
    """Get version history."""
    return version_manager.get_version_history()


def export_version_info() -> Dict[str, Any]:
    """Export version information."""
    return version_manager.export_version_info()
