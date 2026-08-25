from fastapi import APIRouter, WebSocket, WebSocketDisconnect


router = APIRouter(
    tags=["WebSocket"]
)


class ConnectionManager:

    def __init__(self):
        self.active_connections = {}


    async def connect(
        self,
        user_id: int,
        websocket: WebSocket
    ):
        await websocket.accept()

        self.active_connections[user_id] = websocket


    def disconnect(
        self,
        user_id: int
    ):
        if user_id in self.active_connections:
            del self.active_connections[user_id]


    async def send_personal_message(
        self,
        user_id: int,
        message: dict
    ):
        websocket = self.active_connections.get(user_id)

        if websocket:
            await websocket.send_json(message)


    async def send_cart_updated(
        self,
        user_id: int,
        cart_data: dict
    ):
        await self.send_personal_message(
            user_id,
            {
                "event": "cart_updated",
                "data": cart_data
            }
        )


    async def send_order_status_updated(
        self,
        user_id: int,
        order_data: dict
    ):
        await self.send_personal_message(
            user_id,
            {
                "event": "order_status_updated",
                "data": order_data
            }
        )


manager = ConnectionManager()


@router.websocket(
    "/ws/{user_id}"
)
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int
):

    await manager.connect(
        user_id,
        websocket
    )

    try:

        await manager.send_personal_message(
            user_id,
            {
                "event": "connected",
                "message": "WebSocket connection established"
            }
        )

        while True:

            data = await websocket.receive_text()

            await manager.send_personal_message(
                user_id,
                {
                    "event": "message_received",
                    "message": data
                }
            )

    except WebSocketDisconnect:

        manager.disconnect(
            user_id
        )