"""Stepwise evaluation: Braintrust-backed logging for pipeline steps."""

from auto_prompt.evaluation.config import BraintrustConfig, load_braintrust_config_from_env
from auto_prompt.evaluation.contradiction_scoring import score_instruction_contradictions
from auto_prompt.evaluation.end_to_end import EndToEndTraceStub, build_end_to_end_stub, trace_to_jsonable
from auto_prompt.evaluation.logging import (
    build_agent_turn_record,
    build_context_engineering_record,
    build_end_to_end_record,
    build_scraper_markdown_record,
    log_step,
    run_step_eval,
)
from auto_prompt.evaluation.observations import iter_observation_jsonl
from auto_prompt.evaluation.records import EvalRecord
from auto_prompt.evaluation.steps import STEP_ORDER, StepId

__all__ = [
    "STEP_ORDER",
    "BraintrustConfig",
    "build_agent_turn_record",
    "EndToEndTraceStub",
    "EvalRecord",
    "StepId",
    "score_instruction_contradictions",
    "build_context_engineering_record",
    "build_end_to_end_record",
    "build_end_to_end_stub",
    "build_scraper_markdown_record",
    "iter_observation_jsonl",
    "load_braintrust_config_from_env",
    "log_step",
    "run_step_eval",
    "trace_to_jsonable",
]
