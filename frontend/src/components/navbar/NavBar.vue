<script setup>

import MenuIcon from "@/components/navbar/icons/MenuIcon.vue";
import HomepageIcon from "@/components/navbar/icons/HomepageIcon.vue";
import FriendIcon from "@/components/navbar/icons/FriendIcon.vue";
import CreateIcon from "@/components/navbar/icons/CreateIcon.vue";
import SearchIcon from "@/components/navbar/icons/SearchIcon.vue";
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="drawer lg:drawer-open">
    <input id="my-drawer-4" type="checkbox" class="drawer-toggle" />
    <div class="drawer-content">
      <nav class="navbar w-full bg-base-100 shadow-sm">

        <!-- 左 -->
        <div class="navbar-start">
          <label for="my-drawer-4" aria-label="open sidebar" class="btn btn-square btn-ghost">
            <MenuIcon />
          </label>
          <div class="px-1 font-bold text-xl">AIFriends</div>
        </div>

        <!-- 中 -->
        <div class="navbar-center w-4/5 max-w-180 justify-center">
          <div class="join w-4/5 max-w-180">
            <input class="input join-item" placeholder="搜索你感兴趣的内容" />
            <button class="btn join-item rounded-r-full gap-0">
              <SearchIcon />搜索
            </button>
          </div>
        </div>

        <!-- 右 -->
        <div class="navbar-end">
          <RouterLink to="/login" class="btn btn-ghost">登录</RouterLink>
        </div>

      </nav>
      <slot></slot>
    </div>

    <div class="drawer-side is-drawer-close:overflow-visible">
      <label for="my-drawer-4" aria-label="close sidebar" class="drawer-overlay"></label>
      <div class="flex min-h-full flex-col items-start bg-base-200 is-drawer-close:w-16 is-drawer-open:w-64">
        <ul class="menu w-full grow">
          <li>
            <RouterLink to="/" class="sidebar-btn shrink-btn is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="首页">
            <HomepageIcon />
            <span class="is-drawer-close:hidden text-base ml-2">首页</span>
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/friend" class="sidebar-btn shrink-btn is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="好友">
            <FriendIcon />
            <span class="is-drawer-close:hidden text-base ml-2">好友</span>
            </RouterLink>
          </li>
          <li>
            <RouterLink to="/create" class="sidebar-btn shrink-btn is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="创作">
            <CreateIcon />
            <span class="is-drawer-close:hidden text-base ml-2">创作</span>
            </RouterLink>
          </li>

        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 保留你原有所有样式，仅新增对 RouterLink (a标签) 的兼容 */
:deep(li > button),
:deep(li > a) { /* 新增：兼容 RouterLink 渲染的 <a> 标签 */
  display: flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 8px;
  background: transparent;
  border: none;
  width: 100%;
  box-sizing: border-box;
}

/* hover/激活态：对 button 和 a 标签都生效 */
:deep(li > button:hover),
:deep(li > button.active),
:deep(li > a:hover),
:deep(li > a.router-link-active) { /* 新增：路由激活态高亮 */
  background: #eee;
}

/* 图标居中 + 文字间距（保留原有逻辑） */
:deep(li > button svg),
:deep(li > a svg) {
  display: block;
}
:deep(li > button span),
:deep(li > a span) {
  margin-left: 8px;
  white-space: nowrap;
}
</style>

