from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from web.models.friend import Message


class GetHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            last_message_id = int(request.query_params.get('last_message_id'))
            friend_id = request.query_params.get('friend_id')
            queryset = Message.objects.filter(friend_id=friend_id, friend__me__user=request.user)
            if last_message_id > 0:
                queryset = queryset.filter(pk__lt=last_message_id)
            messages_raw = queryset.order_by('-id')[:10]
            messages = []
            for m in messages_raw:
                messages.append({
                    'id': m.id,
                    # ⚠️ AI 主动发言那行记录里，user_message 是个占位符（'[主动消息]'）。
                    # 它是给数据库占位用的，不是"你说的话" —— 原样发给前端会渲染成
                    # 一个写着「[主动消息]」的绿色气泡。这里置空，前端就不会画它。
                    # （前端 Message.vue 有 v-if="message.content"，空串不渲染）
                    # AI 说的那句在 output 里，照常显示。
                    'user_message': '' if m.user_message == '[主动消息]' else m.user_message,
                    'output': m.output,
                    # 带时区的时间戳（ISO 8601，例：2026-09-20T14:32:05+08:00）
                    # 前端 new Date(...) 能直接解析，且自带时区信息，不怕浏览器时区不同
                    'create_time': m.create_time.isoformat(),
                })
            return Response({
                'result': 'success',
                'messages': messages,
            })
        except:
            return Response({
                'result': '系统异常，请稍后重试'
            })
