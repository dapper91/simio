import asyncio as aio
import logging

from simio import net


async def echo(socket: net.TcpSocket[net.IPv4Address]) -> None:
    data = await socket.recv(1024)
    await socket.sendall(data)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    await net.start_tcp_server(
        net.IPv4Address("127.0.0.1", 8080),
        srv_socket=net.TcpSocketInet(),
        handler=echo,
        graceful_shutdown=10.0,
    )


aio.run(main())
