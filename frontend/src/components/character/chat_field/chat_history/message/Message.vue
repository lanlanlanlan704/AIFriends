<script setup>
import {computed} from "vue";
import {useUserStore} from "@/stores/user.js";

const props = defineProps(['message', 'character', 'prevMessage'])

const user = useUserStore()

const WEEK = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']

// 把时间补零成两位数：9 → "09"
function pad(n) {
  return String(n).padStart(2, '0')
}

// 取某天的"零点"，只用来做日期比较（不改动传进来的那个 Date）
function startOfDay(date) {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  return d
}

// 两个时间是不是同一天
function isSameDay(a, b) {
  return a.getFullYear() === b.getFullYear()
      && a.getMonth() === b.getMonth()
      && a.getDate() === b.getDate()
}

// 取某个时间所在"自然周"的编号：同一个月里同一周 ⇒ 算出来相同；跨周 ⇒ 不同。
// 做法：先归零到那天零点，再把日期往前推它自己的星期几，得到"这一周的周日"。
// 两周的周日如果落在同一天，说明是同一周。
// ⚠️ 不要用"相差天数 ≤ 6"来判断"本周"：
//    今天是周一时，上周二只差 6 天，会被误判成"本周二"（其实隔了一周）。
function weekStartOf(date) {
  const d = startOfDay(date)
  d.setDate(d.getDate() - d.getDay())   // getDay(): 周日=0、周一=1 …… 减掉它 = 回到本周的周日
  return d
}

// 把 ISO 时间字符串格式化成微信那种样式
// 今天 → 14:32 ／ 昨天 → 昨天 14:32 ／ 前天 → 前天 14:32
// 本周内 → 星期三 14:32 ／ 更早 → 2026年9月21日 14:32
function formatTime(iso) {
  if (!iso) return ''

  const date = new Date(iso)
  if (isNaN(date.getTime())) return ''       // 时间字符串坏了就什么都不显示

  const now = new Date()
  const hm = `${pad(date.getHours())}:${pad(date.getMinutes())}`

  // 今天：只显示时间
  if (isSameDay(date, now)) return hm

  // 昨天：用"日期减一天"算，不能减 24 小时（跨月/跨年才不出错）
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (isSameDay(date, yesterday)) return `昨天 ${hm}`

  // 前天：比"星期几"更明确，先判掉
  const dayBeforeYesterday = new Date(now)
  dayBeforeYesterday.setDate(dayBeforeYesterday.getDate() - 2)
  if (isSameDay(date, dayBeforeYesterday)) return `前天 ${hm}`

  // 本周内（按自然周判断）：显示星期几
  if (weekStartOf(date).getTime() === weekStartOf(now).getTime()) {
    return `${WEEK[date.getDay()]} ${hm}`
  }

  // 更早：显示完整日期
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日 ${hm}`
}

// 要不要在这条消息上显示时间？
// 规则：同一个人连续说多条（同一分钟内），只在第一条上显示。
//   ⇒ 你和 AI 交替说话时，两条都会显示（因为角色不同）
//   ⇒ AI 一次回复被拆成多条时，只显示第一条（因为是同一个角色）
const timeText = computed(() => {
  const cur = props.message.time
  if (!cur) return ''

  const prevMsg = props.prevMessage
  if (prevMsg?.time && prevMsg.role === props.message.role) {
    const a = new Date(cur).getTime()
    const b = new Date(prevMsg.time).getTime()
    // 同一个"分钟"里就不重复显示（60000 毫秒 = 1 分钟）
    if (!isNaN(a) && !isNaN(b) && Math.floor(a / 60000) === Math.floor(b / 60000)) return ''
  }

  return formatTime(cur)
})
</script>

<template>
  <div v-if="message.content">
    <div v-if="message.role === 'ai'" class="chat chat-start">
      <div class="chat-image avatar">
        <div class="w-10 rounded-full">
          <img :src="character.photo" alt="">
        </div>
      </div>
      <div class="chat-bubble whitespace-pre-wrap break-all">{{ message.content }}</div>
      <div v-if="timeText" class="chat-footer text-xs text-white/70 mt-1">{{ timeText }}</div>
    </div>
    <div v-else class="chat chat-end">
      <div class="chat-image avatar">
        <div class="w-10 rounded-full">
          <img :src="user.photo" alt="">>
        </div>
      </div>
      <div class="chat-bubble chat-bubble-success whitespace-pre-wrap break-all">{{ message.content }}</div>
      <div v-if="timeText" class="chat-footer text-xs text-white/70 mt-1">{{ timeText }}</div>
    </div>
  </div>
</template>

<style scoped>

</style>
