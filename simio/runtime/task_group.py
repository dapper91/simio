import asyncio as aio
import logging
from types import TracebackType
from typing import Any, Coroutine, Literal, Optional, Self

logger = logging.getLogger(__package__)


class TaskGroup:
    """
    A group of tasks that supports exit timeout and optional tasks exception propagation.
    """

    def __init__(
            self,
            timeout: Optional[float] = None,
            exit_when: Literal['ALL_COMPLETED', 'FIRST_COMPLETED', 'FIRST_EXCEPTION'] = aio.ALL_COMPLETED,
            propagate_exceptions: bool = False,
    ):
        self._timeout = timeout
        self._exit_when = exit_when
        self._propagate_exceptions = propagate_exceptions
        self._tasks: set[aio.Task[None]] = set()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
            self,
            exc_type: Optional[type[Exception]],
            exc_val: Optional[Exception],
            exc_tb: Optional[TracebackType],
    ) -> bool:
        if not self._tasks:
            return False

        done, pending = await aio.wait(self._tasks, timeout=self._timeout, return_when=self._exit_when)
        for task in done:
            self._on_task_done(task)
        for task in pending:
            task.cancel()

        task_exceptions: list[Exception] = []
        for task in pending:
            try:
                await task
            except aio.CancelledError:
                pass
            except Exception as exc:
                if self._propagate_exceptions:
                    task_exceptions.append(exc)
                else:
                    logger.exception("task %s raised an exception: %s", task.get_name(), exc)
            finally:
                self._on_task_done(task)

        if task_exceptions:
            raise ExceptionGroup("unhandled tasks exceptions", task_exceptions)

        return False

    def create_task(self, coro: Coroutine[Any, Any, None], name: Optional[str] = None) -> aio.Task[None]:
        """
        Creates a task and adds it to the group.
        """

        task = aio.create_task(coro, name=name)
        task.add_done_callback(self._on_task_done)

        self._tasks.add(task)

        return task

    def _on_task_done(self, task: aio.Task[None]) -> None:
        self._tasks.discard(task)
