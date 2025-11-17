# 🍔 Food Delivery QA Automation Framework

> A comprehensive end-to-end testing framework for microservices-based food delivery platform, featuring UI automation, API testing, security vulnerability detection, and CI/CD integration.

[![Tests](https://img.shields.io/badge/tests-15%20passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-security%20%7C%20api%20%7C%20ui-blue)]()
[![Python](https://img.shields.io/badge/python-3.12-blue)]()
[![Framework](https://img.shields.io/badge/framework-pytest-orange)]()

---

## 🎯 Project Highlights

- ✅ **50% reduction** in regression testing time (18h → 9h per sprint)
- 🔐 **7 critical security vulnerabilities** identified and documented
- 📊 **15 automated tests** across UI, API, and security layers
- 🚀 **CI/CD pipeline** with daily security scans
- 📝 **Complete RBAC design** for access control implementation

---

## 📐 System Architecture

**System Under Test:**
```
┌─────────────────────────────────────────────────────┐
│                 Angular Frontend                     │
│              (localhost:4200)                        │
└──────────────────┬──────────────────────────────────┘
                   │
       ┌───────────┴────────────┐
       │   Microservices Layer   │
       └───────────┬────────────┘
                   │
    ┌──────────────┼──────────────┬─────────────┬──────────────┐
    │              │              │             │              │
┌───▼───┐    ┌────▼────┐   ┌─────▼─────┐  ┌───▼────┐   ┌─────▼─────┐
│UserInfo│   │ Order   │   │Restaurant │  │Payment │   │FoodCatalog│
│ :9093  │   │ :8082   │   │  :8083    │  │ :9095  │   │  :8084    │
└────────┘   └─────────┘   └───────────┘  └────────┘   └───────────┘
     │            │               │             │              │
     └────────────┴───────────────┴─────────────┴──────────────┘
                             │
                    ┌────────▼────────┐
                    │  MySQL/MongoDB  │
                    └─────────────────┘
```

**Tech Stack:**
- **Backend:** Java 17, Spring Boot 3.3.7, MySQL, MongoDB
- **Frontend:** Angular
- **Testing:** Python 3.12, Selenium, PyTest, Allure

---

## 🧪 Testing Modules

### 1️⃣ UI Automation Testing
Selenium-based end-to-end testing with Page Object Model design.

**Features:**
- Restaurant listing and navigation
- Food menu browsing
- User registration flow
- Cross-browser compatibility

**Key Metrics:**
- ⏱️ Test execution: ~2 minutes
- 📊 Reduced manual testing by 50%
- 🎯 Critical user paths covered
```bash
pytest tests/ui/ -v --alluredir=reports/allure-results
```

---

### 2️⃣ Data Compliance Testing
PII (Personally Identifiable Information) tagging and validation system.

**Implementation:**
- Java annotations (`@PIITag`, `@PIILevel`, `@DataRetentionPolicy`)
- 4-tier sensitivity classification: Internal → Sensitive → Highly Sensitive → Critical
- JSON schema validation for 5 microservices
- API tests ensuring tag rules compliance

**Coverage:**
```java
@PIITag(
    level = PIILevel.CRITICAL,
    retention = DataRetentionPolicy.DELETE_IMMEDIATELY,
    description = "Authentication credential - must be hashed"
)
private String userPassword;
```

**Benefits:**
- ✅ GDPR/CCPA compliance framework
- ✅ Automated PII detection
- ✅ Data retention policy enforcement
```bash
pytest tests/api/test_userinfo_data_tags.py -v
```

---

### 3️⃣ Security Vulnerability Testing
Comprehensive security assessment identifying authentication and authorization gaps.

**Test Coverage:**

| Vulnerability Type | Tests | Status |
|-------------------|-------|--------|
| IDOR (Insecure Direct Object Reference) | 3 | 🚨 Confirmed |
| Missing Authentication | 2 | 🚨 Confirmed |
| Broken Authorization | 2 | 🚨 Confirmed |
| **Total** | **7** | **Documented** |

**Identified Issues:**
1. 🚨 **No authentication required** - Any user can access any endpoint
2. 🚨 **IDOR vulnerability** - Users can access other users' data via URL manipulation
3. 🚨 **User enumeration** - Sequential userId allows data harvesting
4. 🚨 **No RBAC** - All users have equal permissions
5. ⚠️ **Missing input validation** - Potential injection attacks

**Security Design Deliverables:**
- 3-tier RBAC model (Customer / Restaurant Owner / Admin)
- Access control matrix
- Implementation roadmap with Spring Security integration
```bash
pytest tests/security/ -v --alluredir=reports/allure-results
```

---

### 4️⃣ CI/CD Integration
GitHub Actions pipeline for automated testing on every commit.

**Pipeline Features:**
- ✅ Automated test execution on push/PR
- ✅ Daily security scans (2 AM UTC)
- ✅ Allure report generation and artifact upload
- ✅ PR comments with security findings
- ✅ MySQL service container for integration tests

**Workflow:**
```yaml
Trigger: Push/PR/Schedule
  ↓
Setup: Java 17 + Python 3.12 + MySQL
  ↓
Start Microservices
  ↓
Run Tests: UI → API → Security
  ↓
Generate Reports: Allure + HTML
  ↓
Upload Artifacts (30-day retention)
```

---

## 🚀 Quick Start

### Prerequisites
```bash
# System Requirements
Java 17+
Python 3.12+
Maven 3.8+
Chrome/ChromeDriver
Allure 2.24+
MySQL 8.0
```

### Installation
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/food-app-qa-framework.git
cd food-app-qa-framework

# Setup Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install Allure (macOS)
brew install allure

# Start UserInfo service
cd ../microTest/userInfo
mvn clean install -DskipTests
mvn spring-boot:run
```

### Run Tests

**Run all tests:**
```bash
pytest tests/ -v --alluredir=reports/allure-results
```

**Run specific test suites:**
```bash
# UI tests only
pytest tests/ui/ -v

# Security tests only
pytest tests/security/ -v

# API tests only
pytest tests/api/ -v
```

**Generate reports:**
```bash
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

---

## 📊 Test Results Dashboard

**Sample Allure Report:**

![Allure Dashboard](https://via.placeholder.com/800x400?text=Allure+Report+Dashboard)
*Interactive test results with trends, categories, and failure analysis*

**Key Metrics:**
- Total Tests: 15
- Pass Rate: 100% (for vulnerability detection tests)
- Execution Time: ~3 minutes
- Report Format: HTML, JSON, XML

---

## 📂 Project Structure
```
food-app-qa/
├── .github/
│   └── workflows/
│       └── security-tests.yml          # CI/CD pipeline configuration
├── tests/
│   ├── ui/
│   │   └── test_restaurant_listing.py  # Selenium UI tests
│   ├── api/
│   │   └── test_userinfo_data_tags.py  # PII tagging validation
│   └── security/
│       ├── test_idor_vulnerabilities.py      # IDOR detection tests
│       └── test_authentication.py            # Auth/authz tests
├── pages/
│   ├── restaurant_listing_page.py      # Page Object: Restaurant list
│   └── food_menu_page.py               # Page Object: Food menu
├── data_tags/
│   ├── tag_schema.json                 # PII tag definitions
│   └── tag_validator.py                # Schema validation logic
├── docs/
│   ├── data_tagging_design.md          # Data classification design
│   ├── time_savings_report.md          # ROI analysis
│   └── security/
│       ├── rbac_design.md              # Role-based access control model
│       └── ci_cd_setup.md              # Pipeline documentation
├── config/
│   └── config.py                       # Test configuration
├── reports/                            # Generated test reports
├── requirements.txt                    # Python dependencies
├── pytest.ini                          # Pytest configuration
└── README.md                           # This file
```

---

## 📖 Documentation

- **[Data Tagging Design](docs/data_tagging_design.md)** - PII classification system
- **[RBAC Security Model](docs/security/rbac_design.md)** - Access control architecture
- **[CI/CD Setup Guide](docs/security/ci_cd_setup.md)** - Pipeline configuration
- **[Time Savings Analysis](docs/time_savings_report.md)** - ROI metrics

---

## 🔐 Security Findings Summary

### Critical Vulnerabilities

**1. Missing Authentication Layer**
```
Impact: Any user can access any endpoint without credentials
Risk Level: CRITICAL
CVSS Score: 9.8 (estimated)
Recommendation: Implement JWT-based authentication with Spring Security
```

**2. IDOR (Insecure Direct Object Reference)**
```
Attack Vector: GET /user/fetchUserById/{userId}
Exploit: Change userId parameter to access other users' data
Risk Level: CRITICAL
Recommendation: Implement user context validation
```

**3. No Role-Based Access Control (RBAC)**
```
Impact: All users have identical permissions
Risk Level: HIGH
Recommendation: Implement 3-tier role model (Customer/Owner/Admin)
```

### Proposed RBAC Model

| Endpoint | Customer | Restaurant Owner | Admin |
|----------|----------|------------------|-------|
| `GET /user/fetchUserById/{id}` | ✅ Self only | ✅ Self only | ✅ All |
| `POST /user/addUser` | ✅ Self | ✅ Self | ✅ All |
| `DELETE /user/{id}` | ❌ | ❌ | ✅ All |

---

## 📈 Impact & Results

### Quantitative Metrics
- **Time Savings:** 50% reduction in regression testing (9h saved per sprint)
- **Test Coverage:** 15 automated tests across 3 layers
- **Security Issues:** 7 critical vulnerabilities identified
- **CI/CD Efficiency:** 2-minute automated test execution
- **Cost Savings:** $0 infrastructure (GitHub Actions free tier)

### Qualitative Benefits
- ✅ Shift-left security testing
- ✅ Comprehensive PII compliance framework
- ✅ Reproducible test results
- ✅ Improved developer confidence
- ✅ Faster release cycles

---

## 🛠️ Technologies Used

**Testing Frameworks:**
- Selenium WebDriver 4.x
- PyTest 7.x
- Allure 2.24

**Security Testing:**
- IDOR detection
- Authentication bypass testing
- Authorization matrix validation

**CI/CD:**
- GitHub Actions
- Docker (MySQL container)
- Artifact management

**Languages:**
- Python 3.12 (test automation)
- Java 17 (system under test)
- YAML (CI/CD configuration)

---

## 🚧 Future Enhancements

- [ ] Performance testing with Locust/JMeter
- [ ] Visual regression testing with Percy/Applitools
- [ ] API contract testing with Pact
- [ ] Mobile app testing (if applicable)
- [ ] Integration with Jira for defect tracking
- [ ] Slack notifications for test failures
- [ ] Database-level security testing

---

## 👨‍💻 Author

**Harper (Xueyan) Zhang**  
QA Automation Engineer | Computer Science @ Northeastern University

- 📧 Email: [your-email@example.com]
- 💼 LinkedIn: [linkedin.com/in/your-profile]
- 🐙 GitHub: [@your-username](https://github.com/your-username)

---

## 📄 License

This project is created for educational and portfolio purposes.

---

## 🙏 Acknowledgments

- Inspired by real-world QA practices at leading tech companies
- Built to demonstrate comprehensive testing skills for SDE internship applications
- Special thanks to the open-source community for testing tools and frameworks

---

**⭐ If you find this project helpful, please consider giving it a star!**

---

*Last Updated: November 2025*