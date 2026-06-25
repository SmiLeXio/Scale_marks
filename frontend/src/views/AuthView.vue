<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { LockKeyhole, LogIn, Mail, UserRound } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const mode = ref('login')
const error = ref('')
const form = ref({
  email: '',
  password: '',
  nickname: ''
})

const isRegister = computed(() => mode.value === 'register')

async function submit() {
  error.value = ''
  try {
    if (isRegister.value) {
      await auth.register(form.value)
    } else {
      await auth.login({ email: form.value.email, password: form.value.password })
    }
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || '请求失败，请检查输入后重试'
  }
}
</script>

<template>
  <main class="min-h-screen px-4 py-6 sm:px-6 lg:px-10">
    <section class="mx-auto grid min-h-[calc(100vh-3rem)] max-w-6xl items-center gap-8 lg:grid-cols-[1.05fr_0.95fr]">
      <div class="order-2 lg:order-1">
        <p class="mb-4 text-sm font-semibold uppercase tracking-normal text-clay">鳞迹</p>
        <h1 class="max-w-xl text-4xl font-black leading-tight text-ink sm:text-6xl">
          鳞迹，把每一次成长、喂食和蜕变都记录下来。
        </h1>
        <div class="mt-8 grid gap-3 sm:grid-cols-3">
          <div class="border-l-4 border-water bg-bone/80 p-4">
            <p class="text-3xl font-black">P0</p>
            <p class="mt-1 text-sm text-ink/65">个体档案与成长记录</p>
          </div>
          <div class="border-l-4 border-clay bg-bone/80 p-4">
            <p class="text-3xl font-black">7d</p>
            <p class="mt-1 text-sm text-ink/65">自动推算喂食周期</p>
          </div>
          <div class="border-l-4 border-fern bg-bone/80 p-4">
            <p class="text-3xl font-black">CSV</p>
            <p class="mt-1 text-sm text-ink/65">后续可扩展导出</p>
          </div>
        </div>
      </div>

      <form class="panel order-1 rounded-lg p-5 sm:p-7 lg:order-2" @submit.prevent="submit">
        <div class="mb-6 flex items-center justify-between gap-4">
          <div>
            <p class="label">账号</p>
            <h2 class="mt-1 text-2xl font-black">{{ isRegister ? '创建档案库' : '登录档案库' }}</h2>
          </div>
          <div class="flex rounded-md border border-ink/10 bg-shell p-1">
            <button
              type="button"
              class="rounded px-3 py-2 text-sm font-semibold"
              :class="mode === 'login' ? 'bg-ink text-bone' : 'text-ink/60'"
              @click="mode = 'login'"
            >
              登录
            </button>
            <button
              type="button"
              class="rounded px-3 py-2 text-sm font-semibold"
              :class="mode === 'register' ? 'bg-ink text-bone' : 'text-ink/60'"
              @click="mode = 'register'"
            >
              注册
            </button>
          </div>
        </div>

        <div class="space-y-4">
          <label v-if="isRegister" class="block">
            <span class="label">昵称</span>
            <span class="mt-1 flex items-center gap-2">
              <UserRound class="h-4 w-4 text-ink/50" />
              <input v-model="form.nickname" class="field" required placeholder="例如：阿麟" />
            </span>
          </label>
          <label class="block">
            <span class="label">邮箱</span>
            <span class="mt-1 flex items-center gap-2">
              <Mail class="h-4 w-4 text-ink/50" />
              <input v-model="form.email" class="field" type="email" required placeholder="you@example.com" />
            </span>
          </label>
          <label class="block">
            <span class="label">密码</span>
            <span class="mt-1 flex items-center gap-2">
              <LockKeyhole class="h-4 w-4 text-ink/50" />
              <input v-model="form.password" class="field" type="password" required minlength="8" placeholder="至少 8 位" />
            </span>
          </label>
        </div>

        <p v-if="error" class="mt-4 rounded-md bg-clay/10 px-3 py-2 text-sm font-semibold text-clay">{{ error }}</p>

        <button class="btn-primary mt-6 w-full" :disabled="auth.loading">
          <LogIn class="h-4 w-4" />
          {{ auth.loading ? '处理中' : isRegister ? '注册并进入' : '登录' }}
        </button>
      </form>
    </section>
  </main>
</template>
