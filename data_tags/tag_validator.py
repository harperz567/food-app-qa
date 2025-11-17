"""
Data tag validation utilities
"""
import json
from typing import Dict, Any, List


class TagValidator:
    """Validates data against PII tag schema"""
    
    def __init__(self, schema_path: str = 'data_tags/tag_schema.json'):
        """Initialize validator with schema"""
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
    
    def get_service_schema(self, service_name: str) -> Dict[str, Any]:
        """Get schema for a specific service"""
        return self.schema['services'].get(service_name, {})
    
    def get_field_tags(self, service_name: str, field_name: str) -> Dict[str, Any]:
        """Get PII tags for a specific field"""
        service = self.get_service_schema(service_name)
        return service.get('fields', {}).get(field_name, {})
    
    def validate_field_exists(self, service_name: str, data: Dict[str, Any]) -> List[str]:
        """Validate all required fields exist in data"""
        service = self.get_service_schema(service_name)
        required_fields = [
            field_name for field_name, field_info in service.get('fields', {}).items()
            if field_info.get('required', False)
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        return missing_fields
    
    def get_sensitive_fields(self, service_name: str, min_level: int = 2) -> List[str]:
        """Get list of sensitive fields (PII level >= min_level)"""
        service = self.get_service_schema(service_name)
        sensitive = []
        
        for field_name, field_info in service.get('fields', {}).items():
            if field_info.get('piiLevel', 0) >= min_level:
                sensitive.append(field_name)
        
        return sensitive
    
    def should_field_be_encrypted(self, service_name: str, field_name: str) -> bool:
        """Check if field should be encrypted (PII level >= 3)"""
        tags = self.get_field_tags(service_name, field_name)
        return tags.get('piiLevel', 0) >= 3
    
    def get_retention_policy(self, service_name: str, field_name: str) -> str:
        """Get retention policy for a field"""
        tags = self.get_field_tags(service_name, field_name)
        return tags.get('retention', 'RETAIN_INDEFINITE')