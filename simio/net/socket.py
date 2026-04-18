import socket as sc
from types import TracebackType
from typing import ClassVar, Optional, Self, Union

from .address import SocketAddress


class Socket[AddressT: SocketAddress]:
    """
    Asynchronous socket.

    :param stype: socket type
    :param proto: socket type protocol
    :param raw: standard library socket
    """

    ADDRESS_TYPE: ClassVar[type[AddressT]]

    def __init__(
            self,
            stype: sc.SocketKind,
            proto: int = -1,
            raw: Optional[sc.socket] = None,
    ):
        self._raw = raw or sc.socket(self.ADDRESS_TYPE.FAMILY, stype, proto)
        self._raw.setblocking(False)

    async def __aenter__(self) -> Self:
        self._raw.__enter__()
        return self

    async def __aexit__(
            self,
            exc_type: Optional[type[Exception]],
            exc_val: Optional[Exception],
            exc_tb: Optional[TracebackType],
    ) -> bool:
        self._raw.__exit__(exc_type, exc_val, exc_tb)
        return False

    @property
    def raw(self) -> sc.socket:
        return self._raw

    @property
    def family(self) -> sc.AddressFamily:
        return self._raw.family

    @property
    def type(self) -> int:
        return self._raw.type

    @property
    def proto(self) -> int:
        return self._raw.proto

    def fileno(self) -> int:
        return self._raw.fileno()

    def shutdown(self, how: int, /) -> None:
        return self._raw.shutdown(how)

    def close(self) -> None:
        self._raw.close()

    def getpeername(self) -> AddressT:
        return self._raw.getpeername()

    def getsockname(self) -> AddressT:
        return self._raw.getsockname()

    def getsockopt(self, level: int, option: int) -> int:
        return self._raw.getsockopt(level, option)

    def setsockopt(self, level: int, option: int, value: Union[int, bytes, bytearray, memoryview]) -> None:
        self._raw.setsockopt(level, option, value)
