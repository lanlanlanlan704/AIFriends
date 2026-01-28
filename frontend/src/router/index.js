import { createRouter, createWebHistory } from 'vue-router'
// 1. 导入所有页面组件（路径要和你的文件结构对应）
import HomepageIndex from '../views/homepage/HomepageIndex.vue'
import FriendIndex from '../views/friend/FriendIndex.vue'
import CreateIndex from '../views/create/CreateIndex.vue'
import ProfileIndex from '../views/user/profile/ProfileIndex.vue'
import LoginIndex from '../views/user/account/LoginIndex.vue'
import RegisterIndex from '../views/user/account/RegisterIndex.vue'
import SpaceIndex from '../views/user/space/SpaceIndex.vue'
import NotFoundIndex from '../views/error/NotFoundIndex.vue'
import {useUserStore} from "@/stores/user.js";


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: HomepageIndex,
      name: 'Home',
      meta: {
        needLogin: false,
      }
    },
    {
      path: '/friend/',
      component: FriendIndex,
      name: 'Friend',
      meta: {
        needLogin: true,
      }
    },
    {
      path: '/create/',
      component: CreateIndex,
      name: 'Create',
      meta: {
        needLogin: true,
      }
    },
    {
      path: '/profile/',
      component: ProfileIndex,
      name: 'Profile',
      meta: {
        needLogin: true,
      }
    },
    { path: '/login/', component: LoginIndex, name: 'Login' },
    { path: '/register/', component: RegisterIndex, name: 'Register' },
    {
      path: '/space/:user_id/',
      component: SpaceIndex,
      name: 'Space',
      meta: {
        needLogin: true,
      }
    },
    { path: '/404/', component: NotFoundIndex, name: '404' },
    { path: '/:pathMatch(.*)*/', component: NotFoundIndex, name: 'Notfound' },
  ],
})

router.beforeEach((to, from) => {
  const user = useUserStore()
  if (to.meta.needLogin && user.hasPulledUserInfo && !user.isLogin()) {
    return {
      name: 'Login',
    }
  }
  return true
})
export default router
