import json
import re

from django.utils.timezone import now
from langchain_core.messages import SystemMessage, HumanMessage

from web.models.friend import SystemPrompt, Message
from web.views.friend.message.memory.graph import MemoryGraph


def create_system_message():
    system_prompts = SystemPrompt.objects.filter(title='记忆').order_by('order_number')
    prompt = ''
    for sp in system_prompts:
        prompt += sp.prompt
    return SystemMessage(prompt)


def create_human_message(friend):
    prompt = f'【原始记忆】\n{friend.memory}\n'
    prompt += f'【最近对话】\n'
    messages = list(Message.objects.filter(friend=friend).order_by('-id')[:10])
    messages.reverse()
    for m in messages:
        prompt += f'user: {m.user_message}\n'
        prompt += f'ai: {m.output}\n'
    return HumanMessage(prompt)


def update_memory(friend):
    try:
        app = MemoryGraph.create_app()
        inputs = {
            'messages': [
                create_system_message(),
                create_human_message(friend),
            ]
        }
        res = app.invoke(inputs)
        raw = res['messages'][-1].content
    except Exception:
        return                                  # ① 调用失败 → 保留旧记忆

    text = re.sub(r'^```(?:json)?\s*|\s*```$', '', (raw or '').strip())

    try:
        data = json.loads(text)
        new_memory = (data.get('memory_summary') or '').strip()
    except (json.JSONDecodeError, AttributeError):
        return                                  # ② 解析不出来 → 保留旧记忆

    if not new_memory:
        return                                  # ③ 取到空的 → 保留旧记忆

    friend.memory = new_memory
    friend.update_time = now()
    friend.save()
