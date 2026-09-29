<script setup>
import {computed, nextTick, ref, useTemplateRef, watch, onBeforeUnmount} from "vue";
import InputField from "@/components/character/chat_field/input_field/InputField.vue";
import CharacterPhotoField from "@/components/character/chat_field/character_photo_field/CharacterPhotoField.vue";
import ChatHistory from "@/components/character/chat_field/chat_history/ChatHistory.vue";
import CONFIG_API from "@/js/config/config.js";
import {useUserStore} from "@/stores/user.js";

const props = defineProps(['friend'])
const modalRef = useTemplateRef('modal-ref')
const inputRef = useTemplateRef('input-ref')
const chatHistoryRef = useTemplateRef('chat-history-ref')
const history = ref([])

// 主动消息：进聊天页时开一条 WebSocket，让后端有机会"隔一会儿敲一次门"。
// 页面一关这条连接就断，所以只有聊天窗口开着的时候才可能收到主动消息。
// 「一轮只说一次」由后端保证（看 Friend.proactive_done），前端不做任何限制。
const PROACTIVE_ENABLED = true

let proactiveWS = null

function connectProactive(friendId) {
  if (!PROACTIVE_ENABLED) return
  if (!friendId) return
  if (proactiveWS) return

  const token = useUserStore().accessToken
  proactiveWS = new WebSocket(`${CONFIG_API.PROACTIVE_WS_URL}?token=${token}&friend_id=${friendId}`)

  proactiveWS.onmessage = (event) => {
    const {text} = JSON.parse(event.data)
    if (!text) return
    handlePushBackMessage({
      role: 'ai',
      content: text,
      id: crypto.randomUUID(),
      time: new Date().toISOString(),
    })
  }

  proactiveWS.onclose = () => {
    proactiveWS = null
  }
}

function closeProactive() {
  if (proactiveWS) {
    proactiveWS.close()
    proactiveWS = null
  }
}

// friend 是异步加载的（点开角色才拿到），所以要看它什么时候才有值
watch(() => props.friend?.id, (id) => {
  if (id) connectProactive(id)
}, {immediate: true})

onBeforeUnmount(closeProactive)

async function showModal() {
  modalRef.value.showModal()

  await nextTick()
  inputRef.value.focus()
  connectProactive(props.friend?.id)
}

const modalStyle = computed(() => {
  if (props.friend) {
    return {
      backgroundImage: `url(${props.friend.character.background_image})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
    }
  } else {
    return {}
  }
})

function handlePushBackMessage(msg) {
  history.value.push(msg)
  chatHistoryRef.value.scrollToBottom()
}

function handleAddToLastMessage(delta) {
  history.value.at(-1).content += delta
  chatHistoryRef.value.scrollToBottom()
}

function handlePushFrontMessage(msg) {
  history.value.unshift(msg)
}

function handleClose() {
  inputRef.value.close()
  // ⚠️ 关掉聊天框必须断开这条连接：不断的话它会一直挂着，
  // 后端的"同一好友只允许一个哨兵"就永远不释放名额，换角色后别的连接只能干看着。
  closeProactive()
}

defineExpose({
  showModal,
})
</script>

<template>
  <dialog ref="modal-ref" class="modal" @close="handleClose">
    <div class="modal-box w-90 h-150" :style="modalStyle">
      <button @click="modalRef.close()" class="btn btn-sm btn-circle btn-ghost bg-transparent absolute right-1 top-1">✕</button>
      <ChatHistory
          ref="chat-history-ref"
          v-if="friend"
          :history="history"
          :friendId="friend.id"
          :character="friend.character"
          @pushFrontMessage="handlePushFrontMessage"
      />
      <InputField
          v-if="friend"
          ref="input-ref"
          :friendId="friend.id"
          @pushBackMessage="handlePushBackMessage"
          @addToLastMessage="handleAddToLastMessage"
      />
      <CharacterPhotoField v-if="friend" :character="friend.character" />
    </div>
  </dialog>
</template>

<style scoped>

</style>
