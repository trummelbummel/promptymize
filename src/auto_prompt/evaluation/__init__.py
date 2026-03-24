"""Stepwise evaluation: Braintrust-backed logging for pipeline steps."""

from auto_prompt.evaluation.config import BraintrustConfig, load_braintrust_config_from_env
from auto_prompt.evaluation.end_to_end import EndToEndTraceStub, build_end_to_end_stub, trace_to_jsonable
from auto_prompt.evaluation.logging import (
    build_context_engineering_record,
    log_step,
    run_step_eval,
)
from auto_prompt.evaluation.observations import iter_observation_jsonl
from auto_prompt.evaluation.records import EvalRecord
from auto_prompt.evaluation.steps import STEP_ORDER, StepId

__all__ = [
    "STEP_ORDER",
    "BraintrustConfig",
    "EndToEndTraceStub",
    "EvalRecord",
    "StepId",
    "build_context_engineering_record",
    "build_end_to_end_stub",
    "iter_observation_jsonl",
    "load_braintrust_config_from_env",
    "log_step",
    "run_step_eval",
    "trace_to_jsonable",
]
