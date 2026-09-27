<script setup>
import SendIcon from "@/components/character/icons/SendIcon.vue";
import MicIcon from "@/components/character/icons/MicIcon.vue";
import {computed, nextTick, onUnmounted, ref, useTemplateRef} from "vue";
import streamApi from "@/js/http/streamApi.js";
import Microphone from "@/components/character/chat_field/input_field/Microphone.vue";

const props = defineProps(['friendId'])
const emit = defineEmits(['pushBackMessage', 'addToLastMessage'])
const inputRef = useTemplateRef('input-ref')
const micRef = useTemplateRef('mic-ref')
const message = ref('')
let processId = 0

// 麦克风组件第一次点击才挂载（那时候才会向浏览器申请麦克风权限），之后一直留着
const micMounted = ref(false)
const micRecording = computed(() => micRef.value?.recording ?? false)
const micBusy = computed(() => !!(micRef.value?.connecting || micRef.value?.finishing))
let micPrefix = ''            // 录音开始前输入框里已有的文字，识别结果接在它后面

let mediaSource = null;
let sourceBuffer = null;
let audioPlayer = new Audio(); // 全局播放器实例
let audioQueue = [];           // 待写入 Buffer 的二进制队列
let isUpdating = false;        // Buffer 是否正在写入

const initAudioStream = () => {
    audioPlayer.pause();
    audioQueue = [];
    isUpdating = false;

    mediaSource = new MediaSource();
    audioPlayer.src = URL.createObjectURL(mediaSource);

    mediaSource.addEventListener('sourceopen', () => {
        try {
            sourceBuffer = mediaSource.addSourceBuffer('audio/mpeg');
            sourceBuffer.addEventListener('updateend', () => {
                isUpdating = false;
                processQueue();
            });
        } catch (e) {
            console.error("MSE AddSourceBuffer Error:", e);
        }
    });

    audioPlayer.play().catch(e => console.error("等待用户交互以播放音频"));
};

const processQueue = () => {
    if (isUpdating || audioQueue.length === 0 || !sourceBuffer || sourceBuffer.updating) {
        return;
    }

    isUpdating = true;
    const chunk = audioQueue.shift();
    try {
        sourceBuffer.appendBuffer(chunk);
    } catch (e) {
        console.error("SourceBuffer Append Error:", e);
        isUpdating = false;
    }
};

const stopAudio = () => {
    audioPlayer.pause();
    audioQueue = [];
    isUpdating = false;

    if (mediaSource) {
        if (mediaSource.readyState === 'open') {
            try {
                mediaSource.endOfStream();
            } catch (e) {
            }
        }
        mediaSource = null;
    }

    if (audioPlayer.src) {
        URL.revokeObjectURL(audioPlayer.src);
        audioPlayer.src = '';
    }
};

const handleAudioChunk = (base64Data) => {  // 将语音片段添加到播放器队列中
    try {
        const binaryString = atob(base64Data);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        audioQueue.push(bytes);
        processQueue();
    } catch (e) {
        console.error("Base64 Decode Error:", e);
    }
};

onUnmounted(() => {
    audioPlayer.pause();
    audioPlayer.src = '';
});

function focus() {
  inputRef.value.focus()
}

async function handleSend(event, audio_msg) {
  let content
  if (audio_msg) {
    content = audio_msg.trim()
  } else {
    content = message.value.trim()
  }
  if (!content) return

  initAudioStream()

  const curId = ++processId
  message.value = ''

  // 这一对消息是"此刻"发出的，用当前时间。
  // ⚠️ 这是浏览器的时间，只用于"立刻显示"；页面重新加载后会换成后端存的真实时间。
  // 用 new Date().toISOString() 生成 UTC 的 ISO 字符串，和 Message.vue 的解析方式保持一致。
  const sendTime = new Date().toISOString()

  emit('pushBackMessage', {role: 'user', content: content, id: crypto.randomUUID(), time: sendTime})
  emit('pushBackMessage', {role: 'ai', content: '', id: crypto.randomUUID(), time: sendTime})

  try {
    await streamApi('/api/friend/message/chat/', {
      body: {
        friend_id: props.friendId,
        message: content,
      },
      onmessage(data, isDone) {
        if (curId !== processId) return

        if (data.content) {
          emit('addToLastMessage', data.content)
        }
        if (data.audio) {
          handleAudioChunk(data.audio)
        }
      },
      onerror(err) {
      },
    })
  } catch (err) {
  }
}

function close() {
  ++processId
  stopAudio()
  if (micRecording.value || micBusy.value) micRef.value?.stop()
}

function handleStop() {
  ++processId
  stopAudio()
}

// ---------- 语音输入：点麦克风图标开始，再点一下停止 ----------

// 把"录音前已有的文字"和"这一轮识别出的文字"拼起来
function mergeMicText(text) {
  return [micPrefix, text].filter(Boolean).join(' ')
}

async function toggleMic() {
  if (micBusy.value) return              // 准备中 / 收尾中，点了不算

  if (!micMounted.value) {
    micMounted.value = true
    await nextTick()                     // 等组件挂载完，micRef 才有值
  }

  if (micRecording.value) micRef.value?.stop()
  else micRef.value?.start()
}

function handleMicStart() {
  micPrefix = message.value.trim()       // 记下原有内容
  handleStop()                           // 打断正在播放的 AI 语音
}

function handleMicLive(text) {
  message.value = mergeMicText(text)     // 边识别边往输入框里填
}

function handleMicFinish(text) {
  message.value = mergeMicText(text)
  micPrefix = ''
  focus()                                // 光标落到输入框，方便直接改
}

defineExpose({
  focus,
  close,
})
</script>

<template>
  <form @submit.prevent="handleSend" class="absolute bottom-4 left-2 h-12 w-86 flex items-center">
    <input
        ref="input-ref"
        v-model="message"
        class="input bg-black/30 backdrop-blur-sm text-white text-base w-full h-full rounded-2xl pr-20"
        type="text"
        placeholder="文本输入..."
    >
    <div @click="handleSend" class="absolute right-2 w-8 h-8 flex justify-center items-center cursor-pointer">
      <SendIcon/>
    </div>

    <!-- 麦克风：点一下开始说话，再点一下结束；录音中变红、图标变停止方块 -->
    <div
        @click="toggleMic"
        class="absolute right-10 w-8 h-8 flex justify-center items-center rounded-full cursor-pointer transition-colors"
        :class="micRecording ? 'bg-red-500 hover:bg-red-400' : 'hover:bg-white/15'"
    >
      <div v-if="micRecording" class="w-2.5 h-2.5 bg-white rounded-sm"></div>
      <span v-else-if="micBusy" class="loading loading-spinner loading-xs text-white"></span>
      <MicIcon v-else/>
    </div>
  </form>

  <!-- 录音组件：只管录音和画倒计时条，界面交给上面的输入框 -->
  <Microphone
      v-if="micMounted"
      ref="mic-ref"
      @start="handleMicStart"
      @live="handleMicLive"
      @finish="handleMicFinish"
  />
</template>

<style scoped>

</style>
