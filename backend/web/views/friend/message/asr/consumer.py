import asyncio
import json
import os
import uuid
from urllib.parse import parse_qs

import websockets
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken


class ASRConsumer(AsyncWebsocketConsumer):

    # 有连接进来
    async def connect(self):
        # 第一步：从地址里取出 token，验一下身份
        token = self.get_token()
        if token is None:
            await self.close()
            return
        try:
            AccessToken(token)
        except TokenError:
            print("[WS] token 无效或已过期，拒绝连接")
            await self.close()
            return

        await self.accept()
        print("[WS] 身份通过，连接建立")

        # 第二步：连上阿里云
        self.task_id = uuid.uuid4().hex
        api_key = os.getenv("API_KEY")
        wss_url = os.getenv("WSS_URL")
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            self.aliyun = await websockets.connect(wss_url, additional_headers=headers)
        except Exception as e:
            print(f"[WS] 连阿里云失败: {e}")
            await self.close()
            return

        # 第三步：告诉阿里云"开始干活"（照抄 asr.py）
        await self.aliyun.send(json.dumps({
            "header": {
                "streaming": "duplex",
                "task_id": self.task_id,
                "action": "run-task",
            },
            "payload": {
                "model": "gummy-realtime-v1",
                "parameters": {
                    "sample_rate": 16000,
                    "format": "pcm",
                    "transcription_enabled": True,
                },
                "input": {},
                "task": "asr",
                "task_group": "audio",
                "function": "recognition",
            },
        }))

        # 第四步：等阿里云回一句"准备好了"
        while True:
            msg = json.loads(await self.aliyun.recv())
            event = msg["header"]["event"]
            if event == "task-started":
                break
            if event == "task-failed":
                print(f"[WS] 阿里云启动任务失败: {msg}")
                await self.close()
                return

        # 第五步：开个后台任务，专门盯着阿里云的结果
        self.pump = asyncio.create_task(self.pump_results())
        print("[WS] 已连上阿里云，可以开始送音频了")

    # 断开时收尾
    async def disconnect(self, close_code):
        if getattr(self, "pump", None):
            self.pump.cancel()
        if getattr(self, "aliyun", None):
            await self.aliyun.close()
        print(f"[WS] 连接断开，code={close_code}")

    # 浏览器送东西进来
    async def receive(self, text_data=None, bytes_data=None):
        # 二进制 = 音频帧，直接转给阿里云
        if bytes_data is not None:
            await self.aliyun.send(bytes_data)
            return

        # 文本 = 控制消息
        data = json.loads(text_data)
        if data.get("action") == "finish":
            # 说完了，通知阿里云收尾（照抄 asr.py）
            await self.aliyun.send(json.dumps({
                "header": {
                    "action": "finish-task",
                    "task_id": self.task_id,
                    "streaming": "duplex",
                },
                "payload": {"input": {}},
            }))
            print("[WS] 收到结束信号，已通知阿里云收尾")

    # 后台任务：一直读阿里云的结果，转手推给浏览器
    async def pump_results(self):
        try:
            async for msg in self.aliyun:
                data = json.loads(msg)
                event = data["header"]["event"]

                if event == "result-generated":
                    transcription = data["payload"]["output"].get("transcription")
                    if transcription:
                        await self.send(json.dumps({
                            "text": transcription["text"],
                            "final": transcription["sentence_end"],
                        }))

                elif event in ("task-finished", "task-failed"):
                    print(f"[WS] 阿里云收尾: {event}")
                    break
        except Exception as e:
            print(f"[WS] 读阿里云结果时出错: {e}")

        await self.close()

    # 从连接地址里把 token 抠出来
    def get_token(self):
        params = parse_qs(self.scope["query_string"].decode())
        values = params.get("token")
        if not values:
            return None
        return values[0]
