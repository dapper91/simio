
import abc
import dataclasses as dc
import socket as sc
from typing import Any, ClassVar

from .typedef import FlowInfo, IPv4Host, IPv6Host, Port, ScopeId


@dc.dataclass
class SocketAddress(abc.ABC):
    FAMILY: ClassVar[sc.AddressFamily]

    @abc.abstractmethod
    def raw(self) -> tuple[Any, ...]: ...


@dc.dataclass
class IPv4Address(SocketAddress):
    FAMILY: ClassVar[sc.AddressFamily] = sc.AddressFamily.AF_INET

    host: IPv4Host
    port: Port

    def raw(self) -> tuple[Any, ...]:
        return self.host, self.port

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"


@dc.dataclass
class IPv6Address(SocketAddress):
    FAMILY: ClassVar[sc.AddressFamily] = sc.AddressFamily.AF_INET6

    host: IPv6Host
    port: Port
    flow_info: FlowInfo
    scope_id: ScopeId

    def raw(self) -> tuple[Any, ...]:
        return self.host, self.port, self.flow_info, self.scope_id

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"
