<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { Calculator, Plus, X } from 'lucide-vue-next'
import EmptyState from '../components/EmptyState.vue'
import PageHeader from '../components/PageHeader.vue'
import PetSelector from '../components/PetSelector.vue'
import { feedingApi } from '../api/feeding'
import { usePetsStore } from '../stores/pets'
import { todayDate } from '../utils/date'

const petsStore = usePetsStore()
const selectedPetId = ref('')
const records = ref([])
const suggestion = ref(null)
const showCreate = ref(false)
const form = reactive({
  date: todayDate(),
  food_type: '小鼠',
  food_weight: '',
  is_success: true,
  refused: false,
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
  if (id) loadFeeding(id)
})

async function loadFeeding(id = selectedPetId.value) {
  const [recordsResponse, suggestionResponse] = await Promise.all([
    feedingApi.list(id),
    feedingApi.calculate(id)
  ])
  records.value = recordsResponse.data
  suggestion.value = suggestionResponse.data
}

async function addRecord() {
  await feedingApi.create(selectedPetId.value, {
    date: form.date,
    food_type: form.food_type,
    food_weight: form.food_weight === '' ? null : Number(form.food_weight),
    is_success: form.is_success,
    refused: form.refused,
    note: form.note || null
  })
  form.food_weight = ''
  form.note = ''
  form.refused = false
  form.is_success = true
  showCreate.value = false
  await loadFeeding()
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
      eyebrow="Feeding"
      title="智能喂食"
      description="根据品种和体重估算喂食量，并在记录喂食后自动生成下一次喂食提醒。"
    />

    <EmptyState
      v-if="!petsStore.pets.length"
      title="先创建宠物档案"
      description="喂食建议需要宠物的品种与体重。"
    >
      <RouterLink class="btn-primary" to="/pets">去创建档案</RouterLink>
    </EmptyState>

    <template v-else>
      <div class="mb-5 max-w-sm">
        <PetSelector v-model="selectedPetId" :pets="petsStore.pets" />
      </div>

      <div class="grid gap-6 xl:grid-cols-[380px_minmax(0,1fr)]">
        <div class="grid gap-4 md:grid-cols-3 xl:grid-cols-1">
          <div class="panel rounded-lg p-5">
            <div class="flex items-center justify-between">
              <p class="label">建议喂食量</p>
              <Calculator class="h-5 w-5 text-water" />
            </div>
            <p class="mt-3 text-4xl font-black">{{ suggestion?.suggested_amount ?? 0 }}g</p>
            <p class="mt-1 text-sm text-ink/60">{{ selectedPet?.species }} · 当前体重 {{ suggestion?.weight ?? 0 }}g</p>
          </div>
          <div class="panel rounded-lg p-5">
            <p class="label">建议周期</p>
            <p class="mt-3 text-4xl font-black">{{ suggestion?.feeding_cycle_days ?? '-' }}天</p>
            <p class="mt-1 text-sm text-ink/60">按体重阶段估算</p>
          </div>
          <div class="panel rounded-lg p-5">
            <p class="label">下次喂食</p>
            <p class="mt-3 text-4xl font-black">{{ suggestion?.next_feeding_date || '待记录' }}</p>
            <p class="mt-1 text-sm text-ink/60">基于上次喂食日期</p>
          </div>
        </div>

        <div class="panel rounded-lg p-5">
          <h2 class="mb-4 text-xl font-black">喂食历史</h2>
          <div class="space-y-3">
            <article v-for="record in records" :key="record.id" class="rounded-md border border-ink/10 bg-shell p-4">
              <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p class="font-black">{{ record.date }} · {{ record.food_type }}</p>
                  <p class="text-sm text-ink/60">{{ record.food_weight ?? '-' }}g · {{ record.refused ? '拒食' : record.is_success ? '成功' : '未成功' }}</p>
                </div>
                <p class="text-sm text-ink/60">{{ record.note || '' }}</p>
              </div>
            </article>
            <p v-if="!records.length" class="rounded-md bg-shell p-4 text-sm text-ink/60">暂无喂食记录。</p>
          </div>
        </div>
      </div>

      <div v-if="showCreate" class="fixed inset-0 z-40 bg-ink/35 p-4 backdrop-blur-sm" @click.self="showCreate = false">
        <aside class="ml-auto flex h-full max-w-lg flex-col overflow-auto rounded-lg bg-bone p-5 shadow-[0_30px_80px_rgba(23,33,27,.35)]">
          <div class="mb-5 flex items-start justify-between gap-4">
            <div>
              <p class="label text-clay">Feeding Log</p>
              <h2 class="mt-1 text-2xl font-black">记录喂食</h2>
              <p class="mt-2 text-sm leading-6 text-ink/60">保存本次喂食后，系统会按周期更新下一次喂食提醒。</p>
            </div>
            <button class="rounded-md p-2 text-ink/55 hover:bg-shell" aria-label="关闭记录喂食" @click="showCreate = false">
              <X class="h-5 w-5" />
            </button>
          </div>

          <form class="space-y-4" @submit.prevent="addRecord">
            <label class="block">
              <span class="label">日期</span>
              <input v-model="form.date" class="field mt-1" type="date" required />
            </label>
            <label class="block">
              <span class="label">饲料类型</span>
              <input v-model="form.food_type" class="field mt-1" required />
            </label>
            <label class="block">
              <span class="label">饲料重量 g</span>
              <input v-model="form.food_weight" class="field mt-1" type="number" min="0" step="0.1" />
            </label>
            <div class="grid grid-cols-2 gap-3">
              <label class="flex min-h-11 items-center gap-2 rounded-md border border-ink/10 bg-shell px-3 text-sm font-semibold">
                <input v-model="form.is_success" type="checkbox" />
                成功进食
              </label>
              <label class="flex min-h-11 items-center gap-2 rounded-md border border-ink/10 bg-shell px-3 text-sm font-semibold">
                <input v-model="form.refused" type="checkbox" />
                拒食
              </label>
            </div>
            <label class="block">
              <span class="label">备注</span>
              <textarea v-model="form.note" class="field mt-1 min-h-24"></textarea>
            </label>
            <button class="btn-primary w-full">
              <Plus class="h-4 w-4" />
              保存喂食记录
            </button>
          </form>
        </aside>
      </div>

      <button
        class="fixed bottom-24 right-5 z-20 grid h-14 w-14 place-items-center rounded-full bg-ink text-bone shadow-soft transition hover:bg-moss lg:bottom-8"
        type="button"
        aria-label="记录喂食"
        @click="openCreate"
      >
        <Plus class="h-6 w-6" />
      </button>
    </template>
  </section>
</template>
