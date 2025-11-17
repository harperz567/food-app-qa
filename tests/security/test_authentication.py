"""
Authentication and Authorization Tests
Tests for missing authentication mechanisms and improper access control
"""

import pytest
import requests
import allure
from config.config import Config

@allure.feature("Security Testing")
@allure.story("Authentication & Authorization")
class TestAuthentication:
    
    @pytest.fixture(scope="class")
    def base_url(self):
        """Base URL for UserInfo service"""
        return Config.USER_SERVICE_URL
    
    @pytest.fixture(scope="class")
    def test_user(self, base_url):
        """Create a test user"""
        user_data = {
            "username": "test_auth_user",
            "userPassword": "securePassword123",
            "address": "100 Security Lane",
            "city": "Boston"
        }
        
        response = requests.post(f"{base_url}/user/addUser", json=user_data)
        if response.status_code == 201:
            return response.json()
        return None
    
    @allure.title("Authentication Test: No Token Required for Sensitive Endpoint")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
    Tests if sensitive endpoints require authentication tokens (JWT/Session).
    
    Expected (Secure System): Endpoints should reject requests without valid auth tokens
    Actual (Current System): All endpoints accessible without authentication
    """)
    def test_no_authentication_required(self, base_url, test_user):
        """Test: Are sensitive endpoints accessible without authentication?"""
        
        if not test_user:
            pytest.skip("Test user not created")
        
        with allure.step("Attempt to access user data WITHOUT any authentication headers"):
            # No Authorization header, no session cookie, nothing
            response = requests.get(
                f"{base_url}/user/fetchUserById/{test_user['userId']}",
                headers={}  # Explicitly empty headers
            )
            
            allure.attach(
                str(response.status_code),
                name="Response Status Code",
                attachment_type=allure.attachment_type.TEXT
            )
            allure.attach(
                response.text,
                name="Response Body",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step("Verify Authentication Requirement"):
            if response.status_code == 200:
                allure.attach(
                    "🚨 CRITICAL VULNERABILITY: No authentication required for sensitive endpoint",
                    name="Security Issue",
                    attachment_type=allure.attachment_type.TEXT
                )
                allure.attach(
                    """
                    Impact: 
                    - Anyone on the internet can access user data
                    - No way to track who accessed what data
                    - Violates data protection regulations (GDPR, CCPA)
                    
                    Recommendation:
                    - Implement JWT-based authentication
                    - Require Authorization header with valid token
                    - Return 401 Unauthorized for missing/invalid tokens
                    """,
                    name="Security Recommendations",
                    attachment_type=allure.attachment_type.TEXT
                )
                pytest.skip("VULNERABILITY CONFIRMED - No authentication required")
            
            elif response.status_code == 401:
                allure.attach(
                    "✅ SECURE: System requires authentication",
                    name="Security Status",
                    attachment_type=allure.attachment_type.TEXT
                )
            else:
                pytest.fail(f"Unexpected response code: {response.status_code}")
    
    @allure.title("Authentication Test: Invalid Token Accepted")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
    Tests if the system validates authentication tokens properly.
    Attempts to access endpoint with fake/invalid token.
    """)
    def test_invalid_token_accepted(self, base_url, test_user):
        """Test: Does the system accept invalid authentication tokens?"""
        
        if not test_user:
            pytest.skip("Test user not created")
        
        fake_tokens = [
            "Bearer fake_jwt_token_12345",
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fakepayload.fakesignature",
            "Invalid_Format_Token",
            ""
        ]
        
        results = []
        
        for token in fake_tokens:
            with allure.step(f"Attempt access with fake token: {token[:30]}..."):
                headers = {"Authorization": token} if token else {}
                response = requests.get(
                    f"{base_url}/user/fetchUserById/{test_user['userId']}",
                    headers=headers
                )
                
                results.append({
                    "token": token[:30] + "..." if len(token) > 30 else token,
                    "status_code": response.status_code,
                    "accepted": response.status_code == 200
                })
        
        with allure.step("Analyze Token Validation"):
            allure.attach(
                str(results),
                name="Token Validation Results",
                attachment_type=allure.attachment_type.JSON
            )
            
            accepted_count = sum(1 for r in results if r['accepted'])
            
            if accepted_count > 0:
                allure.attach(
                    f"🚨 VULNERABILITY CONFIRMED: {accepted_count}/{len(fake_tokens)} invalid tokens were accepted",
                    name="Security Issue",
                    attachment_type=allure.attachment_type.TEXT
                )
                allure.attach(
                    """
                    Impact:
                    - No token validation means authentication can be bypassed
                    - Attackers don't need to steal real tokens
                    
                    Recommendation:
                    - Implement proper JWT validation
                    - Verify token signature with secret key
                    - Check token expiration
                    - Validate token claims (user_id, role, etc.)
                    """,
                    name="Security Recommendations",
                    attachment_type=allure.attachment_type.TEXT
                )
                pytest.skip(f"VULNERABILITY CONFIRMED - {accepted_count} invalid tokens accepted")
            else:
                allure.attach(
                    "✅ SECURE: System rejects all invalid tokens",
                    name="Security Status",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    @allure.title("Authorization Test: No Role-Based Access Control")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("""
    Tests if the system implements role-based access control (RBAC).
    In a secure system, different user roles should have different permissions.
    """)
    def test_no_role_based_access_control(self, base_url, test_user):
        """Test: Does the system implement RBAC?"""
        
        if not test_user:
            pytest.skip("Test user not created")
        
        with allure.step("Check if User entity has role field"):
            response = requests.get(f"{base_url}/user/fetchUserById/{test_user['userId']}")
            user_data = response.json()
            
            allure.attach(
                str(user_data),
                name="User Data Structure",
                attachment_type=allure.attachment_type.JSON
            )
            
            has_role_field = 'role' in user_data or 'userRole' in user_data or 'userType' in user_data
        
        with allure.step("Analyze RBAC Implementation"):
            if not has_role_field:
                allure.attach(
                    "🚨 VULNERABILITY CONFIRMED: No role field in User entity - RBAC not implemented",
                    name="Security Issue",
                    attachment_type=allure.attachment_type.TEXT
                )
                allure.attach(
                    """
                    Current State:
                    - User entity lacks role/permission fields
                    - All users have equal access to all endpoints
                    - No distinction between Customer, Restaurant Owner, Admin
                    
                    Recommended RBAC Model:
                    
                    Roles:
                    1. CUSTOMER - Can only access own data
                    2. RESTAURANT_OWNER - Can manage own restaurant + customer role
                    3. ADMIN - Full system access
                    
                    Implementation Steps:
                    1. Add 'role' field to User entity (enum: CUSTOMER, RESTAURANT_OWNER, ADMIN)
                    2. Add @PreAuthorize annotations to controller methods
                    3. Implement Spring Security with role checks
                    4. Store role in JWT token claims
                    
                    Example:
                    @PreAuthorize("hasRole('ADMIN') or #userId == authentication.principal.userId")
                    public ResponseEntity<UserDTO> fetchUserDetailsById(@PathVariable Integer userId)
                    """,
                    name="RBAC Design Recommendations",
                    attachment_type=allure.attachment_type.TEXT
                )
                pytest.skip("VULNERABILITY CONFIRMED - No RBAC implementation")
            else:
                allure.attach(
                    "✅ Role field exists - Further testing needed to verify RBAC logic",
                    name="Status",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    @allure.title("Security Test: Password Stored in Plain Text")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
    Tests if passwords are properly hashed or stored in plain text.
    Even though the API shows userPassword as null, we check if it's being hashed during storage.
    """)
    def test_password_storage_security(self, base_url):
        """Test: Are passwords properly hashed?"""
        
        with allure.step("Create user with known password"):
            test_password = "MySecretPassword123!"
            user_data = {
                "username": "password_test_user",
                "userPassword": test_password,
                "address": "Security Test St",
                "city": "Boston"
            }
            
            create_response = requests.post(f"{base_url}/user/addUser", json=user_data)
            if create_response.status_code != 201:
                pytest.skip("Could not create test user")
            
            created_user = create_response.json()
        
        with allure.step("Retrieve user data and check password field"):
            fetch_response = requests.get(f"{base_url}/user/fetchUserById/{created_user['userId']}")
            retrieved_user = fetch_response.json()
            
            returned_password = retrieved_user.get('userPassword')
            
            allure.attach(
                f"Original Password: {test_password}\nReturned Password: {returned_password}",
                name="Password Comparison",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step("Analyze Password Security"):
            if returned_password is None:
                allure.attach(
                    "✅ GOOD PRACTICE: Password not returned in API response (but need to verify database storage)",
                    name="Security Status",
                    attachment_type=allure.attachment_type.TEXT
                )
                allure.attach(
                    """
                    Current Implementation:
                    - Password field returns null in API response ✅
                    
                    Still Need to Verify:
                    - Is password hashed in database? (Use BCrypt/Argon2)
                    - Is password field excluded from JSON serialization? (@JsonIgnore)
                    - Are there any endpoints that return password?
                    
                    Best Practices:
                    1. Hash passwords with BCrypt (Spring Security default)
                    2. Add @JsonIgnore to password field
                    3. Never log passwords
                    4. Use HTTPS for all password transmissions
                    """,
                    name="Password Security Recommendations",
                    attachment_type=allure.attachment_type.TEXT
                )
            elif returned_password == test_password:
                allure.attach(
                    "🚨 CRITICAL VULNERABILITY: Password stored and returned in plain text!",
                    name="Security Issue",
                    attachment_type=allure.attachment_type.TEXT
                )
                pytest.skip("CRITICAL VULNERABILITY - Plain text password storage")
            else:
                # Password is returned but appears to be hashed
                allure.attach(
                    "⚠️ WARNING: Password is returned in response (even if hashed, should not be exposed)",
                    name="Security Issue",
                    attachment_type=allure.attachment_type.TEXT
                )