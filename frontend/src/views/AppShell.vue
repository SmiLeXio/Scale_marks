<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  BarChart3,
  CalendarDays,
  Home,
  LogOut,
  NotebookTabs,
  Scale,
  Utensils
} from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import { usePetsStore } from '../stores/pets'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const petsStore = usePetsStore()

const navItems = [
  { path: '/', label: '总览', icon: Home },
  { path: '/pets', label: '档案', icon: NotebookTabs },
  { path: '/growth', label: '成长', icon: BarChart3 },
  { path: '/feeding', label: '喂食', icon: Utensils },
  { path: '/calendar', label: '日历', icon: CalendarDays }
]

const activePetCount = computed(() => petsStore.pets.length)

onMounted(() => {
  petsStore.fetchPets()
})

function logout() {
  auth.logout()
  router.push('/auth')
}
</script>

<template>
  <div class="min-h-screen pb-20 lg:pb-0">
    <aside class="fixed left-0 top-0 hidden h-screen w-64 border-r border-ink/10 bg-bone/90 p-5 backdrop-blur lg:block">
      <div class="flex items-center gap-3">
        <div class="grid h-11 w-11 place-items-center rounded-md bg-ink text-bone">
          <Scale class="h-5 w-5" />
        </div>
        <div>
          <p class="text-lg font-black">鳞迹</p>
          <p class="text-xs text-ink/55">Reptile Journal</p>
        </div>
      </div>

      <nav class="mt-8 space-y-2">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex min-h-11 items-center gap-3 rounded-md px-3 text-sm font-semibold transition"
          :class="route.path === item.path || (item.path !== '/' && route.path.startsWith(item.path)) ? 'bg-ink text-bone' : 'text-ink/65 hover:bg-shell hover:text-ink'"
        >
          <component :is="item.icon" class="h-4 w-4" />
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="absolute bottom-5 left-5 right-5">
        <div class="mb-3 border border-ink/10 bg-shell p-3">
          <p class="text-xs text-ink/55">当前用户</p>
          <p class="truncate text-sm font-bold">{{ auth.user?.nickname }}</p>
          <p class="mt-1 text-xs text-ink/55">{{ activePetCount }} 只宠物档案</p>
        </div>
        <button class="btn-secondary w-full" @click="logout">
          <LogOut class="h-4 w-4" />
          退出
        </button>
      </div>
    </aside>

    <header class="sticky top-0 z-20 border-b border-ink/10 bg-bone/90 px-4 py-3 backdrop-blur lg:hidden">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Scale class="h-5 w-5" />
          <span class="font-black">鳞迹</span>
        </div>
        <button class="rounded-md p-2 text-ink/70" aria-label="退出" @click="logout">
          <LogOut class="h-5 w-5" />
        </button>
      </div>
    </header>

    <main class="lg:ml-64">
      <RouterView />
    </main>

    <nav class="fixed bottom-0 left-0 right-0 z-30 grid grid-cols-5 border-t border-ink/10 bg-bone/95 lg:hidden">
      <RouterLink
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="flex h-16 flex-col items-center justify-center gap-1 text-xs font-semibold"
        :class="route.path === item.path || (item.path !== '/' && route.path.startsWith(item.path)) ? 'text-clay' : 'text-ink/55'"
      >
        <component :is="item.icon" class="h-5 w-5" />
        {{ item.label }}
      </RouterLink>
    </nav>
  </div>
</template>
