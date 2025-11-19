from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol, Union

# Public types
Context = Dict[str, Any]
Result = Dict[str, Any]


class StepFn(Protocol):
    def __call__(self, ctx: Context) -> Union[Result, Awaitable[Result]]: ...


@dataclass(frozen=True)
class Step:
    name: str
    run: StepFn


class Pipeline:
    def __init__(self, steps: List[Step]):
        self._steps = steps

    async def run(self, ctx: Optional[Context] = None) -> Context:
        context: Context = {} if ctx is None else dict(ctx)
        for step in self._steps:
            out = step.run(context)
            if hasattr(out, "__await__"):
                out = await out  # type: ignore[assignment]
            if not isinstance(out, dict):
                raise TypeError(f"Step '{step.name}' must return dict, got {type(out)}")
            # Merge non-destructively: new keys win, existing preserved unless same key
            # To avoid side-effects, we merge shallowly and do not mutate incoming ctx
            context = {**context, **out}
        return context


def step(name: str):
    def wrapper(fn: StepFn) -> Step:
        return Step(name=name, run=fn)
    return wrapper
