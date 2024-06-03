from typing import Optional, Callable, Any, Generator, Union

from envd.process import process_pb2
from pydantic import BaseModel


class ProcessOutput(BaseModel):
    stdout: Optional[str] = None
    stderr: Optional[str] = None


class ProcessResult(ProcessOutput):
    exit_code: int
    error: Optional[str]


class ProcessHandle(Generator):
    @property
    def pid(self):
        return self._pid

    def __init__(
        self,
        pid: int,
        handle_kill: Callable[[], None],
        events: Generator[
            Union[process_pb2.StartResponse, process_pb2.ConnectResponse], Any, None
        ],
    ):
        self._pid = pid
        self._handle_kill = handle_kill
        self._events = events

        self._stdout: bytes = b""
        self._stderr: bytes = b""

        self._result: Optional[ProcessResult] = None

    def __next__(self):
        event = next(self._events)

        if event.HasField(field_name="data"):
            if event.event.data.stdout:
                self._stdout += event.event.data.stdout
                return ProcessOutput(stdout=self._stdout.decode())
            if event.event.data.stderr:
                self._stderr += event.event.data.stderr
                return ProcessOutput(stderr=self._stderr.decode())
        if event.HasField("end"):
            self._result = ProcessResult(
                stdout=self._stdout.decode(),
                stderr=self._stderr.decode(),
                exit_code=event.event.end.exit_code,
                error=event.event.end.error,
            )

        raise StopIteration

    def __iter__(self):
        return self

    def close(self) -> None:
        self._events.close()

    def wait(
        self,
        on_stdout: Optional[Callable[[str], None]] = None,
        on_stderr: Optional[Callable[[str], None]] = None,
    ):
        for output in self:
            if output.stdout and on_stdout:
                on_stdout(output.stdout)
            if output.stderr and on_stderr:
                on_stderr(output.stderr)

        if self._result is None:
            raise RuntimeError("Process has not ended")

        return self._result

    def kill(self):
        self.close()
        self._handle_kill()
