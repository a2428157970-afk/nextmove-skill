"""Provider-neutral Agent Tool descriptions for NextMove capabilities."""

from copy import deepcopy
from typing import Any

from skill.agent.schemas import AgentTool


JsonSchema = dict[str, Any]

RESUME_INPUT_SCHEMA: JsonSchema = {
    "oneOf": [
        {
            "type": "string",
            "description": "Raw resume text.",
        },
        {
            "type": "object",
            "description": "Structured ResumeProfile object.",
            "properties": {
                "personal_information": {"type": "object"},
                "summary": {"type": ["string", "null"]},
                "education": {"type": "array", "items": {"type": "object"}},
                "experience": {"type": "array", "items": {"type": "object"}},
                "skills": {"type": "array", "items": {"type": "string"}},
                "projects": {"type": "array", "items": {"type": "object"}},
                "certifications": {"type": "array", "items": {"type": "string"}},
                "languages": {"type": "array", "items": {"type": "string"}},
                "raw_text": {"type": "string"},
            },
        },
    ]
}

SKILL_ASSESSMENT_OUTPUT_SCHEMA: JsonSchema = {
    "type": "object",
    "properties": {
        "strengths": {"type": "array", "items": {"type": "string"}},
        "gaps": {"type": "array", "items": {"type": "string"}},
        "notes": {"type": ["string", "null"]},
    },
}

RESUME_ANALYSIS_OUTPUT_SCHEMA: JsonSchema = {
    "type": "object",
    "properties": {
        "strengths": {"type": "array", "items": {"type": "string"}},
        "weaknesses": {"type": "array", "items": {"type": "string"}},
        "skill_assessment": SKILL_ASSESSMENT_OUTPUT_SCHEMA,
        "career_level": {
            "type": "string",
            "enum": ["intern", "junior", "mid", "senior", "lead", "unknown"],
        },
    },
}

RESUME_IMPROVEMENT_OUTPUT_SCHEMA: JsonSchema = {
    "type": "object",
    "properties": {
        "issues": {"type": "array", "items": {"type": "string"}},
        "suggestions": {"type": "array", "items": {"type": "string"}},
        "improved_sections": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
    },
}

JOB_MATCH_OUTPUT_SCHEMA: JsonSchema = {
    "type": "object",
    "properties": {
        "match_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "matched_skills": {"type": "array", "items": {"type": "string"}},
        "missing_skills": {"type": "array", "items": {"type": "string"}},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "gaps": {"type": "array", "items": {"type": "string"}},
        "recommendations": {"type": "array", "items": {"type": "string"}},
    },
}

CAREER_ADVICE_OUTPUT_SCHEMA: JsonSchema = {
    "type": "object",
    "properties": {
        "current_level": {"type": "string"},
        "possible_paths": {"type": "array", "items": {"type": "string"}},
        "skill_gaps": {"type": "array", "items": {"type": "string"}},
        "recommended_actions": {"type": "array", "items": {"type": "string"}},
    },
}

CAREER_ANALYSIS_OUTPUT_SCHEMA: JsonSchema = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "analysis": {"oneOf": [RESUME_ANALYSIS_OUTPUT_SCHEMA, {"type": "null"}]},
        "improvement": {
            "oneOf": [RESUME_IMPROVEMENT_OUTPUT_SCHEMA, {"type": "null"}]
        },
        "job_match": {"oneOf": [JOB_MATCH_OUTPUT_SCHEMA, {"type": "null"}]},
        "career_advice": {
            "oneOf": [CAREER_ADVICE_OUTPUT_SCHEMA, {"type": "null"}]
        },
        "failed_capability": {"type": ["string", "null"]},
        "error": {"type": ["object", "null"]},
    },
}


def _object_schema(
    properties: dict[str, JsonSchema],
    required: list[str],
) -> JsonSchema:
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


AGENT_TOOLS: tuple[AgentTool, ...] = (
    AgentTool(
        name="analyze_resume",
        description="Analyze a resume and return strengths, weaknesses, skill assessment, and career level.",
        input_schema=_object_schema(
            properties={"resume": RESUME_INPUT_SCHEMA},
            required=["resume"],
        ),
        output_schema=RESUME_ANALYSIS_OUTPUT_SCHEMA,
    ),
    AgentTool(
        name="improve_resume",
        description="Review a resume and return issues, suggestions, and improved section guidance.",
        input_schema=_object_schema(
            properties={"resume": RESUME_INPUT_SCHEMA},
            required=["resume"],
        ),
        output_schema=RESUME_IMPROVEMENT_OUTPUT_SCHEMA,
    ),
    AgentTool(
        name="match_job",
        description="Compare a resume against a job description and return match score, skill fit, gaps, and recommendations.",
        input_schema=_object_schema(
            properties={
                "resume": RESUME_INPUT_SCHEMA,
                "job_description": {
                    "type": "string",
                    "description": "Target job description text.",
                },
            },
            required=["resume", "job_description"],
        ),
        output_schema=JOB_MATCH_OUTPUT_SCHEMA,
    ),
    AgentTool(
        name="career_advice",
        description="Generate career path guidance from a resume, optionally using an existing resume analysis.",
        input_schema=_object_schema(
            properties={
                "resume": RESUME_INPUT_SCHEMA,
                "analysis": RESUME_ANALYSIS_OUTPUT_SCHEMA,
            },
            required=["resume"],
        ),
        output_schema=CAREER_ADVICE_OUTPUT_SCHEMA,
    ),
    AgentTool(
        name="career_analysis",
        description="Run resume analysis, improvement, job matching, and career advice as one fixed-order report.",
        input_schema=_object_schema(
            properties={
                "resume": RESUME_INPUT_SCHEMA,
                "job_description": {
                    "type": "string",
                    "description": "Target job description text.",
                },
            },
            required=["resume", "job_description"],
        ),
        output_schema=CAREER_ANALYSIS_OUTPUT_SCHEMA,
    ),
)


def get_agent_tools() -> list[AgentTool]:
    """Return independent copies of provider-neutral Agent Tool descriptions."""

    return deepcopy(list(AGENT_TOOLS))
