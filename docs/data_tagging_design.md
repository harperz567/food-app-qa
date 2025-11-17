# Data Tagging System Design

## Overview
This document defines the data classification and retention policy for the food delivery microservices system.

## PII (Personally Identifiable Information) Classification

### Level 0: Public Data
**Definition**: Data that can be freely shared and displayed publicly.

**Examples**:
- Restaurant name
- Restaurant description
- Food item name
- Food item price
- Food item description

**Retention**: Indefinite (as long as business operates)

**Security Requirements**: None

---

### Level 1: Internal Data
**Definition**: Non-sensitive business data, not directly tied to individuals.

**Examples**:
- Order ID
- Restaurant ID
- Transaction timestamp

**Retention**: 7 years (for financial compliance)

**Security Requirements**: Access control required

---

### Level 2: Sensitive PII
**Definition**: Data that can identify an individual but is not highly sensitive.

**Examples**:
- User address
- User city
- Email address (if implemented)
- Phone number (if implemented)

**Retention**: 
- Active users: Retained
- Deleted accounts: 30 days grace period, then permanent deletion

**Security Requirements**: 
- Encrypted in transit (HTTPS)
- Access logging required
- User can request deletion (GDPR compliance)

---

### Level 3: Highly Sensitive PII
**Definition**: Data that poses significant risk if exposed.

**Examples**:
- Username
- User ID in payment context
- Delivery instructions with personal details

**Retention**: 
- Active users: Retained with encryption
- Deleted accounts: Immediate anonymization

**Security Requirements**:
- Encrypted at rest and in transit
- Audit logging on all access
- Cannot be displayed in logs
- Masked in UI (e.g., show only last 4 digits)

---

### Level 4: Highly Sensitive Financial/Authentication Data
**Definition**: Data that could lead to financial loss or account takeover.

**Examples**:
- UserPassword (hashed)
- Payment amount
- Payment method details
- Stripe payment intent ID
- Session tokens (if implemented)

**Retention**:
- Passwords: Until changed or account deleted
- Payment data: 7 years (legal requirement)

**Security Requirements**:
- Always hashed/encrypted (passwords)
- Never logged
- Transmitted only over secure channels
- Access requires additional authentication
- PCI-DSS compliance for payment data

---

## Data Tagging Schema

### Tag Structure
```json
{
  "fieldName": "address",
  "piiLevel": 2,
  "retention": "DELETE_ON_REQUEST",
  "description": "User's delivery address"
}
```

### Retention Policies

| Policy | Description | Deletion Timeline |
|--------|-------------|-------------------|
| `RETAIN_INDEFINITE` | Keep forever | Never |
| `RETAIN_7_YEARS` | Financial compliance | 7 years after last transaction |
| `RETAIN_1_YEAR` | Standard retention | 1 year after last access |
| `DELETE_ON_REQUEST` | User-controlled | Within 30 days of request |
| `DELETE_IMMEDIATELY` | On account deletion | Within 24 hours |

---

## Service-by-Service Data Classification

### UserInfo Service

| Field | PII Level | Retention | Rationale |
|-------|-----------|-----------|-----------|
| `userId` | 1 | RETAIN_1_YEAR | Internal identifier |
| `Username` | 3 | DELETE_ON_REQUEST | Can identify individual |
| `UserPassword` | 4 | DELETE_IMMEDIATELY | Authentication credential |
| `address` | 2 | DELETE_ON_REQUEST | Delivery information |
| `city` | 2 | DELETE_ON_REQUEST | Location data |

---

### Order Service

| Field | PII Level | Retention | Rationale |
|-------|-----------|-----------|-----------|
| `orderId` | 1 | RETAIN_7_YEARS | Business record |
| `userDTO.userId` | 3 | RETAIN_7_YEARS | Links order to user |
| `userDTO.address` | 2 | RETAIN_7_YEARS | Delivery proof |
| `foodItemsList` | 0 | RETAIN_7_YEARS | Public product data |
| `restaurant` | 0 | RETAIN_7_YEARS | Public business data |

---

### Payment Service

| Field | PII Level | Retention | Rationale |
|-------|-----------|-----------|-----------|
| `paymentId` | 1 | RETAIN_7_YEARS | Transaction record |
| `orderId` | 1 | RETAIN_7_YEARS | Links to order |
| `userId` | 3 | RETAIN_7_YEARS | Links to user |
| `amount` | 4 | RETAIN_7_YEARS | Financial data |
| `paymentStatus` | 1 | RETAIN_7_YEARS | Transaction status |
| `paymentMethod` | 4 | RETAIN_7_YEARS | Sensitive financial info |
| `stripePaymentIntentId` | 4 | RETAIN_7_YEARS | Payment processor ID |

---

### Restaurant Service

| Field | PII Level | Retention | Rationale |
|-------|-----------|-----------|-----------|
| `id` | 0 | RETAIN_INDEFINITE | Public identifier |
| `name` | 0 | RETAIN_INDEFINITE | Public information |
| `address` | 0 | RETAIN_INDEFINITE | Public business address |
| `city` | 0 | RETAIN_INDEFINITE | Public location |
| `restaurantDescription` | 0 | RETAIN_INDEFINITE | Public marketing content |

---

### Food Catalog Service

| Field | PII Level | Retention | Rationale |
|-------|-----------|-----------|-----------|
| `id` | 0 | RETAIN_INDEFINITE | Public identifier |
| `itemName` | 0 | RETAIN_INDEFINITE | Public product name |
| `itemDescription` | 0 | RETAIN_INDEFINITE | Public product info |
| `isVeg` | 0 | RETAIN_INDEFINITE | Public dietary info |
| `price` | 0 | RETAIN_INDEFINITE | Public pricing |
| `restaurantId` | 0 | RETAIN_INDEFINITE | Public association |
| `quantity` | 0 | RETAIN_INDEFINITE | Inventory data |

---

## Data Flow and Tag Propagation

### Example: Creating an Order
```
User Service → Order Service → Payment Service

Step 1: User Service provides user data
{
  "userId": 123,
  "address": "123 Main St",
  "piiTags": {
    "userId": {"level": 3, "retention": "DELETE_ON_REQUEST"},
    "address": {"level": 2, "retention": "DELETE_ON_REQUEST"}
  }
}

Step 2: Order Service receives and preserves tags
{
  "orderId": 456,
  "userDTO": {
    "userId": 123,
    "address": "123 Main St"
  },
  "piiTags": {
    "userDTO.userId": {"level": 3, "retention": "RETAIN_7_YEARS"},
    "userDTO.address": {"level": 2, "retention": "RETAIN_7_YEARS"}
  }
}

Step 3: Payment Service receives order reference
{
  "paymentId": 789,
  "orderId": 456,
  "userId": 123,
  "amount": 29.99,
  "piiTags": {
    "userId": {"level": 3, "retention": "RETAIN_7_YEARS"},
    "amount": {"level": 4, "retention": "RETAIN_7_YEARS"}
  }
}
```

### Contract Testing Requirements

1. **Tag Consistency**: PII level must remain consistent or increase (never decrease)
2. **Tag Presence**: All sensitive fields must have tags
3. **Retention Policy**: Must match business requirements
4. **No Tag Loss**: Tags cannot be dropped during service-to-service communication

---

## Implementation Notes

### For Backend Developers
- Add `@PIITag` annotations to entity fields
- Include tag metadata in API responses
- Log access to Level 3+ data

### For QA Engineers
- Verify tags exist in API responses
- Test tag propagation across services
- Validate retention policies are enforced
- Check for tag consistency

### For Security Team
- Audit Level 4 data access
- Verify encryption for Level 3+ data
- Monitor for unauthorized tag changes

---

## Compliance Considerations

- **GDPR**: DELETE_ON_REQUEST fields support right to deletion
- **CCPA**: Users can request data export with all tags visible
- **PCI-DSS**: Level 4 payment data follows card industry standards
- **SOX**: 7-year retention for financial records

---

## Future Enhancements

1. Automated tag enforcement at database level
2. Tag-based access control (TBAC)
3. Automated data anonymization on account deletion
4. Real-time tag audit dashboard
5. Machine learning for automatic tag suggestion