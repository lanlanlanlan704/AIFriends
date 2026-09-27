<script setup>
import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import {MicVAD} from "@ricky0123/vad-web";
import CONFIG_API from "@/js/config/config.js";
import {useUserStore} from "@/stores/user.js";

// 这个组件不再自己画界面，只负责"录音"这一件事：
//   - 父组件点麦克风图标时调用 start() / stop()
//   - 识别出来的文字通过 live / finish 事件交给父组件，由父组件写进输入框
const emit = defineEmits(['start', 'live', 'finish'])

const MAX_RECORD_MS = 60 * 1000      // 一轮录音最长 1 分钟
const CLOSE_TIMEOUT_MS = 10 * 1000   // 喊停后等服务器收尾，最多等这么久
const OPEN_TIMEOUT_MS = 5 * 1000     // 点开始后等连接就绪，最多等这么久

const asrText = ref('')        // 这一轮识别出来的文字
const recording = ref(false)   // 正在录音（点开始 → 点停止之间）
const connecting = ref(false)  // 点了开始，还在等连接 / 麦克风就绪
const finishing = ref(false)   // 已经喊停，在等服务器把最后一句吐完
const hint = ref('')           // 出错时的提示文字
const elapsedMs = ref(0)       // 这一轮已经录了多少毫秒（驱动底部进度条）

// 距离 60 秒上限还剩几秒
const remainingSec = computed(() => Math.ceil((MAX_RECORD_MS - elapsedMs.value) / 1000))

// 贴在输入框上方的小提示：只在"准备中 / 识别中 / 出错"这几个没法从画面看出来的阶段出现
const statusText = computed(() => {
  if (recording.value) return ''          // 录音中：输入框里有字、底下有进度条，够了
  if (connecting.value) return '准备麦克风…'
  if (finishing.value) return '识别中…'
  return hint.value
})

let vadInstance = null;
let ws = null;
let stopped = false;           // 组件是不是已经关掉了
let startAt = 0;               // 这一轮的起始时刻（时间戳）
let timerId = null;            // 计时器编号
let closeTimerId = null;       // 「识别中」兜底超时的编号
let committed = '';            // 这一轮里"已经说完的句子"，攒在这里
let micFailed = false;         // 麦克风是否初始化失败
let micReadyPromise = Promise.resolve()   // 麦克风就绪的等待句柄
const openWaiters = [];        // 排队等连接就绪的回调，连上后逐个兑现

// ---------- WebSocket ----------

const connectWS = () => {
  const token = useUserStore().accessToken
  ws = new WebSocket(`${CONFIG_API.WS_URL}?token=${token}`)

  ws.onopen = () => {
    console.log("[WS] 已连上后端")
    while (openWaiters.length) openWaiters.shift()()   // 通知所有在等连接的人
  }

  ws.onmessage = (event) => {
    const {text, final} = JSON.parse(event.data)

    // 阿里云是"按句"给结果的：同一句话里 text 会越滚越长，
    // 但开始说下一句时，text 会重新从空开始。
    // 所以不能整行覆盖 —— 要把"已经说完的句子"攒进 committed，拼在当前这句前面。
    if (final) {
      committed += text
      console.log("[WS] 这句说完了:", text)
    }
    // 这一轮（最多 60 秒）里说过的全部
    asrText.value = final ? committed : committed + text
    if (recording.value || finishing.value) emit('live', asrText.value)
  }

  ws.onerror = (e) => {
    console.error("[WS] 出错:", e)
  }

  ws.onclose = () => {
    // 服务器把最后一句吐完就主动断开了，这时候才真的把文字交出去
    if (finishing.value) finishRound()
    if (!stopped) connectWS()    // 断了就重连，保证下一句还能用
  }
}

// 等连接就绪；超时还没连上就返回 false（不然"后端没启动"时界面会一直卡在准备中）
const waitForOpen = (timeoutMs = OPEN_TIMEOUT_MS) => {
  if (ws && ws.readyState === WebSocket.OPEN) return Promise.resolve(true)

  return new Promise(resolve => {
    let done = false

    const t = setTimeout(() => {
      if (done) return
      done = true
      const i = openWaiters.indexOf(ok)
      if (i >= 0) openWaiters.splice(i, 1)   // 不再等了，把自己从队列里摘掉
      resolve(false)
    }, timeoutMs)

    const ok = () => {
      if (done) return
      done = true
      clearTimeout(t)
      resolve(true)
    }

    openWaiters.push(ok)
  })
}

// 连接还没准备好的时候，音频先丢掉，不报错
const wsSend = (data) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(data)
  }
}

// ---------- 一轮对话的收尾（全流程唯一的收尾出口）----------

const finishRound = () => {
  if (closeTimerId) {
    clearTimeout(closeTimerId)
    closeTimerId = null
  }
  finishing.value = false
  const result = asrText.value.trim()   // 这一轮说过的全部，不是只有最后一句
  asrText.value = ''
  committed = ''
  if (result) emit('finish', result)
}

// ---------- 60 秒上限的计时 ----------

const tick = () => {
  elapsedMs.value = Date.now() - startAt      // 用真实时间算，不能按次数累加
  if (elapsedMs.value >= MAX_RECORD_MS) stopRecording()
}

const startTimer = () => {
  stopTimer()
  startAt = Date.now()
  elapsedMs.value = 0
  timerId = setInterval(tick, 100)
}

const stopTimer = () => {
  if (timerId) {
    clearInterval(timerId)
    timerId = null
  }
}

// ---------- 开始 / 停止（由父组件调用）----------

const start = async () => {
  if (recording.value || connecting.value || finishing.value) return   // 挡住连点
  hint.value = ''
  emit('start')                     // 通知父组件：记下输入框原有内容，并打断正在播放的 AI 语音

  // 两件事同时等：WebSocket 连上 + 麦克风初始化完成。少等一个都会丢开头几个字。
  connecting.value = true
  const [connected] = await Promise.all([waitForOpen(), micReadyPromise])
  connecting.value = false

  if (stopped) return                            // 等待期间组件被关掉了
  if (micFailed) {
    hint.value = '麦克风打不开，检查一下浏览器权限'
    return
  }
  if (!connected) {
    hint.value = '连不上服务器，检查一下后端'
    return
  }

  committed = ''                                 // 新一轮，从头攒
  asrText.value = ''
  recording.value = true
  startTimer()
}

const stopRecording = () => {
  if (!recording.value) return                   // 手动点和自动到点撞上时，也只会执行一次
  stopTimer()
  recording.value = false
  finishing.value = true
  wsSend(JSON.stringify({action: 'finish'}))

  // 兜底：万一服务器不关连接，别让界面永远卡在「识别中…」
  closeTimerId = setTimeout(() => {
    if (finishing.value) {
      console.warn('[ASR] 等服务器收尾超时，强制收尾')
      finishRound()
    }
  }, CLOSE_TIMEOUT_MS)
}

// ---------- 麦克风 ----------

// 这里只用 VAD 库当"麦克风采集器"：它每帧都会回调，我们只取帧，不看它的判定结果
const setupMic = async () => {
  const baseUrl = CONFIG_API.VAD_URL
  try {
    vadInstance = await MicVAD.new({
      baseAssetPath: baseUrl,
      onFrameProcessed: (probs, frame) => {
        if (recording.value) wsSend(float32ToInt16(frame))
      },
      ortConfig: (ort) => {
        ort.env.wasm.wasmPaths = baseUrl;
        ort.env.logLevel = "error";
      },
      // 手动模式下这几个阈值已经不影响流程了，原样留着
      positiveSpeechThreshold: 0.8,
      negativeSpeechThreshold: 0.65,
      minSpeechFrames: 5,
      redemptionFrames: 5,
    });

    await vadInstance.start();
    micFailed = false
  } catch (e) {
    console.error("麦克风初始化失败:", e);
    micFailed = true
  }
};
// 将 Float32 转 PCM 16-bit
const float32ToInt16 = (float32Array) => {
  const buffer = new Int16Array(float32Array.length);
  for (let i = 0; i < float32Array.length; i++) {
    let s = Math.max(-1, Math.min(1, float32Array[i]));
    buffer[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  return buffer.buffer;
};

onMounted(() => {
  connectWS()
  micReadyPromise = setupMic()   // 记下句柄，start() 要等它
})

onBeforeUnmount(() => {
  stopped = true          // 必须先置，否则下面 close() 会触发无限重连
  stopTimer()
  if (closeTimerId) {
    clearTimeout(closeTimerId)
    closeTimerId = null
  }
  openWaiters.length = 0
  if (ws) {
    ws.close()
    ws = null
  }
  if (vadInstance) {
    vadInstance.destroy()
    vadInstance = null
  }
})

defineExpose({recording, connecting, finishing, start, stop: stopRecording})
</script>

<template>
  <!-- 小提示：贴在输入框上方一点，只在准备 / 识别中 / 出错时出现 -->
  <div
      v-if="statusText"
      class="absolute left-2 z-10 px-2 py-0.5 rounded-full bg-black/60 backdrop-blur-sm text-white/70 text-xs"
      :style="{ bottom: '4.25rem' }"
  >
    {{ statusText }}
  </div>

  <!-- 60 秒倒计时进度条：跟输入框同位置同尺寸，贴在它底边，不挡任何东西 -->
  <div
      v-if="recording"
      class="absolute bottom-4 left-2 z-10 h-12 w-86 rounded-2xl overflow-hidden pointer-events-none"
  >
    <div
        class="absolute bottom-0 left-0 h-0.5"
        :class="remainingSec <= 10 ? 'bg-orange-400' : 'bg-blue-400'"
        :style="{ width: `${Math.max(0, 100 - elapsedMs / MAX_RECORD_MS * 100)}%` }"
    ></div>
  </div>
</template>

<style scoped>
</style>
