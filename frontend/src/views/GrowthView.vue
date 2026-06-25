<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { Plus, X } from 'lucide-vue-next'
import EmptyState from '../components/EmptyState.vue'
import GrowthChart from '../components/GrowthChart.vue'
import PageHeader from '../components/PageHeader.vue'
import PetSelector from '../components/PetSelector.vue'
import { growthApi } from '../api/growth'
import { usePetsStore } from '../stores/pets'
import { todayDate } from '../utils/date'

const petsStore = usePetsStore()
const selectedPetId = ref('')
const records = ref([])
const loading = ref(false)
const showCreate = ref(false)
const form = reactive({
  date: todayDate(),
  weight: '',
  length: '',
  note: ''
})

const selectedPet = computed(() => petsStore.currentPet(selectedPetId.value))

watch(
  () => petsStore.pets,
  (pets) => {
    if (!selectedPetId.value && pets.length) {
      selectedPetId.value = pets[0].id
    }
  },
  { immediate: true }
)

watch(selectedPetId, (id) => {
  if (id) loadRecords(id)
})

async function loadRecords(id = selectedPetId.value) {
  loading.value = true
  try {
    const { data } = await growthApi.list(id)
    records.value = data
  } finally {
    loading.value = false
  }
}

async function addRecord() {
  await growthApi.create(selectedPetId.value, {
    date: form.date,
    weight: form.weight === '' ? null : Number(form.weight),
    length: form.length === '' ? null : Number(form.length),
    note: form.note || null
  })
  form.weight = ''
  form.length = ''
  form.note = ''
  showCreate.value = false
  await loadRecords()
  await petsStore.fetchPets()
}

function openCreate() {
  form.date = todayDate()
  showCreate.value = true
}
</script>

<template>
  <section class="px-4 py-6 sm:px-6 lg:px-8">
    <PageHeader
      eyebrow="Growth"
      title="成长记录"
      description="用体重和体长曲线追踪状态变化，后续可以标记蜕皮、产蛋等关键节点。"
    />

    <EmptyState
      v-if="!petsStore.pets.length"
      title="先创建宠物档案"
      description="成长记录必须关联到一只宠物。"
    >
      <RouterLink class="btn-primary" to="/pets">去创建档案</RouterLink>
    </EmptyState>

    <template v-else>
      <div class="mb-5 max-w-sm">
        <PetSelector v-model="selectedPetId" :pets="petsStore.pets" />
      </div>

      <div class="grid gap-6">
        <div class="panel rounded-lg p-5">
          <div class="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 class="text-xl font-black">{{ selectedPet?.name }} 的成长曲线</h2>
              <p class="text-sm text-ink/60">体重使用左轴，体长使用右轴。</p>
            </div>
            <p class="text-sm font-semibold text-ink/55">{{ records.length }} 条记录</p>
          </div>
          <GrowthChart v-if="records.length" :records="records" />
          <p v-else class="rounded-md bg-shell p-6 text-center text-sm text-ink/60">
            暂无成长记录。
          </p>
        </div>

      </div>

      <div class="mt-6 panel rounded-lg p-5">
        <h2 class="mb-4 text-xl font-black">记录列表</h2>
        <div class="overflow-x-auto">
          <table class="w-full min-w-[560px] text-left text-sm">
            <thead class="text-xs uppercase tracking-normal text-ink/50">
              <tr>
                <th class="border-b border-ink/10 py-3">日期</th>
                <th class="border-b border-ink/10 py-3">体重</th>
                <th class="border-b border-ink/10 py-3">体长</th>
                <th class="border-b border-ink/10 py-3">备注</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in records" :key="record.id">
                <td class="border-b border-ink/5 py-3 font-semibold">{{ record.date }}</td>
                <td class="border-b border-ink/5 py-3">{{ record.weight ?? '-' }}g</td>
                <td class="border-b border-ink/5 py-3">{{ record.length ?? '-' }}cm</td>
                <td class="border-b border-ink/5 py-3 text-ink/65">{{ record.note || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="showCreate" class="fixed inset-0 z-40 bg-ink/35 p-4 backdrop-blur-sm" @click.self="showCreate = false">
        <aside class="ml-auto flex h-full max-w-lg flex-col overflow-auto rounded-lg bg-bone p-5 shadow-[0_30px_80px_rgba(23,33,27,.35)]">
          <div class="mb-5 flex items-start justify-between gap-4">
            <div>
              <p class="label text-clay">Growth Log</p>
              <h2 class="mt-1 text-2xl font-black">新增记录</h2>
              <p class="mt-2 text-sm leading-6 text-ink/60">记录体重、体长和备注，曲线会在保存后自动更新。</p>
            </div>
            <button class="rounded-md p-2 text-ink/55 hover:bg-shell" aria-label="关闭新增记录" @click="showCreate = false">
              <X class="h-5 w-5" />
            </button>
          </div>

          <form class="space-y-4" @submit.prevent="addRecord">
            <label class="block">
              <span class="label">日期</span>
              <input v-model="form.date" class="field mt-1" type="date" required />
            </label>
            <label class="block">
              <span class="label">体重 g</span>
              <input v-model="form.weight" class="field mt-1" type="number" min="0" step="0.1" />
            </label>
            <label class="block">
              <span class="label">体长 cm</span>
              <input v-model="form.length" class="field mt-1" type="number" min="0" step="0.1" />
            </label>
            <label class="block">
              <span class="label">备注</span>
              <textarea v-model="form.note" class="field mt-1 min-h-24"></textarea>
            </label>
            <button class="btn-primary w-full" :disabled="loading">
              <Plus class="h-4 w-4" />
              添加成长记录
            </button>
          </form>
        </aside>
      </div>

      <button
        class="fixed bottom-24 right-5 z-20 grid h-14 w-14 place-items-center rounded-full bg-ink text-bone shadow-soft transition hover:bg-moss lg:bottom-8"
        type="button"
        aria-label="新增成长记录"
        @click="openCreate"
      >
        <Plus class="h-6 w-6" />
      </button>
    </template>
  </section>
</template>
