# RBAC Security Model Design

## Executive Summary
**Security Assessment**: The current system lacks authentication and authorization mechanisms, exposing critical vulnerabilities including IDOR (Insecure Direct Object Reference) and unauthorized data access.

## Identified Vulnerabilities

### 1. Missing Authentication
- **Endpoint**: `GET /user/fetchUserById/{userId}`
- **Issue**: No authentication required - anyone can access
- **Impact**: Complete exposure of user PII data
- **Risk Level**: CRITICAL

### 2. IDOR Vulnerability
- **Issue**: Sequential userId (auto-increment) allows enumeration
- **Attack Vector**: Attacker can iterate through `/user/fetchUserById/1`, `/2`, `/3`...
- **Exposed Data**: Username, password (even if hashed), address, city
- **Risk Level**: CRITICAL

### 3. Missing Authorization
- **Issue**: No role-based access control
- **Impact**: All users have equal access to all resources
- **Risk Level**: HIGH

## Proposed RBAC Model

### Role Definitions

#### 1. Customer (ROLE_CUSTOMER)
**Permissions**:
- ✅ Create own user account
- ✅ Read own user data only
- ✅ Update own profile
- ❌ Access other users' data
- ❌ Access admin functions

**API Access**:
```
POST /user/addUser          ✅ (create own account)
GET /user/fetchUserById/{id} ✅ (only if id == current user's id)
```

#### 2. Restaurant Owner (ROLE_RESTAURANT_OWNER)
**Permissions**:
- ✅ All Customer permissions
- ✅ Manage own restaurant data
- ✅ View orders for own restaurant
- ❌ Access other restaurants' data
- ❌ Access user credentials

#### 3. System Admin (ROLE_ADMIN)
**Permissions**:
- ✅ Read all user data (for support purposes)
- ✅ Manage system configuration
- ✅ Access audit logs
- ❌ Modify user passwords directly

### Access Control Matrix

| Endpoint | Customer | Restaurant Owner | Admin |
|----------|----------|------------------|-------|
| `POST /user/addUser` | ✅ Self only | ✅ Self only | ✅ Any user |
| `GET /user/fetchUserById/{id}` | ✅ Self only | ✅ Self only | ✅ Any user |
| `PUT /user/updateUser/{id}` | ✅ Self only | ✅ Self only | ✅ Any user |
| `DELETE /user/{id}` | ❌ | ❌ | ✅ |

## Implementation Recommendations

### 1. Add Role Field to User Entity
```java
@Entity
public class User {
    // ... existing fields
    
    @Enumerated(EnumType.STRING)
    @PIITag(
        level = PIILevel.INTERNAL,
        retention = DataRetentionPolicy.RETAIN_1_YEAR,
        description = "User role for access control"
    )
    private UserRole role; // CUSTOMER, RESTAURANT_OWNER, ADMIN
}

public enum UserRole {
    CUSTOMER,
    RESTAURANT_OWNER,
    ADMIN
}
```

### 2. Add Spring Security
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
```

### 3. Implement Authentication
- Add JWT token-based authentication
- Store current user context in SecurityContext
- Validate token on every request

### 4. Implement Authorization
```java
@GetMapping("/fetchUserById/{userId}")
@PreAuthorize("hasRole('ADMIN') or #userId == authentication.principal.userId")
public ResponseEntity<UserDTO> fetchUserDetailsById(@PathVariable Integer userId) {
    // Only admins or the user themselves can access
}
```

## Testing Strategy

### Security Tests to Implement
1. **IDOR Detection Test**: Verify unauthorized access is blocked
2. **Authentication Test**: Verify endpoints require valid tokens
3. **Authorization Test**: Verify role-based access rules
4. **Session Management Test**: Verify token expiration

### Expected Outcomes After Fix
- ❌ Customer A cannot access Customer B's data
- ❌ Unauthenticated requests return 401
- ❌ Unauthorized role access returns 403
- ✅ Admin can access all users
- ✅ Users can access own data

## Timeline
- **Week 1**: Document vulnerabilities + Design RBAC model ✅
- **Week 2**: Implement security tests
- **Week 3**: Add Spring Security implementation
- **Week 4**: CI/CD integration for automated security testing

---
**Document Version**: 1.0  
**Last Updated**: November 17, 2025  
**Author**: Harper Zhang - QA Engineer