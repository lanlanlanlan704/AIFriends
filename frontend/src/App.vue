<script setup>

import NavBar from "@/components/navbar/NavBar.vue";
</script>

<template>
  <NavBar>
    页面内容
  </NavBar>
  <svg width="32" height="32" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <!-- 话筒头 -->
    <rect x="22" y="6" width="20" height="28" rx="10" fill="black"/>

    <!-- 话筒柄 -->
    <rect x="30" y="34" width="4" height="14" rx="2" fill="black"/>

    <!-- U 型支架 -->
    <path d="M18 30v4c0 8 6.5 14 14 14s14-6 14-14v-4"
          fill="none"
          stroke="black"
          stroke-width="4"
          stroke-linecap="round"/>

    <!-- 底座 -->
    <rect x="22" y="52" width="20" height="4" rx="2" fill="black"/>
</svg>




</template>

<style scoped>
</style>
