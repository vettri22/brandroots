import os
import json
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.config import settings

class LLMAnalysisResult(BaseModel):
    findings: List[Dict[str, Any]]
    model_name: str
    provider_type: str
    is_external_api: bool

class BaseLLMService:
    def analyze_content(
        self,
        text: str,
        rules: List[Dict[str, Any]],
        facts: List[Dict[str, Any]],
        terminology: List[Dict[str, Any]]
    ) -> LLMAnalysisResult:
        raise NotImplementedError

class LocalHybridService(BaseLLMService):
    """
    Intelligent local compliance analyzer.
    Used when external API keys are not configured or in offline/development mode.
    Explicitly labeled as 'local_hybrid_deterministic' to ensure 100% transparent reporting.
    """
    def analyze_content(
        self,
        text: str,
        rules: List[Dict[str, Any]],
        facts: List[Dict[str, Any]],
        terminology: List[Dict[str, Any]]
    ) -> LLMAnalysisResult:
        findings = []
        text_lower = text.lower()

        # 1. Check Approved Facts (e.g. outdated pricing or numerical claims)
        for fact in facts:
            if not fact.get("is_active", True):
                continue
            prohibited_vals = fact.get("prohibited_old_values") or []
            for old_val in prohibited_vals:
                if old_val.lower() in text_lower:
                    idx = text_lower.find(old_val.lower())
                    actual_snippet = text[idx:idx + len(old_val)]
                    findings.append({
                        "category": "pricing" if "price" in fact.get("category", "") else "fact_conflict",
                        "severity": "critical",
                        "confidence": "deterministic_verified",
                        "location_start": idx,
                        "location_end": idx + len(old_val),
                        "affected_text": actual_snippet,
                        "explanation": f"Draft uses outdated figure '{actual_snippet}'. Current approved fact '{fact.get('id')}' states: {fact.get('claim_statement')}.",
                        "rule_id": fact.get("id"),
                        "rule_version": fact.get("version", 1),
                        "source_reference": fact.get("source_document"),
                        "suggested_correction": fact.get("canonical_value") or fact.get("claim_statement"),
                        "status": "open"
                    })

        # 2. Check Approved Terminology (preferred vs prohibited variants)
        for term in terminology:
            if not term.get("is_active", True):
                continue
            prohibited = term.get("prohibited_variants") or []
            for bad_term in prohibited:
                pattern = re.compile(rf"\b{re.escape(bad_term)}\b", re.IGNORECASE)
                for match in pattern.finditer(text):
                    start, end = match.span()
                    snippet = text[start:end]
                    findings.append({
                        "category": "terminology",
                        "severity": "medium",
                        "confidence": "deterministic_verified",
                        "location_start": start,
                        "location_end": end,
                        "affected_text": snippet,
                        "explanation": f"Prohibited term '{snippet}' found. Use approved brand terminology: '{term.get('preferred_term')}'. Rationale: {term.get('rationale')}",
                        "rule_id": term.get("id"),
                        "rule_version": term.get("version", 1),
                        "source_reference": "Brand Terminology Glossary 2026",
                        "suggested_correction": term.get("preferred_term"),
                        "status": "open"
                    })

        # 3. Check Brand Guidelines (voice, promotional claims, guarantees, disclaimers)
        for rule in rules:
            if not rule.get("is_active", True):
                continue
            rule_id = rule.get("id")
            rule_text = rule.get("rule_text")
            patterns = rule.get("prohibited_patterns") or []

            # Deterministic pattern matching
            for pat in patterns:
                regex = re.compile(rf"\b{re.escape(pat)}\b", re.IGNORECASE)
                for match in regex.finditer(text):
                    start, end = match.span()
                    snippet = text[start:end]
                    findings.append({
                        "category": rule.get("category", "promotional_claim"),
                        "severity": rule.get("severity", "warning"),
                        "confidence": "rule_pattern_match",
                        "location_start": start,
                        "location_end": end,
                        "affected_text": snippet,
                        "explanation": f"Violates rule '{rule_id}' ({rule.get('title')}): {rule_text}",
                        "rule_id": rule_id,
                        "rule_version": rule.get("version", 1),
                        "source_reference": rule.get("source_reference") or "Approved Brand Guidelines v" + str(rule.get("version", 1)),
                        "suggested_correction": f"Replace or qualify '{snippet}' to avoid unverified promises",
                        "status": "open"
                    })

            # Check for required disclaimers if condition met
            req_phrases = rule.get("required_phrases") or []
            if req_phrases:
                for req in req_phrases:
                    if req.lower() not in text_lower:
                        # If promotional text exists, disclaimer is required
                        if any(w in text_lower for w in ["pricing", "cost", "trial", "results", "effective"]):
                            findings.append({
                                "category": "disclaimer",
                                "severity": "high",
                                "confidence": "rule_condition_match",
                                "location_start": len(text),
                                "location_end": len(text),
                                "affected_text": "[End of document / Footer]",
                                "explanation": f"Mandatory disclaimer missing per guideline '{rule_id}': '{req}'",
                                "rule_id": rule_id,
                                "rule_version": rule.get("version", 1),
                                "source_reference": rule.get("source_reference"),
                                "suggested_correction": f"Add required disclosure: '{req}'",
                                "status": "open"
                            })

            # Check contextual claims: unsupported guarantees
            if "guarantee" in rule_text.lower() or "claim" in rule.get("category", "").lower():
                guarantee_regex = re.compile(
                    r"\b(guaranteed\s+(results|success|roi|outcome|cure)|100%\s+(effective|money-back|foolproof)|zero\s+risk|miracle\s+cure)\b",
                    re.IGNORECASE
                )
                for match in guarantee_regex.finditer(text):
                    start, end = match.span()
                    snippet = text[start:end]
                    # Avoid duplicate if already caught by prohibited_patterns
                    if not any(f["location_start"] == start and f["location_end"] == end for f in findings):
                        findings.append({
                            "category": "promotional_claim",
                            "severity": "critical",
                            "confidence": "contextual_heuristic",
                            "location_start": start,
                            "location_end": end,
                            "affected_text": snippet,
                            "explanation": f"Draft contains absolute outcome guarantee '{snippet}'. Per guideline '{rule_id}', unsupported guarantees violate compliance policy unless backed by an explicit clinical/audited SLA certificate.",
                            "rule_id": rule_id,
                            "rule_version": rule.get("version", 1),
                            "source_reference": rule.get("source_reference") or "Brand Compliance Playbook",
                            "suggested_correction": "proven track record and measured clinical efficacy in peer-reviewed trials",
                            "status": "open"
                        })

        return LLMAnalysisResult(
            findings=findings,
            model_name="local-hybrid-rules-v2.0",
            provider_type="local_hybrid_deterministic",
            is_external_api=False
        )

def get_llm_service() -> BaseLLMService:
    # If external API is configured and key exists, can initialize ExternalAPILLMService.
    # Otherwise cleanly fall back to LocalHybridService with explicit labeling.
    return LocalHybridService()
