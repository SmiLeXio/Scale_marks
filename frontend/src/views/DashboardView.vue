<script setup>
import { onMounted, ref } from 'vue'
import { CalendarCheck2, Utensils } from 'lucide-vue-next'
import EmptyState from '../components/EmptyState.vue'
import PageHeader from '../components/PageHeader.vue'
import PetCard from '../components/PetCard.vue'
import { remindersApi } from '../api/reminders'
import { usePetsStore } from '../stores/pets'
import { formatDateTime } from '../utils/date'

const petsStore = usePetsStore()
const reminders = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    await petsStore.fetchPets()
    const { data } = await remindersApi.today()
    reminders.value = data
  } finally {
    loading.value = false
  }
}

async function completeReminder(id) {
  await remindersApi.complete(id)
  reminders.value = reminders.value.filter((reminder) => reminder.id !== id)
}

onMounted(load)
</script>

<template>
  <section class="px-4 py-6 sm:px-6 lg:px-8">
    <PageHeader
      eyebrow="Dashboard"
      title="我的爬宠"
      description="打开应用后优先查看宠物卡片，头像、品种和核心养护数据一屏可见。"
    />

    <EmptyState
      v-if="!petsStore.pets.length && !loading"
      title="还没有宠物档案"
      description="总览页只负责查看。请到档案页使用右下角加号创建档案。"
    />

    <div v-else class="grid gap-4 xl:grid-cols-2">
      <PetCard v-for="pet in petsStore.pets" :key="pet.id" :pet="pet" readonly />
    </div>

    <div class="mt-8 grid gap-6 xl:grid-cols-[1fr_360px]">
      <section class="panel rounded-lg p-5">
        <div class="mb-4 flex items-center justify-between gap-3">
          <div>
            <p class="label text-clay">Today</p>
            <h2 class="mt-1 text-xl font-black">今日待办</h2>
          </div>
          <CalendarCheck2 class="h-5 w-5 text-clay" />
        </div>

        <div v-if="reminders.length" class="grid gap-3 md:grid-cols-2">
          <article v-for="reminder in reminders" :key="reminder.id" class="rounded-md border border-ink/10 bg-shell p-4">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-black">{{ reminder.title }}</p>
                <p class="mt-1 text-sm text-ink/60">{{ reminder.pet_name }} · {{ formatDateTime(reminder.due_date) }}</p>
              </div>
              <button class="btn-secondary min-h-9 px-3 py-1" @click="completeReminder(reminder.id)">完成</button>
            </div>
          </article>
        </div>
        <p v-else class="rounded-md bg-shell p-4 text-sm text-ink/60">今天没有待办。</p>
      </section>

      <section class="panel rounded-lg p-5">
        <div class="flex items-center justify-between">
          <div>
            <p class="label text-clay">Care Queue</p>
            <h2 class="mt-1 text-xl font-black">快速状态</h2>
          </div>
          <Utensils class="h-5 w-5 text-water" />
        </div>
        <div class="mt-5 grid grid-cols-2 gap-3">
          <div class="rounded-md bg-shell p-4">
            <p class="label">档案数量</p>
            <p class="mt-2 text-3xl font-black">{{ petsStore.pets.length }}</p>
          </div>
          <div class="rounded-md bg-shell p-4">
            <p class="label">今日任务</p>
            <p class="mt-2 text-3xl font-black">{{ reminders.length }}</p>
          </div>
        </div>
      </section>
    </div>
  </section>
</template>
