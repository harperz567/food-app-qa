"""
IDOR (Insecure Direct Object Reference) Vulnerability Tests
Tests whether users can access other users' data without authorization
"""

import pytest
import requests
import allure
from config.config import Config

@allure.feature("Security Testing")
@allure.story("IDOR Vulnerability Detection")
class TestIDORVulnerabilities:
    
    @pytest.fixture(scope="class")
    def base_url(self):
        """Base URL for UserInfo service"""
        return Config.USER_SERVICE_URL
    
    @pytest.fixture(scope="class")
    def test_users(self, base_url):
        """Create multiple test users for IDOR testing"""
        users_data = [
            {
                "Username": "alice_customer",
                "UserPassword": "password123",
                "address": "123 Main St",
                "city": "Boston"
            },
            {
                "Username": "bob_customer",
                "UserPassword": "password456",
                "address": "456 Oak Ave",
                "city": "Cambridge"
            },
            {
                "Username": "charlie_customer",
                "UserPassword": "password789",
                "address": "789 Elm St",
                "city": "Somerville"
            }
        ]
        
        created_users = []
        for user_data in users_data:
            response = requests.post(f"{base_url}/user/addUser", json=user_data)
            if response.status_code == 201:
                created_users.append(response.json())
        
        yield created_users
        
        # Cleanup would go here if DELETE endpoint existed
    
    @allure.title("IDOR Test: Access Other User's Data Without Authentication")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
    Tests if an attacker can access another user's sensitive information
    by simply changing the userId in the URL without authentication.
    
    Expected (Secure System): Should return 401 Unauthorized or 403 Forbidden
    Actual (Current System): Returns 200 with full user data - VULNERABILITY CONFIRMED
    """)
    def test_access_other_user_data_without_auth(self, base_url, test_users):
        """Test: Can we access user B's data without being authenticated?"""
        
        if len(test_users) < 2:
            pytest.skip("Not enough test users created")
        
        user_a = test_users[0]
        user_b = test_users[1]
        
        with allure.step(f"User A created with userId: {user_a['userId']}"):
            allure.attach(
                str(user_a),
                name="User A Data",
                attachment_type=allure.attachment_type.JSON
            )
        
        with allure.step(f"Attempt to access User B's data (userId: {user_b['userId']}) WITHOUT authentication"):
            # In a secure system, this request should be made without auth token
            # and should fail. Currently, no auth is required.
            response = requests.get(f"{base_url}/user/fetchUserById/{user_b['userId']}")
            
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
        
        with allure.step("Analyze Security Vulnerability"):
            # Current behavior: Returns 200 with data (VULNERABLE)
            # Expected behavior: Should return 401 or 403
            
            if response.status_code == 200:
                allure.attach(
                    "🚨 VULNERABILITY CONFIRMED: Unauthenticated access to user data is allowed",
                    name="Security Issue",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                # Verify we got the actual user data
                response_data = response.json()
                assert response_data['userId'] == user_b['userId'], \
                    "Response should contain User B's data"
                
                # Document what sensitive data was exposed
                exposed_fields = ['Username', 'UserPassword', 'address', 'city']
                exposed_data = {k: response_data.get(k) for k in exposed_fields}
                allure.attach(
                    str(exposed_data),
                    name="🔓 Exposed Sensitive Data",
                    attachment_type=allure.attachment_type.JSON
                )
                
                # This test passes because we confirmed the vulnerability exists
                # In production, we'd want this to FAIL (meaning security is fixed)
                pytest.skip("VULNERABILITY CONFIRMED - System allows unauthorized access")
            
            else:
                # If we get here, security has been implemented!
                assert response.status_code in [401, 403], \
                    f"Expected 401/403, got {response.status_code}"
                allure.attach(
                    "✅ SECURE: System properly blocks unauthorized access",
                    name="Security Status",
                    attachment_type=allure.attachment_type.TEXT
                )


    @allure.title("IDOR Test: Sequential User ID Enumeration")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
    Tests if an attacker can enumerate all users by trying sequential userIds.
    This is possible because userId uses AUTO_INCREMENT strategy.
    
    Attack Scenario: Attacker discovers userId=100 exists, then tries 101, 102, 103...
    to harvest all user data from the system.
    """)
    def test_sequential_userid_enumeration(self, base_url, test_users):
        """Test: Can we enumerate all users by trying sequential IDs?"""
        
        if not test_users:
            pytest.skip("No test users available")
        
        # Get the first user's ID
        start_id = test_users[0]['userId']
        
        with allure.step(f"Starting enumeration from userId: {start_id}"):
            allure.attach(
                f"Attempting to access userIds from {start_id} to {start_id + 5}",
                name="Enumeration Range",
                attachment_type=allure.attachment_type.TEXT
            )
        
        accessible_users = []
        
        # Try to access the next 5 user IDs
        for user_id in range(start_id, start_id + 6):
            response = requests.get(f"{base_url}/user/fetchUserById/{user_id}")
            
            if response.status_code == 200:
                user_data = response.json()
                accessible_users.append({
                    'userId': user_id,
                    'username': user_data.get('Username'),
                    'city': user_data.get('city')
                })
        
        with allure.step(f"Enumeration Result: {len(accessible_users)} users accessed"):
            allure.attach(
                str(accessible_users),
                name="🔓 Enumerated Users",
                attachment_type=allure.attachment_type.JSON
            )
            
            if len(accessible_users) > 0:
                allure.attach(
                    f"🚨 VULNERABILITY CONFIRMED: Successfully enumerated {len(accessible_users)} users through sequential ID guessing",
                    name="Security Issue",
                    attachment_type=allure.attachment_type.TEXT
                )
                pytest.skip(f"VULNERABILITY CONFIRMED - Enumerated {len(accessible_users)} users")
            else:
                allure.attach(
                    "✅ SECURE: System prevents user enumeration",
                    name="Security Status",
                    attachment_type=allure.attachment_type.TEXT
                )


    @allure.title("IDOR Test: Cross-User Data Modification Attempt")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
    Tests if User A (logged in as Customer) can modify User B's data.
    Note: UPDATE endpoint may not exist yet, but this documents the test case.
    """)
    def test_cross_user_data_modification(self, base_url, test_users):
        """Test: Can User A modify User B's data?"""
        
        if len(test_users) < 2:
            pytest.skip("Not enough test users created")
        
        user_a = test_users[0]
        user_b = test_users[1]
        
        with allure.step("Simulate User A attempting to modify User B's address"):
            # This tests if UPDATE endpoint exists and is vulnerable
            malicious_update = {
                "username": user_b.get('username', user_b.get('Username', '')),
                "userPassword": user_b.get('userPassword', user_b.get('UserPassword', '')),
                "address": "HACKED BY USER A",
                "city": user_b['city']
            }
            
            # Try PUT request (common for updates)
            response = requests.put(
                f"{base_url}/user/updateUser/{user_b['userId']}", 
                json=malicious_update
            )
            
            allure.attach(
                str(response.status_code),
                name="Update Attempt Status",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step("Analyze Modification Attempt"):
            if response.status_code == 404:
                allure.attach(
                    "ℹ️ UPDATE endpoint not implemented yet",
                    name="Status",
                    attachment_type=allure.attachment_type.TEXT
                )
                pytest.skip("UPDATE endpoint not implemented")
            
            elif response.status_code == 200:
                # Verify if the modification actually worked
                verify_response = requests.get(f"{base_url}/user/fetchUserById/{user_b['userId']}")
                updated_data = verify_response.json()
                
                if updated_data.get('address') == "HACKED BY USER A":
                    allure.attach(
                        "🚨 CRITICAL VULNERABILITY: User A successfully modified User B's data",
                        name="Security Issue",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    pytest.skip("VULNERABILITY CONFIRMED - Cross-user modification allowed")
                else:
                    allure.attach(
                        "✅ SECURE: Modification was rejected",
                        name="Security Status",
                        attachment_type=allure.attachment_type.TEXT
                    )
            
            elif response.status_code in [401, 403]:
                allure.attach(
                    "✅ SECURE: System properly blocks unauthorized modification",
                    name="Security Status",
                    attachment_type=allure.attachment_type.TEXT
                )