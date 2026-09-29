"""AI 主动发消息：每 30 秒敲一次门，AI 自己决定开不开。

两个旋钮必须分开：
- CHECK_EVERY_MS：多久敲一次门。纯成本旋钮，调大只影响"敲门频率"。
- MIN_IDLE_MS：至少晾多久才有资格敲门。手感旋钮，决定"多久不理它才会来一句"。
"""

import asyncio
import json
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from web.models.friend import Friend, Message
from web.views.friend.message.proactive.graph import ProactiveGraph, build_messages


# 多久敲一次门（毫秒）
CHECK_EVERY_MS = 30_000
# 至少多久没说话才允许说话
MIN_IDLE_MS = 90_000
# 多久没说话算"好久不见"（小时）—— 离线补话用。
# 打开页面时若超过这个数，立刻走一次判断（不睡那 30 秒）。
# 调试时嫌等太久可以直接改小，比如 0.05（= 3 分钟）。
OFFLINE_HOURS = 12
# 说出来的话太短 / 太长都判为不合格（字）
MIN_LEN = 4
MAX_LEN = 60

# 在线登记表：friend_id -> 正在敲门的那个哨兵任务。
# ⚠️ 这里存"任务"而不是"连接数"：前端的连接可能泄漏（比如关掉弹窗时没断开），
# 一旦计数不归零，后来的连接就永远只能围观。存任务就能问它一句"你还在跑吗"（.done()），
# 跑完了就让新连接接棒，不会因为一次泄漏而永久卡死。
ONLINE = {}


class ProactiveConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        token = self.get_token()
        if token is None:
            await self.close()
            return
        try:
            user = await self.get_user(token)
        except TokenError:
            print("[Proactive] token 无效或已过期，拒绝连接")
            await self.close()
            return

        await self.accept()

        friend = await self.get_friend(user, self.friend_id)
        if friend is None:
            print(f"[Proactive] 找不到 friend_id={self.friend_id}")
            await self.close()
            return

        self.friend = friend

        # 敲门哨兵：同一个好友只允许一个在跑。
        # ⚠️ 多标签页 / 页面重连会各开一条连接，如果每个连接都开一个哨兵，
        # 两个哨兵可能在同一秒都查到"还没说过话"⇒ 各发一条。
        # 但"上一个哨兵已经跑完"（.done()）不算占用 —— 新连接要能接棒，
        # 否则哨兵一旦结束，这个好友就再也没人敲门了。
        old = ONLINE.get(friend.id)
        if old is None or old.done():
            self.knock = asyncio.create_task(self.knock_loop())
            ONLINE[friend.id] = self.knock                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
            print(f"[Proactive] friend_id={friend.id} 本连接负责敲门")
        else:
            self.knock = None
            print(f"[Proactive] friend_id={friend.id} 已有哨兵在跑，本连接只围观")

    async def disconnect(self, close_code):
        # 先取消任务，否则页面关了任务还挂着（围观连接没有任务，是 None）
        if getattr(self, 'knock', None):
            self.knock.cancel()
            friend = getattr(self, 'friend', None)
            # 只清理"确实是我占着"的登记，别人的登记不能动
            if friend is not None and ONLINE.get(friend.id) is self.knock:
                ONLINE.pop(friend.id, None)
                print(f"[Proactive] friend_id={friend.id} 哨兵已下线")
        print(f"[Proactive] 连接断开，code={close_code}")

    async def knock_loop(self):
        """循环：隔一会儿敲一次门。说过了就歇着，但哨兵本身不会结束。

        ⚠️ 这里不能 return：你回一句话时 chat.py 会把 done 改回 False（解锁），
        但如果哨兵已经结束，就再也没人敲门了 —— "回话就能再被找"这条会失效。
        """
        try:
            # 第 0 步：离线补话。刚连上立刻查一次，不睡那 30 秒。
            # 和下面的"在线冷场"是两个入口、两套门槛，别混：
            #   离线 = "他离开很久刚回来"，门槛 OFFLINE_HOURS（默认 12 小时）
            #   在线 = "他还在，只是没说话"，门槛 MIN_IDLE_MS（90 秒）
            if not await self.refresh_done():
                offline_minutes = await self.idle_minutes()
                if offline_minutes >= OFFLINE_HOURS * 60:
                    print(f"[Proactive] 离线补话：已 {offline_minutes / 60:.1f} 小时没聊")
                    text = await self.ask_ai(offline_minutes)
                    if text is not None:
                        await self.speak(text)

            while True:
                await asyncio.sleep(CHECK_EVERY_MS / 1000)

                # 本轮已经说过了 → 歇着，不发；等你说完话 done 变回 False 再继续
                if await self.refresh_done():
                    continue

                idle_minutes = await self.idle_minutes()
                if idle_minutes * 60_000 < MIN_IDLE_MS:
                    continue

                text = await self.ask_ai(idle_minutes)
                if text is None:
                    continue

                await self.speak(text)
                # 说完不结束：下一轮 done 已是 True，会自动歇着，不空转
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"[Proactive] knock_loop 出错: {e}")

    async def ask_ai(self, idle_minutes):
        """敲门 → AI 决定说不说。不合格返回 None。"""
        try:
            llm = ProactiveGraph.create_app()
            msgs = await sync_to_async(build_messages, thread_sensitive=True)(
                self.friend, idle_minutes
            )
            resp = await llm.ainvoke(msgs)
            raw = (resp.content or '').strip()
        except Exception as e:
            print(f"[Proactive] 调用 AI 失败: {e}")
            return None

        # 闸门①：AI 自己说不说
        if raw.upper() == 'NO' or raw.upper().startswith('NO\n') or raw == '':
            print("[Proactive] AI 决定：不说")
            return None

        # 闸门②：长度
        text = raw.strip().strip('"').strip("'").strip()
        # 万一它多回了一行，只取第一句有意义的
        text = text.split('\n')[0].strip()
        if not (MIN_LEN <= len(text) <= MAX_LEN):
            print(f"[Proactive] 长度不合格（{len(text)} 字），丢弃：{text}")
            return None

        return text

    async def speak(self, text):
        """落库 + 打勾 + 推给浏览器。"""
        try:
            await sync_to_async(self.save_message, thread_sensitive=True)(text)
            await self.send(json.dumps({'text': text}, ensure_ascii=False))
            print(f"[Proactive] 已主动发言：{text}")
        except Exception as e:
            print(f"[Proactive] 落库/推送失败: {e}")

    def save_message(self, text):
        # 先落库（这条消息本身就是"说过话"的证据，别的哨兵也看得到）
        Message.objects.create(
            friend=self.friend,
            user_message='[主动消息]',
            input='',
            output=text[:500],
        )
        # 再打勾
        self.friend.proactive_done = True
        self.friend.update_time = now()
        self.friend.save()

    async def refresh_done(self):
        """重新从库里读 proactive_done（你回话时会被 chat.py 改回 False）。"""
        done = await sync_to_async(
            lambda: Friend.objects.filter(pk=self.friend.pk)
            .values_list('proactive_done', flat=True)
            .first(),
            thread_sensitive=True,
        )()
        return bool(done)

    async def idle_minutes(self):
        """距上次说话过了多少分钟。从没聊过就按好友关系建立时间算。"""
        def _calc():
            last = (
                Message.objects.filter(friend=self.friend)
                .order_by('-id')
                .values_list('create_time', flat=True)
                .first()
            )
            return last or self.friend.update_time

        last = await sync_to_async(_calc, thread_sensitive=True)()
        return (now() - last).total_seconds() / 60

    async def get_user(self, token):
        def _get():
            access = AccessToken(token)
            from django.contrib.auth.models import User
            return User.objects.get(pk=access['user_id'])
        return await sync_to_async(_get, thread_sensitive=True)()

    async def get_friend(self, user, friend_id):
        def _get():
            return Friend.objects.filter(pk=friend_id, me__user=user).first()
        return await sync_to_async(_get, thread_sensitive=True)()

    @property
    def friend_id(self):
        params = parse_qs(self.scope['query_string'].decode())
        values = params.get('friend_id')
        if not values:
            return None
        try:
            return int(values[0])
        except ValueError:
            return None

    def get_token(self):
        params = parse_qs(self.scope['query_string'].decode())
        values = params.get('token')
        if not values:
            return None
        return values[0]
