"""Deterministic career-domain taxonomy for job matching."""

from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple


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
    PRODUCT = "product"
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
    PRODUCT_MANAGER = "product_manager"
    PRODUCT_ANALYST = "product_analyst"
    PRODUCT_OPERATIONS = "product_operations"
    PRODUCT_ASSISTANT = "product_assistant"


class ProductCapabilityCategory(str, Enum):
    USER_UNDERSTANDING = "user_understanding"
    REQUIREMENT_MANAGEMENT = "requirement_management"
    PRODUCT_PLANNING = "product_planning"
    DATA_ANALYSIS = "data_analysis"
    DELIVERY_COLLABORATION = "delivery_collaboration"


@dataclass(frozen=True, slots=True)
class ProductCapabilityDefinition:
    canonical: str
    category: ProductCapabilityCategory
    direct_aliases: tuple[str, ...]
    transferable_aliases: tuple[str, ...]
    families: tuple[JobFamily, ...]


PRODUCT_JOB_FAMILIES = (
    JobFamily.PRODUCT_MANAGER,
    JobFamily.PRODUCT_ANALYST,
    JobFamily.PRODUCT_OPERATIONS,
    JobFamily.PRODUCT_ASSISTANT,
)


PRODUCT_CAPABILITIES = (
    ProductCapabilityDefinition(
        "用户理解",
        ProductCapabilityCategory.USER_UNDERSTANDING,
        (
            "用户访谈",
            "用户反馈整理",
            "user interview",
            "user feedback analysis",
        ),
        ("customer research", "customer discovery", "customer feedback"),
        PRODUCT_JOB_FAMILIES,
    ),
    ProductCapabilityDefinition(
        "需求管理",
        ProductCapabilityCategory.REQUIREMENT_MANAGEMENT,
        ("PRD", "user story", "requirement document", "feature design"),
        ("requirement collection", "requirements gathering"),
        PRODUCT_JOB_FAMILIES,
    ),
    ProductCapabilityDefinition(
        "产品规划",
        ProductCapabilityCategory.PRODUCT_PLANNING,
        ("产品规划", "roadmap", "product roadmap", "feature prioritization"),
        (),
        PRODUCT_JOB_FAMILIES,
    ),
    ProductCapabilityDefinition(
        "产品数据分析",
        ProductCapabilityCategory.DATA_ANALYSIS,
        ("指标分析", "product metrics", "A/B test", "ab test"),
        ("commercial analysis", "customer data analysis"),
        PRODUCT_JOB_FAMILIES,
    ),
    ProductCapabilityDefinition(
        "交付协作",
        ProductCapabilityCategory.DELIVERY_COLLABORATION,
        (
            "研发协作",
            "上线跟进",
            "product delivery",
            "delivery collaboration",
            "launch follow-up",
        ),
        (
            "stakeholder coordination",
            "cross-functional coordination",
            "cross-team coordination",
        ),
        PRODUCT_JOB_FAMILIES,
    ),
)


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
    CareerDomain.PRODUCT: PRODUCT_JOB_FAMILIES,
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


class DomainSignal(NamedTuple):
    alias: str
    canonical: str
    domain: CareerDomain
    weight: int
    family: JobFamily | None = None


DOMAIN_SIGNALS: tuple[DomainSignal, ...] = (
    DomainSignal("人事行政专员", "人事行政专员", CareerDomain.HUMAN_RESOURCES, 4, JobFamily.HR_GENERALIST),
    DomainSignal("hr generalist", "hr generalist", CareerDomain.HUMAN_RESOURCES, 4, JobFamily.HR_GENERALIST),
    DomainSignal("人事", "人事", CareerDomain.HUMAN_RESOURCES, 3, JobFamily.HR_GENERALIST),
    DomainSignal("招聘专员", "招聘专员", CareerDomain.HUMAN_RESOURCES, 4, JobFamily.RECRUITMENT),
    DomainSignal("recruitment specialist", "recruitment specialist", CareerDomain.HUMAN_RESOURCES, 4, JobFamily.RECRUITMENT),
    DomainSignal("recruitment", "recruitment", CareerDomain.HUMAN_RESOURCES, 3, JobFamily.RECRUITMENT),
    DomainSignal("招聘", "招聘", CareerDomain.HUMAN_RESOURCES, 3, JobFamily.RECRUITMENT),
    DomainSignal("interview coordination", "interview coordination", CareerDomain.HUMAN_RESOURCES, 3, JobFamily.RECRUITMENT),
    DomainSignal("考勤", "考勤", CareerDomain.HUMAN_RESOURCES, 2, JobFamily.COMPENSATION_BENEFITS),
    DomainSignal("薪酬", "薪酬", CareerDomain.HUMAN_RESOURCES, 2, JobFamily.COMPENSATION_BENEFITS),
    DomainSignal("劳动关系", "劳动关系", CareerDomain.HUMAN_RESOURCES, 3, JobFamily.EMPLOYEE_RELATIONS),
    DomainSignal("backend engineer", "backend engineer", CareerDomain.TECHNOLOGY, 4, JobFamily.BACKEND),
    DomainSignal("backend", "backend", CareerDomain.TECHNOLOGY, 3, JobFamily.BACKEND),
    DomainSignal("python", "python", CareerDomain.TECHNOLOGY, 2, JobFamily.BACKEND),
    DomainSignal("fastapi", "fastapi", CareerDomain.TECHNOLOGY, 2, JobFamily.BACKEND),
    DomainSignal("api", "api", CareerDomain.TECHNOLOGY, 2, JobFamily.BACKEND),
    DomainSignal("frontend", "frontend", CareerDomain.TECHNOLOGY, 4, JobFamily.FRONTEND),
    DomainSignal("react", "react", CareerDomain.TECHNOLOGY, 2, JobFamily.FRONTEND),
    DomainSignal("data analyst", "data analyst", CareerDomain.TECHNOLOGY, 4, JobFamily.DATA),
    DomainSignal("sql", "sql", CareerDomain.TECHNOLOGY, 2, JobFamily.DATA),
    DomainSignal("devops", "devops", CareerDomain.TECHNOLOGY, 4, JobFamily.DEVOPS),
    DomainSignal("会计专员", "会计专员", CareerDomain.FINANCE, 4, JobFamily.ACCOUNTING),
    DomainSignal("accountant", "accountant", CareerDomain.FINANCE, 4, JobFamily.ACCOUNTING),
    DomainSignal("会计", "会计", CareerDomain.FINANCE, 3, JobFamily.ACCOUNTING),
    DomainSignal("财务报表", "财务报表", CareerDomain.FINANCE, 3, JobFamily.ACCOUNTING),
    DomainSignal("月度结账", "月度结账", CareerDomain.FINANCE, 3, JobFamily.ACCOUNTING),
    DomainSignal("账目核对", "账目核对", CareerDomain.FINANCE, 2, JobFamily.ACCOUNTING),
    DomainSignal("financial analyst", "financial analyst", CareerDomain.FINANCE, 4, JobFamily.FINANCIAL_ANALYSIS),
    DomainSignal("audit", "audit", CareerDomain.FINANCE, 3, JobFamily.AUDIT_TAX),
    DomainSignal("行政专员", "行政专员", CareerDomain.OPERATIONS, 4, JobFamily.ADMINISTRATION),
    DomainSignal("office administrator", "office administrator", CareerDomain.OPERATIONS, 4, JobFamily.ADMINISTRATION),
    DomainSignal("办公室管理", "办公室管理", CareerDomain.OPERATIONS, 3, JobFamily.ADMINISTRATION),
    DomainSignal("供应商协调", "供应商协调", CareerDomain.OPERATIONS, 2, JobFamily.ADMINISTRATION),
    DomainSignal("流程优化", "流程优化", CareerDomain.OPERATIONS, 2, JobFamily.BUSINESS_OPERATIONS),
    DomainSignal("business operations", "business operations", CareerDomain.OPERATIONS, 4, JobFamily.BUSINESS_OPERATIONS),
    DomainSignal("project operations", "project operations", CareerDomain.OPERATIONS, 4, JobFamily.PROJECT_OPERATIONS),
    DomainSignal("procurement", "procurement", CareerDomain.SUPPLY_CHAIN, 4, JobFamily.PROCUREMENT),
    DomainSignal("logistics", "logistics", CareerDomain.SUPPLY_CHAIN, 4, JobFamily.LOGISTICS),
    DomainSignal("production planner", "production planner", CareerDomain.SUPPLY_CHAIN, 4, JobFamily.PLANNING),
    DomainSignal("production", "production", CareerDomain.MANUFACTURING, 4, JobFamily.PRODUCTION),
    DomainSignal("quality control", "quality control", CareerDomain.MANUFACTURING, 4, JobFamily.QUALITY),
    DomainSignal("maintenance technician", "maintenance technician", CareerDomain.MANUFACTURING, 4, JobFamily.MAINTENANCE),
    DomainSignal("customer support", "customer support", CareerDomain.CUSTOMER_SERVICE, 4, JobFamily.CUSTOMER_SUPPORT),
    DomainSignal("customer success", "customer success", CareerDomain.CUSTOMER_SERVICE, 4, JobFamily.CUSTOMER_SUCCESS),
    DomainSignal("service operations", "service operations", CareerDomain.CUSTOMER_SERVICE, 4, JobFamily.SERVICE_OPERATIONS),
    DomainSignal("business development", "business development", CareerDomain.SALES, 4, JobFamily.BUSINESS_DEVELOPMENT),
    DomainSignal("account manager", "account manager", CareerDomain.SALES, 4, JobFamily.ACCOUNT_MANAGEMENT),
    DomainSignal("sales operations", "sales operations", CareerDomain.SALES, 4, JobFamily.SALES_OPERATIONS),
    DomainSignal("content marketing", "content marketing", CareerDomain.MARKETING, 4, JobFamily.CONTENT_BRAND),
    DomainSignal("digital marketing", "digital marketing", CareerDomain.MARKETING, 4, JobFamily.DIGITAL_MARKETING),
    DomainSignal("market research", "market research", CareerDomain.MARKETING, 4, JobFamily.MARKET_RESEARCH),
    DomainSignal("产品经理", "产品经理", CareerDomain.PRODUCT, 4, JobFamily.PRODUCT_MANAGER),
    DomainSignal("product manager", "product manager", CareerDomain.PRODUCT, 4, JobFamily.PRODUCT_MANAGER),
    DomainSignal("产品分析师", "产品分析师", CareerDomain.PRODUCT, 4, JobFamily.PRODUCT_ANALYST),
    DomainSignal("product analyst", "product analyst", CareerDomain.PRODUCT, 4, JobFamily.PRODUCT_ANALYST),
    DomainSignal("产品运营", "产品运营", CareerDomain.PRODUCT, 4, JobFamily.PRODUCT_OPERATIONS),
    DomainSignal("product operations", "product operations", CareerDomain.PRODUCT, 4, JobFamily.PRODUCT_OPERATIONS),
    DomainSignal("产品助理", "产品助理", CareerDomain.PRODUCT, 4, JobFamily.PRODUCT_ASSISTANT),
    DomainSignal("product assistant", "product assistant", CareerDomain.PRODUCT, 4, JobFamily.PRODUCT_ASSISTANT),
    DomainSignal("product roadmap", "product roadmap", CareerDomain.PRODUCT, 2, JobFamily.PRODUCT_MANAGER),
    DomainSignal("feature prioritization", "feature prioritization", CareerDomain.PRODUCT, 2, JobFamily.PRODUCT_MANAGER),
    DomainSignal("prd", "prd", CareerDomain.PRODUCT, 2),
    DomainSignal("user story", "user story", CareerDomain.PRODUCT, 2),
    DomainSignal("a/b test", "a/b test", CareerDomain.PRODUCT, 2, JobFamily.PRODUCT_ANALYST),
    DomainSignal("product metrics", "product metrics", CareerDomain.PRODUCT, 2, JobFamily.PRODUCT_ANALYST),
)


OCCUPATIONAL_MARKERS = (
    "专员",
    "工程师",
    "教师",
    "经理",
    "顾问",
    "designer",
    "engineer",
    "manager",
    "specialist",
    "teacher",
    "consultant",
)
