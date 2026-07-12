"""Deterministic career-domain taxonomy for job matching."""

from enum import Enum


class CareerDomain(str, Enum):
    HUMAN_RESOURCES = "human_resources"
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    SALES = "sales"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    SUPPLY_CHAIN = "supply_chain"
    MANUFACTURING = "manufacturing"
    CUSTOMER_SERVICE = "customer_service"
    OTHER = "other"
    UNKNOWN = "unknown"


class JobFamily(str, Enum):
    HR_GENERALIST = "hr_generalist"
    RECRUITMENT = "recruitment"
    COMPENSATION_BENEFITS = "compensation_benefits"
    EMPLOYEE_RELATIONS = "employee_relations"
    BACKEND = "backend"
    FRONTEND = "frontend"
    DATA = "data"
    DEVOPS = "devops"
    ACCOUNTING = "accounting"
    FINANCIAL_ANALYSIS = "financial_analysis"
    AUDIT_TAX = "audit_tax"
    BUSINESS_DEVELOPMENT = "business_development"
    ACCOUNT_MANAGEMENT = "account_management"
    SALES_OPERATIONS = "sales_operations"
    CONTENT_BRAND = "content_brand"
    DIGITAL_MARKETING = "digital_marketing"
    MARKET_RESEARCH = "market_research"
    BUSINESS_OPERATIONS = "business_operations"
    PROJECT_OPERATIONS = "project_operations"
    ADMINISTRATION = "administration"
    PROCUREMENT = "procurement"
    LOGISTICS = "logistics"
    PLANNING = "planning"
    PRODUCTION = "production"
    QUALITY = "quality"
    MAINTENANCE = "maintenance"
    CUSTOMER_SUPPORT = "customer_support"
    CUSTOMER_SUCCESS = "customer_success"
    SERVICE_OPERATIONS = "service_operations"


DOMAIN_FAMILIES: dict[CareerDomain, tuple[JobFamily, ...]] = {
    CareerDomain.HUMAN_RESOURCES: (
        JobFamily.HR_GENERALIST,
        JobFamily.RECRUITMENT,
        JobFamily.COMPENSATION_BENEFITS,
        JobFamily.EMPLOYEE_RELATIONS,
    ),
    CareerDomain.TECHNOLOGY: (
        JobFamily.BACKEND,
        JobFamily.FRONTEND,
        JobFamily.DATA,
        JobFamily.DEVOPS,
    ),
    CareerDomain.FINANCE: (
        JobFamily.ACCOUNTING,
        JobFamily.FINANCIAL_ANALYSIS,
        JobFamily.AUDIT_TAX,
    ),
    CareerDomain.SALES: (
        JobFamily.BUSINESS_DEVELOPMENT,
        JobFamily.ACCOUNT_MANAGEMENT,
        JobFamily.SALES_OPERATIONS,
    ),
    CareerDomain.MARKETING: (
        JobFamily.CONTENT_BRAND,
        JobFamily.DIGITAL_MARKETING,
        JobFamily.MARKET_RESEARCH,
    ),
    CareerDomain.OPERATIONS: (
        JobFamily.BUSINESS_OPERATIONS,
        JobFamily.PROJECT_OPERATIONS,
        JobFamily.ADMINISTRATION,
    ),
    CareerDomain.SUPPLY_CHAIN: (
        JobFamily.PROCUREMENT,
        JobFamily.LOGISTICS,
        JobFamily.PLANNING,
    ),
    CareerDomain.MANUFACTURING: (
        JobFamily.PRODUCTION,
        JobFamily.QUALITY,
        JobFamily.MAINTENANCE,
    ),
    CareerDomain.CUSTOMER_SERVICE: (
        JobFamily.CUSTOMER_SUPPORT,
        JobFamily.CUSTOMER_SUCCESS,
        JobFamily.SERVICE_OPERATIONS,
    ),
    CareerDomain.OTHER: (),
    CareerDomain.UNKNOWN: (),
}


ADJACENT_DOMAINS = frozenset(
    {
        (CareerDomain.OPERATIONS, CareerDomain.SUPPLY_CHAIN),
        (CareerDomain.SUPPLY_CHAIN, CareerDomain.OPERATIONS),
        (CareerDomain.OPERATIONS, CareerDomain.CUSTOMER_SERVICE),
        (CareerDomain.CUSTOMER_SERVICE, CareerDomain.OPERATIONS),
        (CareerDomain.SALES, CareerDomain.MARKETING),
        (CareerDomain.MARKETING, CareerDomain.SALES),
    }
)
