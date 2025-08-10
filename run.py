import asyncio
import threading
import websockets
from app.main import app
from app.worker import worker_loop
from app.websocket_handler import websocket_handler, set_of_clients

STOP_EVENT = threading.Event()  # Флаг завершения


def run_asyncio_components():
    """Запускает все асинхронные компоненты в одном цикле событий."""

    async def main():
        # Запускаем WebSocket сервер на порту 8888
        ws_server = await websockets.serve(websocket_handler, "localhost", 8888)
        print("WebSocket сервер запущен на ws://localhost:8888")

        # Запускаем воркер
        worker_task = asyncio.create_task(worker_loop(set_of_clients))

        try:
            # Ждём, пока либо сервер, либо флаг STOP_EVENT сработает
            while not STOP_EVENT.is_set():
                await asyncio.sleep(0.1)
        finally:
            print("Остановка WebSocket сервера...")
            ws_server.close()
            await ws_server.wait_closed()

            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


if __name__ == "__main__":
    # Запускаем асинхронные части в отдельном потоке
    worker_thread = threading.Thread(target=run_asyncio_components)
    worker_thread.daemon = True
    worker_thread.start()

    try:
        # Запускаем Flask-приложение
        app.run(debug=True, port=5000, use_reloader=False)
    finally:
        # При остановке Flask — останавливаем WebSocket
        STOP_EVENT.set()
        worker_thread.join()
