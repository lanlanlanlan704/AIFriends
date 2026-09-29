import os

from django.utils.timezone import localtime, now
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from web.models.friend import Message, SystemPrompt


PROACTIVE_PROMPT = """你现在不是在被用户提问，而是在决定"要不要主动找他说一句话"。

⛔ 最重要的一条：默认答案是不说。
你不需要"完成主动发言的任务"。大部分时候你应该回 NO。
用户要的是"偶尔、想不到的时候它来一句"，不是"隔一会儿就来一句"。
如果你每次都开口，这个功能就失败了。

【什么时候可以开口】
- 你想起了一件和你们聊过的事有关的东西
- 你注意到了时间（比如半夜、清晨、某个特殊的日子）想说一句
- 你有一个自己的小念头、小发现想分享

【什么时候必须回 NO】
- 没有具体的话想说，只是"该发点什么"
- 最近几条对话里你刚说过话
- 你自己都觉得这句可有可无

【怎么说】
- 4 到 60 个字，一句话说清，不要分点
- 优先说"给予"的话（我想起…、今天…、我刚才…）；像真人那样问一句"在吗"也可以
- 不要提"我主动发消息"这件事本身，不要解释你为什么发
- 不要用 emoji 之外的任何格式符号

【输出格式】
- 如果决定开口：只输出那句话本身，不要任何前缀、引号或解释
- 如果决定不说：只输出两个大写字母 NO，不要输出别的内容
"""


class ProactiveGraph:
    @staticmethod
    def create_app():
        llm = ChatOpenAI(
            model='deepseek-v3.2',
            openai_api_key=os.getenv('API_KEY'),
            openai_api_base=os.getenv('API_BASE'),
            streaming=False,
        )
        return llm


def build_messages(friend, idle_minutes):
    """把角色设定 + 长期记忆 + 最近几条对话 + 本次敲门理由拼成一次调用。

    判断和生成合并成一次调用：多一次调用只会多一份延迟和成本，
    而"没话可说"和"不该开口"本来就是同一个判断。
    """
    system_prompts = SystemPrompt.objects.filter(title='回复').order_by('order_number')
    prompt = ''
    for sp in system_prompts:
        prompt += sp.prompt

    prompt += f'\n【角色性格】\n{friend.character.profile}\n'
    prompt += f'\n【长期记忆】\n{friend.memory}\n'
    prompt += f'\n【现在时间】\n{localtime(now()).strftime("%Y-%m-%d %H:%M:%S")}\n'
    if idle_minutes >= 60:
        prompt += f'\n【距上次说话】\n已经 {idle_minutes / 60:.1f} 小时没聊天了。\n'
    else:
        prompt += f'\n【距上次说话】\n已经 {idle_minutes} 分钟没聊天了。\n'

    recent = list(Message.objects.filter(friend=friend).order_by('-id')[:6])
    recent.reverse()
    history = ''
    for m in recent:
        history += f'用户：{m.user_message}\n你说：{m.output}\n'
    if history:
        prompt += f'\n【最近的对话】\n{history}\n'
    else:
        prompt += '\n【最近的对话】\n（你们还没聊过）\n'

    prompt += '\n【现在，你要决定】\n要不要主动找他说一句话？说就只回那句话，不说就只回 NO。'

    return [SystemMessage(PROACTIVE_PROMPT), HumanMessage(prompt)]
