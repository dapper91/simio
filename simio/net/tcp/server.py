import asyncio as aio
import logging
import socket as sc
from typing import Any, Callable, Coroutine, Optional, Protocol

from simio.net.address import SocketAddress
from simio.runtime import TaskGroup

from .socket import TcpSocket

logger = logging.getLogger(__package__)


class Handler[AddressT: SocketAddress](Protocol):
    async def __call__(self, socket: TcpSocket[AddressT], /) -> None: ...


async def start_tcp_server[AddressT: SocketAddress](
        address: AddressT,
        handler: Handler[AddressT],
        *,
        srv_socket: TcpSocket[AddressT],
        backlog: int = 128,
        reuse_address: bool = True,
        graceful_shutdown: Optional[float] = None,
) -> None:
    """
    Starts TCP socket server.

    :param address: address to bind to
    :param handler: client socket handler
    :param srv_socket: server socket
    :param backlog: number of unaccepted connections that the system will allow before refusing new connections
    :param reuse_address: reuse bind address
    :param graceful_shutdown: period of time during which the server waits for handlers to complete
                              before canceling them
    """

    logger.info("starting server on %s", address)

    async with srv_socket:
        if reuse_address:
            srv_socket.setsockopt(sc.SOL_SOCKET, sc.SO_REUSEADDR, 1)

        srv_socket.bind(address)
        srv_socket.listen(backlog)

        async with TaskGroup(timeout=graceful_shutdown) as handlers:
            while True:
                try:
                    cli_socket, address = await srv_socket.accept()
                except aio.CancelledError:
                    break

                handlers.create_task(_handle_client_socket(handler, cli_socket))


async def _handle_client_socket[TcpSocketT: TcpSocket[Any]](
        handler: Callable[[TcpSocketT], Coroutine[None, None, None]],
        socket: TcpSocketT,
) -> None:
    logger.info("client %s connected", socket.getpeername())

    async with socket:
        try:
            await handler(socket)
        except Exception as e:
            logger.exception("client %s handling error: %s", socket.getpeername(), e)

        logger.info("client %s disconnected", socket.getpeername())
