<script setup>

</script>

<template>
  <div class="flex justify-center mt-30">
    <fieldset class="fieldset bg-base-200 border-base-300 rounded-box w-xs border p-4">
      <legend class="fieldset-legend"></legend>

      <label class="label">用户名</label>
      <input type="email" class="input" placeholder="用户名" />

      <label class="label">密码</label>
      <input type="password" class="input" placeholder="密码" />

      <button class="btn btn-neutral mt-4">登录</button>
      <div class="flex justify-end">
        <RouterLink to="/register" class="btn btn-sm btn-ghost tex-gray-500">注册</RouterLink>
      </div>
    </fieldset>
  </div>
</template>

<style scoped>

</style>