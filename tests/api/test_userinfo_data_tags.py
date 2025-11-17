import pytest
import requests
import allure
import json
from data_tags.tag_validator import TagValidator


@allure.feature('Data Classification')
@allure.story('UserInfo Service PII Tags')
class TestUserInfoDataTags:
    
    @pytest.fixture
    def tag_validator(self):
        """Initialize tag validator"""
        return TagValidator()
    
    @pytest.fixture
    def base_url(self):
        """UserInfo service base URL"""
        return "http://localhost:9093"
    
    @allure.title("Verify UserInfo API returns all required fields")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_userinfo_api_returns_required_fields(self, base_url, tag_validator):
        """Test: Verify UserInfo API returns all PII-tagged fields"""
        
        with allure.step("Call UserInfo API"):
            # Note: You need to have a test user created first
            # You can create one via POST /api/user/addUser
            response = requests.get(f"{base_url}/user/fetchUserById/6")
            
            # Handle both ResponseEntity<UserDTO> and direct UserDTO response
            if response.status_code == 200:
                data = response.json()
                allure.attach(json.dumps(data, indent=2), 
                            name="API Response", 
                            attachment_type=allure.attachment_type.JSON)
        
        with allure.step("Validate required fields exist"):
            # Check if response is wrapped in ResponseEntity
            if 'body' in data:
                user_data = data['body']
            else:
                user_data = data
            
            missing_fields = tag_validator.validate_field_exists('userinfo', user_data)
            
            assert len(missing_fields) == 0, \
                f"Missing required fields: {missing_fields}"
    
    @allure.title("Verify sensitive fields are present in UserInfo")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_userinfo_contains_sensitive_fields(self, base_url, tag_validator):
        """Test: Verify UserInfo returns sensitive PII data (Level 2+)"""
        
        with allure.step("Get user data"):
            response = requests.get(f"{base_url}/user/fetchUserById/6")
            data = response.json()
            user_data = data.get('body', data)
        
        with allure.step("Get sensitive fields from schema"):
            sensitive_fields = tag_validator.get_sensitive_fields('userinfo', min_level=2)
            allure.attach(
                ", ".join(sensitive_fields),
                name="Sensitive Fields (PII Level >= 2)",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step("Verify sensitive fields exist in response"):
            for field in sensitive_fields:
                assert field in user_data, \
                    f"Sensitive field '{field}' not found in response"
                
                # Get PII level for documentation
                pii_level = tag_validator.get_field_tags('userinfo', field)['piiLevel']
                print(f"✅ {field}: PII Level {pii_level}")
    
    @allure.title("Verify critical fields (Level 3+) are documented")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_critical_fields_are_documented(self, tag_validator):
        """Test: Verify all critical fields have proper tags"""
        
        with allure.step("Get critical fields (PII Level >= 3)"):
            critical_fields = tag_validator.get_sensitive_fields('userinfo', min_level=3)
            
            assert len(critical_fields) > 0, "Should have at least one critical field"
            
            allure.attach(
                json.dumps(critical_fields, indent=2),
                name="Critical Fields",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Verify each critical field has retention policy"):
            for field in critical_fields:
                tags = tag_validator.get_field_tags('userinfo', field)
                
                assert 'retention' in tags, \
                    f"Field '{field}' missing retention policy"
                
                retention = tags['retention']
                pii_level = tags['piiLevel']
                
                print(f"✅ {field}: Level {pii_level}, Retention: {retention}")
                
                allure.attach(
                    f"Field: {field}\nPII Level: {pii_level}\nRetention: {retention}",
                    name=f"{field} Tags",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    @allure.title("Verify password field should be encrypted")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_password_field_encryption_requirement(self, tag_validator):
        """Test: Verify password field is marked for encryption"""
        
        with allure.step("Check if userPassword should be encrypted"):
            should_encrypt = tag_validator.should_field_be_encrypted('userinfo', 'userPassword')  # ✅
            
            assert should_encrypt, \
                "userPassword field should be marked for encryption (PII Level >= 3)"
        
        with allure.step("Verify password has correct PII level"):
            tags = tag_validator.get_field_tags('userinfo', 'userPassword')  # ✅
            pii_level = tags['piiLevel']
            
            assert pii_level == 4, \
                f"Password should be CRITICAL (Level 4), got Level {pii_level}"
            
            print(f"✅ userPassword correctly marked as Level {pii_level} (CRITICAL)")
    
    @allure.title("Document all UserInfo field classifications")
    @allure.severity(allure.severity_level.NORMAL)
    def test_document_all_field_classifications(self, tag_validator):
        """Test: Generate documentation of all field classifications"""
        
        with allure.step("Get all UserInfo fields"):
            service_schema = tag_validator.get_service_schema('userinfo')
            fields = service_schema.get('fields', {})
            
            # Create a summary table
            summary = []
            for field_name, field_info in fields.items():
                summary.append({
                    'field': field_name,
                    'piiLevel': field_info.get('piiLevel'),
                    'piiLevelName': field_info.get('piiLevelName'),
                    'retention': field_info.get('retention'),
                    'description': field_info.get('description')
                })
            
            allure.attach(
                json.dumps(summary, indent=2),
                name="UserInfo Field Classification Summary",
                attachment_type=allure.attachment_type.JSON
            )
            
            print("\n" + "="*70)
            print("UserInfo Service - Data Classification Summary")
            print("="*70)
            for item in summary:
                print(f"\n{item['field']}:")
                print(f"  PII Level: {item['piiLevel']} ({item['piiLevelName']})")
                print(f"  Retention: {item['retention']}")
                print(f"  Description: {item['description']}")
            print("="*70)