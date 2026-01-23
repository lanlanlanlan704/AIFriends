<script setup>

import MenuIcon from "@/components/navbar/icons/MenuIcon.vue";
import HomepageIcon from "@/components/navbar/icons/HomepageIcon.vue";
import FriendIcon from "@/components/navbar/icons/FriendIcon.vue";
import CreateIcon from "@/components/navbar/icons/CreateIcon.vue";
import SearchIcon from "@/components/navbar/icons/SearchIcon.vue";
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
        <div class="navbar-center w-4/5 max-w-180">
          <div class="join w-4/5 max-w-180">
            <input class="input join-item" placeholder="搜索你感兴趣的内容" />
            <button class="btn join-item rounded-r-full gap-0">
              <SearchIcon />搜索
            </button>
          </div>
        </div>

        <!-- 右 -->
        <div class="navbar-end">
          <button class="btn btn-ghost">登录</button>
        </div>

      </nav>
      <slot></slot>
    </div>

    <div class="drawer-side is-drawer-close:overflow-visible">
      <label for="my-drawer-4" aria-label="close sidebar" class="drawer-overlay"></label>
      <div class="flex min-h-full flex-col items-start bg-base-200 is-drawer-close:w-16 is-drawer-open:w-64">
        <ul class="menu w-full grow">
          <li>
            <button class="sidebar-btn shrink-btn is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="首页">
            <HomepageIcon />
            <span class="is-drawer-close:hidden text-base ml-2">首页</span>
            </button>
          </li>
          <li>
            <button class="sidebar-btn shrink-btn is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="好友">
            <FriendIcon />
            <span class="is-drawer-close:hidden text-base ml-2">好友</span>
            </button>
          </li>
          <li>
            <button class="sidebar-btn shrink-btn is-drawer-close:tooltip is-drawer-close:tooltip-right py-3" data-tip="创作">
            <CreateIcon />
            <span class="is-drawer-close:hidden text-base ml-2">创作</span>
            </button>
          </li>

        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 只修 hover 框范围 + SVG 居中，不碰宽高布局 */

:deep(li > button) {
  display: flex;
  align-items: center;

  padding: 6px 10px;      /* 给内容一点内边距 */
  border-radius: 8px;

  background: transparent;
  border: none;

  width: 100%;            /* 保持你原来“整行”逻辑 */
  box-sizing: border-box;
}

/* hover / active：整行高亮，不出边栏 */
:deep(li > button:hover),
:deep(li > button.active) {
  background: #eee;
}

/* SVG 真正居中（不再 baseline 飘） */
:deep(li > button svg) {
  display: block;
}

/* 图标和文字间距 */
:deep(li > button span) {
  margin-left: 8px;
  white-space: nowrap;
}
</style>

