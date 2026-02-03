<script setup>
import {ref} from "vue";
import {useUserStore} from "@/stores/user.js";
import {useRouter} from "vue-router";
import api from "@/js/http/api.js";

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const user = useUserStore()
const router = useRouter()
async function handleLogin() {
  errorMessage.value = ''
  if (!username.value.trim()) {
    errorMessage.value = '用户名不能为空'
  } else if (!password.value.trim()) {
    errorMessage.value = '密码不能为空'
  } else {
    try {
      const res = await api.post('/api/user/account/login/',{
          username: username.value,
          password: password.value,
      })
      const data = res.data
      if (data.result === 'success'){
        user.setAccessToken(data.access)
        user.setUserInfo(data)
        await router.push({    // 加上await是优化用户体验，保证加载完信息之后再进行路由跳转，避免用户在登陆后刷新页面时依然看见登录键
          name: 'Home'
        })
      } else{
        errorMessage.value=data.result
      }
    }
    catch (err) {
      console.log(err)
    }
  }
}

</script>

<template>
  <div class="flex justify-center mt-30">
    <form @submit.prevent="handleLogin" class="fieldset bg-base-200 border-base-300 rounded-box w-xs border p-4">
      <legend class="fieldset-legend"></legend>

      <label class="label">用户名</label>
      <input v-model="username" type="text" class="input" placeholder="用户名" />

      <label class="label">密码</label>
      <input v-model="password" type="password" class="input" placeholder="密码" />

      <p v-if="errorMessage" class="text-red-500 text-sm mt-1">{{errorMessage}}</p>

      <button class="btn btn-neutral mt-4">登录</button>
      <div class="flex justify-end">
        <RouterLink to="/register" class="btn btn-sm btn-ghost tex-gray-500">注册</RouterLink>
      </div>
    </form>
  </div>
</template>

<style scoped>

</style>