<script setup>
import {useUserStore} from "@/stores/user.js";
import UserSpaceIndex from "@/components/navbar/icons/UserSpaceIndex.vue";
import UserProfileIcon from "@/components/navbar/icons/UserProfileIcon.vue";
import UserLogoutIcon from "@/components/navbar/icons/UserLogoutIcon.vue";
import api from "@/js/http/api.js";
import {useRouter} from "vue-router";
const user = useUserStore()
const router = useRouter()

//点击菜单后菜单自动消失
function closeMenu() {
  const element = document.activeElement
  if (element && element instanceof HTMLElement) element.blur()
}

async function handleLogout() {
  try{
    const res = await api.post('/api/user/account/logout/')
    if (res.data.result === 'success'){
      user.logout()
      await router.push({
        name: 'Home'
      })
    }
  } catch(err) {
    console.log(err)
  }
}

</script>

<template>
  <div class="dropdown dropdown-end">
    <div tabindex="0" role="button" class="avatar btn btn-circle w-8 h-8 mr-6">
      <div class="w-8 rounded-full">
        <img :src="user.photo" alt="">
      </div>
    </div>
    <ul tabindex="-1" class="dropdown-content menu bg-base-100 rounded-box z-1 w-50 p-2 shadow-lg">
      <li>
        <RouterLink @click="closeMenu" :to="{name: 'Space', params:{user_id:user.id}}" active-class="btn-active" class="flex items-center">
          <div class="avatar">
            <div class="w-10 rounded-full">
              <img :src="user.photo" alt="">
            </div>
          </div>
          <div class="overflow-hidden" style="max-width: 120px;">
            <span class="text-base font-bold truncate block">
              {{user.username}}
            </span>
          </div>
        </RouterLink>
      </li>
      <li>
        <RouterLink @click="closeMenu" :to="{name: 'Space', params:{user_id:user.id}}" active-class="btn-active" class="font-bold py-5">
          <UserSpaceIndex class="mr-3" />个人空间
        </RouterLink>
      </li>
      <li>
        <RouterLink @click="closeMenu" :to="{name: 'Profile'}" active-class="btn-active" class="font-bold py-5">
          <UserProfileIcon class="mr-3" />编辑资料
        </RouterLink>
      </li>
      <li></li>
      <li>
        <a @click="handleLogout" class="font-bold py-5">
          <UserLogoutIcon class="mr-3" />退出登录
        </a>
      </li>
    </ul>
  </div>

</template>

<style scoped>

</style>