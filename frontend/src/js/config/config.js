const platform = 'django'   // vue、django、cloud

const CONFIG_API = {
    HTTP_URL: '',
    VAD_URL: '',
    WS_URL: '',   // 语音识别用的 WebSocket 地址
}

if (platform === 'vue') {
    CONFIG_API.HTTP_URL = 'http://127.0.0.1:8000'
    CONFIG_API.VAD_URL = 'http://localhost:5173/vad/'
    CONFIG_API.WS_URL = 'ws://127.0.0.1:8000/ws/asr/'
} else if (platform === 'django') {
    CONFIG_API.HTTP_URL = 'http://127.0.0.1:8000'
    CONFIG_API.VAD_URL = 'http://127.0.0.1:8000/static/frontend/vad/'
    CONFIG_API.WS_URL = 'ws://127.0.0.1:8000/ws/asr/'
} else if (platform === 'cloud') {
    CONFIG_API.HTTP_URL = 'https://app7703.acapp.acwing.com.cn'
    CONFIG_API.VAD_URL = 'https://app7703.acapp.acwing.com.cn/static/frontend/vad/'
    CONFIG_API.WS_URL = 'wss://app7703.acapp.acwing.com.cn/ws/asr/'
}

export default CONFIG_API
