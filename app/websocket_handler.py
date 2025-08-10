import asyncio
import json

set_of_clients = set()


async def websocket_handler(websocket):
    """
    Эта функция вызывается каждый раз, когда новый клиент подключается к серверу.
    """
    print(f"Клиент подключился: {websocket.remote_address}")
    # Добавляем нового клиента в наш набор
    set_of_clients.add(websocket)
    try:
        # Держим соединение открытым, пока клиент не отключится.
        await websocket.wait_closed()
    finally:
        # Как только клиент отключается, удаляем его из набора.
        print(f"Клиент отключился: {websocket.remote_address}")
        set_of_clients.remove(websocket)

async def broadcast(message):
    """
    Отправляет сообщение всем подключенным клиентам.
    """
    # Если клиентов нет, ничего не делаем.
    if not set_of_clients:
        return

    message_json = json.dumps(message)
    await asyncio.gather(
        *(client.send(message_json) for client in set_of_clients)
    )
