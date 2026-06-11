"""
IAMShield - MongoDB Database Connection & Seed Module
"""
from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = os.getenv("DB_NAME",   "iamshield")

_client = None

def get_db():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client[DB_NAME]


CATEGORIES_SEED = [
    {"_id": "privileged", "name": "Privileged Access",      "icon": "lock",    "color": "#FFD700", "order": 1},
    {"_id": "workforce",  "name": "Workforce IAM",           "icon": "users",   "color": "#4FC3F7", "order": 2},
    {"_id": "customer",   "name": "Customer Identity",       "icon": "globe",   "color": "#81C784", "order": 3},
    {"_id": "governance", "name": "Access Governance",       "icon": "shield",  "color": "#FF8A65", "order": 4},
    {"_id": "network",    "name": "Network & API Security",  "icon": "wifi",    "color": "#CE93D8", "order": 5},
    {"_id": "cloud",      "name": "Cloud Security",          "icon": "cloud",   "color": "#29B6F6", "order": 6},
    {"_id": "zerotrust",  "name": "Zero Trust Architecture", "icon": "verified","color": "#EF5350", "order": 7},
    {"_id": "devops",     "name": "DevOps & Secrets Mgmt",   "icon": "code",    "color": "#66BB6A", "order": 8},
]

QUESTIONS_SEED = [
    # ── Privileged Access ──────────────────────────────────────────────────────
    {"category": "privileged", "order": 1,
     "text": "Who are the privileged users you need to protect?",
     "options": [
         {"value": "sysadmins",   "label": "System Administrators"},
         {"value": "dbadmins",    "label": "Database Administrators"},
         {"value": "cloudadmins", "label": "Cloud Infrastructure Admins"},
         {"value": "devops",      "label": "DevOps / CI-CD Pipelines"},
     ]},
    {"category": "privileged", "order": 2,
     "text": "Which capability matters most to your organization?",
     "options": [
         {"value": "session_recording", "label": "Session Recording & Monitoring"},
         {"value": "vault",             "label": "Credential Vaulting"},
         {"value": "jit_access",        "label": "Just-In-Time Access"},
         {"value": "cloud_entitlement", "label": "Cloud Entitlement Management"},
     ]},
    {"category": "privileged", "order": 3,
     "text": "What is your current privileged access risk level?",
     "options": [
         {"value": "high_risk",    "label": "High – We have had incidents or breaches"},
         {"value": "medium_risk",  "label": "Medium – Gaps exist but no major incidents yet"},
         {"value": "low_risk",     "label": "Low – Basic controls are in place"},
         {"value": "compliance",   "label": "Compliance-driven – Auditors require it"},
     ]},

    # ── Workforce IAM ─────────────────────────────────────────────────────────
    {"category": "workforce", "order": 1,
     "text": "Which workforce groups need identity coverage?",
     "options": [
         {"value": "employees",   "label": "Full-Time Employees"},
         {"value": "contractors", "label": "Contractors & Vendors"},
         {"value": "remote",      "label": "Remote / Hybrid Workers"},
         {"value": "partners",    "label": "Business Partners"},
     ]},
    {"category": "workforce", "order": 2,
     "text": "What is your biggest workforce IAM pain point?",
     "options": [
         {"value": "sso",          "label": "Single Sign-On Complexity"},
         {"value": "lifecycle",    "label": "User Lifecycle Management"},
         {"value": "mfa",          "label": "MFA Rollout & Adoption"},
         {"value": "provisioning", "label": "Automated Provisioning"},
     ]},
    {"category": "workforce", "order": 3,
     "text": "How many users are in your organization?",
     "options": [
         {"value": "small",    "label": "< 500 users"},
         {"value": "medium",   "label": "500 – 5,000 users"},
         {"value": "large",    "label": "5,000 – 50,000 users"},
         {"value": "xlarge",   "label": "50,000+ users"},
     ]},

    # ── Customer Identity ─────────────────────────────────────────────────────
    {"category": "customer", "order": 1,
     "text": "What type of customers are you securing?",
     "options": [
         {"value": "b2c",      "label": "B2C End Consumers"},
         {"value": "b2b",      "label": "B2B Enterprise Clients"},
         {"value": "b2b2c",    "label": "B2B2C Multi-Tenant"},
         {"value": "iot_users","label": "IoT / Device Users"},
     ]},
    {"category": "customer", "order": 2,
     "text": "What is your top customer identity risk?",
     "options": [
         {"value": "account_takeover", "label": "Account Takeover (ATO)"},
         {"value": "fraud",            "label": "Fraudulent Registrations"},
         {"value": "data_privacy",     "label": "Data Privacy Compliance"},
         {"value": "ux_friction",      "label": "Authentication Friction / Drop-off"},
     ]},
    {"category": "customer", "order": 3,
     "text": "What scale of customer logins do you handle per day?",
     "options": [
         {"value": "low_vol",  "label": "< 10,000 logins / day"},
         {"value": "med_vol",  "label": "10K – 1M logins / day"},
         {"value": "high_vol", "label": "1M – 100M logins / day"},
         {"value": "hyper",    "label": "100M+ logins / day (hyperscale)"},
     ]},

    # ── Access Governance ─────────────────────────────────────────────────────
    {"category": "governance", "order": 1,
     "text": "What is driving your governance initiative?",
     "options": [
         {"value": "audit",      "label": "External Audit Requirements"},
         {"value": "regulation", "label": "Regulatory Compliance (SOX, HIPAA)"},
         {"value": "risk",       "label": "Risk Reduction"},
         {"value": "digital_tx", "label": "Digital Transformation"},
     ]},
    {"category": "governance", "order": 2,
     "text": "What is your biggest governance challenge?",
     "options": [
         {"value": "access_reviews", "label": "Access Certification & Reviews"},
         {"value": "role_mgmt",      "label": "Role Management & SoD"},
         {"value": "policy_mgmt",    "label": "Policy Enforcement"},
         {"value": "audit_trail",    "label": "Audit Trail & Reporting"},
     ]},
    {"category": "governance", "order": 3,
     "text": "Which compliance frameworks apply to your organization?",
     "options": [
         {"value": "sox",     "label": "SOX (Sarbanes-Oxley)"},
         {"value": "hipaa",   "label": "HIPAA / HITECH"},
         {"value": "iso27001","label": "ISO 27001 / 27002"},
         {"value": "nist",    "label": "NIST Cybersecurity Framework"},
     ]},

    # ── Network & API Security ────────────────────────────────────────────────
    {"category": "network", "order": 1,
     "text": "Which network resources need protection?",
     "options": [
         {"value": "apis",          "label": "Public / Internal APIs"},
         {"value": "microservices", "label": "Microservices & Containers"},
         {"value": "vpn",           "label": "Remote Access / VPN Replacement"},
         {"value": "cloud_infra",   "label": "Multi-Cloud Infrastructure"},
     ]},
    {"category": "network", "order": 2,
     "text": "What is your biggest network security concern?",
     "options": [
         {"value": "lateral_movement", "label": "Lateral Movement / East-West Traffic"},
         {"value": "api_abuse",        "label": "API Abuse & Bot Traffic"},
         {"value": "zero_trust_impl",  "label": "Zero Trust Implementation"},
         {"value": "visibility",       "label": "Lack of Network Visibility"},
     ]},
    {"category": "network", "order": 3,
     "text": "What is your primary network deployment model?",
     "options": [
         {"value": "on_prem",    "label": "Fully On-Premise"},
         {"value": "hybrid",     "label": "Hybrid (On-Prem + Cloud)"},
         {"value": "cloud_only", "label": "Cloud-Only"},
         {"value": "multi_cloud","label": "Multi-Cloud / Edge"},
     ]},

    # ── Cloud Security ────────────────────────────────────────────────────────
    {"category": "cloud", "order": 1,
     "text": "Which cloud platforms does your organization use?",
     "options": [
         {"value": "aws",    "label": "Amazon Web Services (AWS)"},
         {"value": "azure",  "label": "Microsoft Azure"},
         {"value": "gcp",    "label": "Google Cloud Platform (GCP)"},
         {"value": "multi",  "label": "Multi-Cloud / Hybrid"},
     ]},
    {"category": "cloud", "order": 2,
     "text": "What is your biggest cloud identity challenge?",
     "options": [
         {"value": "excessive_perms", "label": "Excessive Cloud Permissions (Least Privilege)"},
         {"value": "shadow_it",       "label": "Shadow IT & Unmanaged Cloud Resources"},
         {"value": "cloud_misconfig", "label": "Cloud Misconfiguration Risks"},
         {"value": "cross_account",   "label": "Cross-Account / Cross-Cloud Access"},
     ]},
    {"category": "cloud", "order": 3,
     "text": "Which cloud workloads need identity protection?",
     "options": [
         {"value": "serverless",  "label": "Serverless Functions (Lambda / Functions)"},
         {"value": "containers",  "label": "Kubernetes / Container Workloads"},
         {"value": "saas_apps",   "label": "SaaS Applications"},
         {"value": "data_lakes",  "label": "Data Lakes & Analytics Platforms"},
     ]},

    # ── Zero Trust Architecture ───────────────────────────────────────────────
    {"category": "zerotrust", "order": 1,
     "text": "Where are you in your Zero Trust journey?",
     "options": [
         {"value": "zt_planning",    "label": "Just starting – evaluating strategies"},
         {"value": "zt_piloting",    "label": "Piloting – testing in one department"},
         {"value": "zt_expanding",   "label": "Expanding – rolling out across org"},
         {"value": "zt_mature",      "label": "Mature – fully adopted, optimizing"},
     ]},
    {"category": "zerotrust", "order": 2,
     "text": "Which Zero Trust pillar needs the most attention?",
     "options": [
         {"value": "zt_identity",  "label": "Identity Verification (Verify Explicitly)"},
         {"value": "zt_device",    "label": "Device Health & Compliance"},
         {"value": "zt_network",   "label": "Network Micro-Segmentation"},
         {"value": "zt_data",      "label": "Data Classification & Protection"},
     ]},
    {"category": "zerotrust", "order": 3,
     "text": "What is driving your Zero Trust initiative?",
     "options": [
         {"value": "zt_ransomware",  "label": "Ransomware / Lateral Movement Prevention"},
         {"value": "zt_remote",      "label": "Secure Remote Work"},
         {"value": "zt_compliance",  "label": "Compliance & Regulatory Pressure"},
         {"value": "zt_cloud_move",  "label": "Cloud Migration / Digital Transformation"},
     ]},

    # ── DevOps & Secrets Management ───────────────────────────────────────────
    {"category": "devops", "order": 1,
     "text": "What types of secrets need to be managed?",
     "options": [
         {"value": "api_keys",    "label": "API Keys & Tokens"},
         {"value": "db_creds",    "label": "Database Credentials"},
         {"value": "tls_certs",   "label": "TLS Certificates & PKI"},
         {"value": "ssh_keys",    "label": "SSH Keys & Service Accounts"},
     ]},
    {"category": "devops", "order": 2,
     "text": "Which CI/CD platforms are in your pipeline?",
     "options": [
         {"value": "github_actions", "label": "GitHub Actions"},
         {"value": "jenkins",        "label": "Jenkins / GitLab CI"},
         {"value": "azure_devops",   "label": "Azure DevOps"},
         {"value": "argocd",         "label": "ArgoCD / Kubernetes GitOps"},
     ]},
    {"category": "devops", "order": 3,
     "text": "What is your biggest DevOps security gap?",
     "options": [
         {"value": "hardcoded",   "label": "Hardcoded secrets in code / repos"},
         {"value": "rotation",    "label": "Manual / infrequent secret rotation"},
         {"value": "sprawl",      "label": "Secret sprawl across environments"},
         {"value": "audit_devops","label": "Lack of audit trail for secret access"},
     ]},
]

PRODUCTS_SEED = [
    # Privileged Access
    {"id": "pam_enterprise", "name": "PAM Enterprise", "category": "privileged", "price": 24999,
     "description": "Secures privileged accounts across your on-premise and hybrid infrastructure. Every admin session is recorded, credentials are auto-rotated in a vault, and threats are flagged in real time before they escalate.",
     "features": ["Session Recording", "Credential Vault", "Just-In-Time Access", "Threat Analytics", "SIEM Integration"],
     "score_weights": {"sysadmins": 9, "dbadmins": 8, "session_recording": 10, "vault": 9, "jit_access": 7, "high_risk": 9, "medium_risk": 7}},
    {"id": "cloud_pam", "name": "Cloud PAM", "category": "privileged", "price": 18999,
     "description": "Controls who can access your AWS, Azure, and GCP infrastructure without installing agents. Manages cloud entitlements and secrets natively, so DevOps teams stay productive without bypassing security.",
     "features": ["Cloud Entitlement Management", "Secrets Manager", "Agentless Architecture", "Multi-Cloud Support", "DevOps Integration"],
     "score_weights": {"cloudadmins": 10, "devops": 9, "jit_access": 9, "cloud_entitlement": 10, "compliance": 8}},

    # Workforce IAM
    {"id": "workforce_sso", "name": "Workforce SSO Suite", "category": "workforce", "price": 12999,
     "description": "Gives every employee one secure login for all their apps — on any device, from anywhere. Adaptive MFA only challenges users when risk is detected, reducing friction without compromising security.",
     "features": ["Single Sign-On", "Adaptive MFA", "Passwordless Auth", "7000+ App Integrations", "Workforce Insights"],
     "score_weights": {"employees": 8, "remote": 9, "sso": 10, "mfa": 9, "large": 8, "xlarge": 7}},
    {"id": "identity_lifecycle", "name": "Identity Lifecycle Manager", "category": "workforce", "price": 15999,
     "description": "Automatically provisions the right access the moment a new hire joins and revokes it the day they leave. Syncs with your HR system so IT never manually touches an account again.",
     "features": ["Automated Provisioning", "HR System Integration", "Role-Based Access", "Offboarding Automation", "Compliance Reports"],
     "score_weights": {"contractors": 9, "partners": 8, "lifecycle": 10, "provisioning": 10, "medium": 8, "large": 9}},

    # Customer Identity
    {"id": "customer_identity_cloud", "name": "Customer Identity Cloud", "category": "customer", "price": 19999,
     "description": "Handles registration, login, and profile management for your customers at any scale. Social login, passwordless options, and progressive profiling reduce sign-up drop-off while keeping data private.",
     "features": ["Social Login", "Progressive Profiling", "Consent Management", "GDPR Compliance", "99.99% SLA"],
     "score_weights": {"b2c": 10, "b2b2c": 9, "ux_friction": 10, "data_privacy": 8, "high_vol": 9, "hyper": 10}},
    {"id": "fraud_protection", "name": "Fraud Protection Suite", "category": "customer", "price": 22999,
     "description": "Stops account takeovers and fraudulent transactions before they happen. Analyses typing patterns, device behaviour, and risk signals in real time — invisible to legitimate users, blocking to bad actors.",
     "features": ["AI Fraud Detection", "Behavioral Biometrics", "Device Fingerprinting", "Real-Time Risk Scoring", "Bot Detection"],
     "score_weights": {"b2b": 8, "iot_users": 7, "account_takeover": 10, "fraud": 10, "med_vol": 8, "high_vol": 9}},

    # Access Governance
    {"id": "governance_manager", "name": "Governance Manager", "category": "governance", "price": 17999,
     "description": "Automatically reviews who has access to what across your entire organisation and flags violations. Role mining surfaces over-privileged accounts, and SoD enforcement prevents any single user from holding conflicting permissions.",
     "features": ["Access Certifications", "Role Mining", "SoD Enforcement", "Policy Engine", "Executive Dashboards"],
     "score_weights": {"audit": 9, "regulation": 9, "access_reviews": 10, "role_mgmt": 10, "sox": 9, "hipaa": 8}},
    {"id": "compliance_analytics", "name": "Compliance Analytics", "category": "governance", "price": 13999,
     "description": "Prepares your organisation for SOX, HIPAA, ISO 27001, and NIST audits automatically. Collects evidence continuously and generates audit reports so your team spends days on compliance, not months.",
     "features": ["Pre-Built Frameworks", "Automated Evidence Collection", "Audit Trail", "Risk Dashboards", "Regulatory Reporting"],
     "score_weights": {"risk": 9, "digital_tx": 7, "policy_mgmt": 10, "audit_trail": 10, "iso27001": 9, "nist": 9}},

    # Network & API Security
    {"id": "zero_trust_gateway", "name": "Zero Trust Gateway", "category": "network", "price": 21999,
     "description": "Replaces your legacy VPN with access that verifies every user and device before connecting — not just at the perimeter. Each connection is micro-segmented so a breach in one area cannot spread laterally.",
     "features": ["Zero Trust Network Access", "East-West Inspection", "Identity-Aware Proxy", "Continuous Verification", "Micro-Segmentation"],
     "score_weights": {"vpn": 10, "cloud_infra": 9, "lateral_movement": 10, "zero_trust_impl": 10, "hybrid": 8, "cloud_only": 9}},
    {"id": "api_security_platform", "name": "API Security Platform", "category": "network", "price": 16999,
     "description": "Discovers all your APIs (including shadow ones), tests them for vulnerabilities, and blocks attacks at runtime. ML detects abnormal call patterns and OAuth enforcement stops credential abuse.",
     "features": ["API Discovery", "Runtime Protection", "OAuth & JWT Enforcement", "Bot Mitigation", "GraphQL Security"],
     "score_weights": {"apis": 10, "microservices": 9, "api_abuse": 10, "visibility": 9, "multi_cloud": 8}},

    # Cloud Security
    {"id": "cloud_identity_platform", "name": "Cloud Identity Platform", "category": "cloud", "price": 23999,
     "description": "Gives you a single view of every identity and permission across your cloud accounts. Continuously enforces least-privilege, catches misconfigurations before attackers do, and shows you shadow IT you did not know existed.",
     "features": ["Multi-Cloud IAM", "Least-Privilege Enforcement", "Misconfiguration Detection", "Cloud SIEM Integration", "Shadow IT Discovery"],
     "score_weights": {"multi": 10, "aws": 8, "azure": 8, "gcp": 8, "excessive_perms": 10, "cloud_misconfig": 10, "shadow_it": 9}},
    {"id": "cloud_workload_protection", "name": "Cloud Workload Protection", "category": "cloud", "price": 19499,
     "description": "Protects containers and Kubernetes workloads by giving each one a verified identity at runtime. No implicit trust between services — every workload must prove who it is before communicating.",
     "features": ["Workload Identity", "Container Security", "Serverless Protection", "K8s RBAC Enforcement", "Runtime Threat Detection"],
     "score_weights": {"containers": 10, "serverless": 9, "cross_account": 8, "data_lakes": 7, "aws": 7, "gcp": 7}},

    # Zero Trust Architecture
    {"id": "zero_trust_platform", "name": "Zero Trust Security Platform", "category": "zerotrust", "price": 28999,
     "description": "Applies Zero Trust across identity, device, network, and data in one platform. Every access request is continuously verified — even from inside your network — so perimeter breaches cannot turn into full compromises.",
     "features": ["Continuous Verification", "Device Trust Engine", "Network Micro-Segmentation", "Adaptive Access Policies", "ZT Maturity Dashboard"],
     "score_weights": {"zt_identity": 10, "zt_network": 9, "zt_expanding": 9, "zt_mature": 8, "zt_ransomware": 9, "zt_remote": 9}},
    {"id": "device_trust_gateway", "name": "Device Trust & NAC Gateway", "category": "zerotrust", "price": 14999,
     "description": "Checks whether a device is patched, encrypted, and compliant before it touches corporate resources. Unmanaged or risky devices are blocked or quarantined automatically, regardless of valid credentials.",
     "features": ["Device Posture Assessment", "NAC Enforcement", "Endpoint Compliance", "Certificate-Based Auth", "BYOD Support"],
     "score_weights": {"zt_device": 10, "zt_data": 7, "zt_planning": 7, "zt_piloting": 8, "zt_compliance": 9, "zt_cloud_move": 8}},

    # DevOps & Secrets Management
    {"id": "secrets_vault", "name": "Enterprise Secrets Vault", "category": "devops", "price": 11999,
     "description": "Removes hardcoded passwords and API keys from your codebase and pipelines. Secrets are stored centrally, rotated automatically, and injected at runtime — developers never see the actual credentials.",
     "features": ["Auto-Rotation", "Dynamic Secrets", "PKI Management", "CI/CD Integration", "Audit Logging"],
     "score_weights": {"api_keys": 9, "db_creds": 10, "tls_certs": 9, "ssh_keys": 8, "hardcoded": 10, "rotation": 10, "sprawl": 9}},
    {"id": "pipeline_security", "name": "DevSecOps Pipeline Shield", "category": "devops", "price": 13499,
     "description": "Scans every code commit and build for exposed secrets before they reach production. Service accounts get only the permissions they need, and every build artifact is cryptographically signed so you know nothing was tampered with.",
     "features": ["Secrets Scanning", "SAST Integration", "Service Account Mgmt", "Artifact Signing", "GitOps Security"],
     "score_weights": {"github_actions": 10, "jenkins": 9, "azure_devops": 9, "argocd": 9, "hardcoded": 10, "audit_devops": 9}},
]


def seed_database():
    db = get_db()
    seeded = []
    if db.categories.count_documents({}) == 0:
        db.categories.insert_many(CATEGORIES_SEED); seeded.append("categories")
    if db.questions.count_documents({}) == 0:
        db.questions.insert_many(QUESTIONS_SEED); seeded.append("questions")
    if db.products.count_documents({}) == 0:
        db.products.insert_many(PRODUCTS_SEED); seeded.append("products")

    db.assessments.create_index("userId")
    db.assessments.create_index("sessionId", sparse=True)
    db.assessments.create_index([("userId", 1), ("createdAt", -1)])
    db.users.create_index("email", unique=True)

    if seeded:
        print(f"Seeded: {', '.join(seeded)}")
    else:
        print("Database already seeded")


try:
    seed_database()
except Exception as e:
    print(f"MongoDB not available: {e}")


import bcrypt as _bcrypt

def seed_admin():
    db = get_db()
    if db.admins.count_documents({}) == 0:
        hashed = _bcrypt.hashpw(b"admin123", _bcrypt.gensalt())
        db.admins.insert_one({
            "username":  "admin",
            "password":  hashed,
            "createdAt": __import__('datetime').datetime.utcnow()
        })
        db.admins.create_index("username", unique=True)
        print("Admin seeded: username=admin  password=admin123")

try:
    seed_admin()
except Exception as e:
    print(f"Admin seed skipped: {e}")