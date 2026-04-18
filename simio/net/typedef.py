import ipaddress as ip
from typing import TypeAlias, Union

IPv4Host: TypeAlias = Union[ip.IPv4Address, str]
Port: TypeAlias = int

IPv6Host: TypeAlias = Union[ip.IPv6Address, str]
FlowInfo: TypeAlias = int
ScopeId: TypeAlias = int
