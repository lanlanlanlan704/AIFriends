import {defineStore} from "pinia";
import {ref} from "vue";

export const useUserStore = defineStore("user", () => {
    const id = ref(0)
    const username = ref('')
    const photo = ref('')
    const profile = ref('')
    const accessToken = ref('')
    const hasPulledUserInfo = ref(false)
    function isLogin(){
        return !!accessToken.value   // 必须带value!!!!!
    }
    function setAccessToken(token) {
        accessToken.value = token
    }
    function setUserInfo(data)     //不规定形参类型，传进来什么类型参数就是什么类型
    {
        id.value = data.user_id
        username.value = data.username
        photo.value = data.photo
        profile.value = data.profile
    }
    function logout(){
        id.value = 0
        username.value = ''
        photo.value = ''
        accessToken.value = ''
        profile.value = ''
    }

    function setHasPulledUserInfo(newStatus){
        hasPulledUserInfo.value = newStatus
    }


    return {
        id,
        username,
        photo,
        profile,
        accessToken, //千万不要忘了！！！！！
        isLogin,
        setAccessToken,
        setUserInfo,
        logout,
        hasPulledUserInfo,
        setHasPulledUserInfo,
    }
})
