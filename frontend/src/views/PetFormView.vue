<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ArrowLeft, Save } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import ImageUploader from '../components/ImageUploader.vue'
import PageHeader from '../components/PageHeader.vue'
import SpeciesPicker from '../components/SpeciesPicker.vue'
import { usePetsStore } from '../stores/pets'

const router = useRouter()
const route = useRoute()
const petsStore = usePetsStore()
const error = ref('')
const saving = ref(false)
const form = reactive({
  name: '',
  species: '玉米蛇',
  morph: '',
  birth_date: '',
  gender: 'unknown',
  weight: '',
  length: '',
  feeding_cycle: 7,
  last_feeding_date: '',
  avatar_url: '',
  notes: ''
})

const isEdit = computed(() => route.name === 'pet-edit')
const editingPet = computed(() => petsStore.pets.find((pet) => pet.id === route.params.id))

function toInputDate(value) {
  return value ? String(value).slice(0, 10) : ''
}

function fillForm(pet) {
  if (!pet) return
  form.name = pet.name || ''
  form.species = pet.species || '玉米蛇'
  form.morph = pet.morph || ''
  form.birth_date = toInputDate(pet.birth_date)
  form.gender = pet.gender || 'unknown'
  form.weight = pet.weight ?? ''
  form.length = pet.length ?? ''
  form.feeding_cycle = pet.feeding_cycle ?? 7
  form.last_feeding_date = toInputDate(pet.last_feeding_date)
  form.avatar_url = pet.avatar_url || ''
  form.notes = pet.notes || ''
}

function payloadFromForm() {
  return {
    ...form,
    birth_date: form.birth_date || null,
    last_feeding_date: form.last_feeding_date || null,
    morph: form.morph || null,
    notes: form.notes || null,
    avatar_url: form.avatar_url || null,
    gender: form.gender === 'unknown' ? null : form.gender,
    weight: form.weight === '' ? null : Number(form.weight),
    length: form.length === '' ? null : Number(form.length),
    feeding_cycle: Number(form.feeding_cycle)
  }
}

async function submitPet() {
  error.value = ''
  if (isEdit.value && !editingPet.value) {
    error.value = '没有找到要修改的档案'
    return
  }
  saving.value = true
  try {
    if (isEdit.value) {
      await petsStore.updatePet(route.params.id, payloadFromForm())
    } else {
      await petsStore.createPet(payloadFromForm())
    }
    router.push('/pets')
  } catch (err) {
    error.value = err.response?.data?.detail || (isEdit.value ? '更新失败' : '创建失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  if (!petsStore.pets.length) {
    await petsStore.fetchPets()
  }
  if (isEdit.value) {
    if (editingPet.value) {
      fillForm(editingPet.value)
    } else {
      error.value = '没有找到要修改的档案'
    }
  }
})

watch(editingPet, (pet) => {
  if (isEdit.value) {
    fillForm(pet)
  }
})
</script>

<template>
  <section class="px-4 py-6 sm:px-6 lg:px-8">
      <PageHeader
      :eyebrow="isEdit ? 'Edit Pet' : 'New Pet'"
      :title="isEdit ? '修改宠物档案' : '新增宠物档案'"
      :description="isEdit ? '调整头像、品种、体重体长和养护设置，保存后会同步到总览和档案卡片。' : '分步骤录入核心信息，头像可选；没有头像时系统会根据品种生成临时头像。'"
    >
      <RouterLink class="btn-secondary" to="/pets">
        <ArrowLeft class="h-4 w-4" />
        返回档案
      </RouterLink>
    </PageHeader>

    <form class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]" @submit.prevent="submitPet">
      <div class="space-y-6">
        <section class="panel rounded-lg p-5">
          <div class="mb-5">
            <p class="label text-clay">01</p>
            <h2 class="mt-1 text-xl font-black">身份信息</h2>
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <label class="field-shell block">
              <span class="label">名称</span>
              <input v-model="form.name" class="mt-1 w-full bg-transparent text-lg font-black outline-none" required placeholder="例如：小青" />
            </label>
            <label class="field-shell block">
              <span class="label">基因/表型</span>
              <input v-model="form.morph" class="mt-1 w-full bg-transparent text-lg font-black outline-none" placeholder="白化、原色等" />
            </label>
          </div>
          <div class="mt-4">
            <SpeciesPicker v-model="form.species" />
          </div>
        </section>

        <section class="panel rounded-lg p-5">
          <div class="mb-5">
            <p class="label text-clay">02</p>
            <h2 class="mt-1 text-xl font-black">照片与基础数据</h2>
          </div>
          <ImageUploader v-model="form.avatar_url" />
          <div class="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <label class="field-shell block">
              <span class="label">出生/入手日期</span>
              <input v-model="form.birth_date" class="mt-2 w-full bg-transparent font-bold outline-none" type="date" />
            </label>
            <label class="field-shell block">
              <span class="label">性别</span>
              <select v-model="form.gender" class="mt-2 w-full bg-transparent font-bold outline-none">
                <option value="unknown">未知</option>
                <option value="male">雄性</option>
                <option value="female">雌性</option>
              </select>
            </label>
            <label class="field-shell block">
              <span class="label">体重 g</span>
              <input v-model="form.weight" class="mt-2 w-full bg-transparent font-bold outline-none" type="number" min="0" step="0.1" placeholder="0.0" />
            </label>
            <label class="field-shell block">
              <span class="label">体长 cm</span>
              <input v-model="form.length" class="mt-2 w-full bg-transparent font-bold outline-none" type="number" min="0" step="0.1" placeholder="0.0" />
            </label>
          </div>
        </section>

        <section class="panel rounded-lg p-5">
          <div class="mb-5">
            <p class="label text-clay">03</p>
            <h2 class="mt-1 text-xl font-black">养护设置</h2>
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <label class="field-shell block">
              <span class="label">喂食周期 天</span>
              <input v-model="form.feeding_cycle" class="mt-2 w-full bg-transparent text-lg font-black outline-none" type="number" min="1" max="90" />
            </label>
            <label class="field-shell block">
              <span class="label">上次喂食日期</span>
              <input v-model="form.last_feeding_date" class="mt-2 w-full bg-transparent font-bold outline-none" type="date" />
            </label>
          </div>
          <label class="field-shell mt-4 block">
            <span class="label">备注</span>
            <textarea v-model="form.notes" class="mt-2 min-h-28 w-full resize-none bg-transparent leading-6 outline-none" placeholder="饲养环境、来源、特殊情况"></textarea>
          </label>
        </section>
      </div>

      <aside class="xl:sticky xl:top-6 xl:self-start">
        <div class="panel rounded-lg p-5">
          <p class="label">预览</p>
          <div class="mt-4 overflow-hidden rounded-lg border border-ink/10 bg-shell">
            <img v-if="form.avatar_url" :src="form.avatar_url" alt="头像预览" class="h-48 w-full object-cover" />
            <div v-else class="grid h-48 place-items-center bg-ink text-5xl font-black text-bone">
              {{ form.species.slice(0, 1) }}
            </div>
            <div class="p-4">
              <h2 class="text-2xl font-black">{{ form.name || '未命名' }}</h2>
              <p class="mt-1 text-sm text-ink/60">{{ form.species }} · {{ form.morph || '未记录基因' }}</p>
            </div>
          </div>
          <p v-if="error" class="mt-4 rounded-md bg-clay/10 px-3 py-2 text-sm font-semibold text-clay">{{ error }}</p>
          <button class="btn-primary mt-5 w-full" :disabled="saving">
            <Save class="h-4 w-4" />
            {{ saving ? '保存中' : isEdit ? '保存修改' : '保存档案' }}
          </button>
        </div>
      </aside>
    </form>
  </section>
</template>
