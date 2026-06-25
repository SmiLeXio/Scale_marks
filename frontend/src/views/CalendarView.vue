<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { Bell, Check, ChevronLeft, ChevronRight, Copy, Plus, RotateCcw, Send, Settings } from 'lucide-vue-next'
import EmptyState from '../components/EmptyState.vue'
import PageHeader from '../components/PageHeader.vue'
import { notificationsApi } from '../api/notifications'
import { remindersApi } from '../api/reminders'
import { usePetsStore } from '../stores/pets'
import { formatDateTime, toDateTimeLocal, toLocalDateKey } from '../utils/date'

const petsStore = usePetsStore()
const reminders = ref([])
const currentMonth = ref(new Date())
const showSettings = ref(false)
const qqBinding = ref(null)
const qqStatus = ref('')
const manualGroupOpenid = ref('')
const testingQQ = ref(false)

const form = reactive({
  pet_id: '',
  type: 'feeding',
  title: '',
  description: '',
  due_date: toDateTimeLocal(),
  repeat_type: 'once',
  repeat_interval_days: 7
})

const monthLabel = computed(() => {
  return new Intl.DateTimeFormat('zh-CN', { year: 'numeric', month: 'long' }).format(currentMonth.value)
})

const remindersByDate = computed(() => {
  return reminders.value.reduce((groups, reminder) => {
    const key = reminder.due_date.slice(0, 10)
    groups[key] = groups[key] || []
    groups[key].push(reminder)
    return groups
  }, {})
})

const calendarDays = computed(() => {
  const year = currentMonth.value.getFullYear()
  const month = currentMonth.value.getMonth()
  const first = new Date(year, month, 1)
  const start = new Date(first)
  start.setDate(first.getDate() - first.getDay())

  return Array.from({ length: 42 }, (_, index) => {
    const date = new Date(start)
    date.setDate(start.getDate() + index)
    const key = toLocalDateKey(date)
    return {
      key,
      day: date.getDate(),
      isCurrentMonth: date.getMonth() === month,
      isToday: key === toLocalDateKey(),
      reminders: remindersByDate.value[key] || []
    }
  })
})

const upcomingReminders = computed(() => {
  return reminders.value
    .filter((reminder) => !reminder.is_completed)
    .slice()
    .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
    .slice(0, 6)
})

watch(
  () => petsStore.pets,
  (pets) => {
    if (!form.pet_id && pets.length) {
      form.pet_id = pets[0].id
    }
  },
  { immediate: true }
)

async function loadReminders() {
  const { data } = await remindersApi.list()
  reminders.value = data
}

async function loadQQBinding() {
  const { data } = await notificationsApi.getQQGroup()
  qqBinding.value = data
  manualGroupOpenid.value = data.group_openid || ''
}

async function addReminder() {
  await remindersApi.create({
    ...form,
    title: form.title || '养护提醒',
    description: form.description || null,
    due_date: form.due_date,
    repeat_interval_days: form.repeat_type === 'custom' ? Number(form.repeat_interval_days) : null
  })
  form.title = ''
  form.description = ''
  form.due_date = toDateTimeLocal()
  form.repeat_type = 'once'
  await loadReminders()
}

async function completeReminder(id) {
  const { data } = await remindersApi.complete(id)
  const index = reminders.value.findIndex((reminder) => reminder.id === id)
  if (index >= 0) {
    reminders.value[index] = data
  }
}

function moveMonth(offset) {
  const next = new Date(currentMonth.value)
  next.setMonth(next.getMonth() + offset)
  currentMonth.value = next
}

async function openSettings() {
  showSettings.value = true
  qqStatus.value = ''
  await loadQQBinding()
}

async function regenerateCode() {
  const { data } = await notificationsApi.regenerateQQGroupCode()
  qqBinding.value = data
  qqStatus.value = '绑定码已更新'
}

async function saveQQSettings() {
  const { data } = await notificationsApi.updateQQGroup({
    enabled: qqBinding.value.enabled,
    daily_summary_time: qqBinding.value.daily_summary_time
  })
  qqBinding.value = data
  qqStatus.value = '设置已保存'
}

async function manualBind() {
  const { data } = await notificationsApi.manualBindQQGroup({ group_openid: manualGroupOpenid.value })
  qqBinding.value = data
  qqStatus.value = '群 openid 已绑定'
}

async function testQQ() {
  qqStatus.value = ''
  testingQQ.value = true
  try {
    const { data } = await notificationsApi.testQQGroup()
    qqStatus.value = data.detail
  } catch (err) {
    qqStatus.value = err.response?.data?.detail || '测试消息发送失败'
  } finally {
    testingQQ.value = false
  }
}

function copyBindingCommand() {
  const text = `绑定鳞迹群 ${qqBinding.value.binding_code}`
  navigator.clipboard?.writeText(text)
  qqStatus.value = '绑定命令已复制'
}

loadReminders()
</script>

<template>
  <section class="px-4 py-6 sm:px-6 lg:px-8">
    <PageHeader
      eyebrow="Calendar"
      title="养护日历"
      description="按月查看提醒，新增一次性或每 N 天循环的养护任务，并配置 QQ 群提醒。"
    >
      <button class="btn-secondary" @click="openSettings">
        <Bell class="h-4 w-4" />
        通知设置
        <Settings class="h-4 w-4" />
      </button>
    </PageHeader>

    <EmptyState
      v-if="!petsStore.pets.length"
      title="先创建宠物档案"
      description="提醒必须关联到一只宠物。"
    >
      <RouterLink class="btn-primary" to="/pets">去创建档案</RouterLink>
    </EmptyState>

    <template v-else>
      <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_380px]">
        <section class="panel rounded-lg p-5">
          <div class="mb-5 flex items-center justify-between gap-3">
            <div>
              <p class="label text-clay">Month</p>
              <h2 class="mt-1 text-2xl font-black">{{ monthLabel }}</h2>
            </div>
            <div class="flex gap-2">
              <button class="btn-secondary min-h-10 px-3" @click="moveMonth(-1)" aria-label="上个月">
                <ChevronLeft class="h-4 w-4" />
              </button>
              <button class="btn-secondary min-h-10 px-3" @click="moveMonth(1)" aria-label="下个月">
                <ChevronRight class="h-4 w-4" />
              </button>
            </div>
          </div>

          <div class="grid grid-cols-7 border-y border-ink/10 bg-shell text-center text-xs font-black text-ink/50">
            <div v-for="day in ['日', '一', '二', '三', '四', '五', '六']" :key="day" class="py-2">{{ day }}</div>
          </div>

          <div class="grid grid-cols-7">
            <div
              v-for="day in calendarDays"
              :key="day.key"
              class="min-h-28 border-b border-r border-ink/10 bg-bone/80 p-2 text-sm first:border-l"
              :class="day.isCurrentMonth ? '' : 'bg-shell/50 text-ink/30'"
            >
              <div class="mb-2 flex items-center justify-between">
                <span
                  class="grid h-7 w-7 place-items-center rounded-full font-black"
                  :class="day.isToday ? 'bg-ink text-bone' : ''"
                >
                  {{ day.day }}
                </span>
                <span v-if="day.reminders.length" class="text-xs font-black text-clay">{{ day.reminders.length }}</span>
              </div>
              <div class="space-y-1">
                <div
                  v-for="reminder in day.reminders.slice(0, 3)"
                  :key="reminder.id"
                  class="truncate rounded bg-water/10 px-2 py-1 text-xs font-bold text-water"
                  :class="reminder.is_completed ? 'opacity-45 line-through' : ''"
                >
                  {{ reminder.pet_name }} · {{ reminder.title }}
                </div>
                <p v-if="day.reminders.length > 3" class="px-2 text-xs font-bold text-ink/45">
                  +{{ day.reminders.length - 3 }}
                </p>
              </div>
            </div>
          </div>
        </section>

        <aside class="space-y-6">
          <form class="panel rounded-lg p-5" @submit.prevent="addReminder">
            <div class="mb-5">
              <p class="label text-clay">Create</p>
              <h2 class="mt-1 text-xl font-black">新增提醒</h2>
            </div>
            <div class="space-y-4">
              <label class="block">
                <span class="label">宠物</span>
                <select v-model="form.pet_id" class="field mt-1">
                  <option v-for="pet in petsStore.pets" :key="pet.id" :value="pet.id">
                    {{ pet.name }}
                  </option>
                </select>
              </label>
              <div class="grid grid-cols-2 gap-3">
                <label class="block">
                  <span class="label">类型</span>
                  <select v-model="form.type" class="field mt-1">
                    <option value="feeding">喂食</option>
                    <option value="bathing">泡澡</option>
                    <option value="calcium">补钙</option>
                    <option value="vitamin">维生素</option>
                    <option value="temperature">温控</option>
                    <option value="cleaning">清洁</option>
                  </select>
                </label>
                <label class="block">
                  <span class="label">循环</span>
                  <select v-model="form.repeat_type" class="field mt-1">
                    <option value="once">一次</option>
                    <option value="daily">每天</option>
                    <option value="weekly">每周</option>
                    <option value="biweekly">双周</option>
                    <option value="monthly">每月</option>
                    <option value="custom">每 N 天</option>
                  </select>
                </label>
              </div>
              <label v-if="form.repeat_type === 'custom'" class="block">
                <span class="label">每几天提醒一次</span>
                <input v-model="form.repeat_interval_days" class="field mt-1" type="number" min="1" max="365" />
              </label>
              <label class="block">
                <span class="label">标题</span>
                <input v-model="form.title" class="field mt-1" placeholder="例如：补钙" />
              </label>
              <label class="block">
                <span class="label">时间</span>
                <input v-model="form.due_date" class="field mt-1" type="datetime-local" required />
              </label>
              <label class="block">
                <span class="label">说明</span>
                <textarea v-model="form.description" class="field mt-1 min-h-20" placeholder="可选"></textarea>
              </label>
            </div>
            <button class="btn-primary mt-5 w-full">
              <Plus class="h-4 w-4" />
              新增提醒
            </button>
          </form>

          <section class="panel rounded-lg p-5">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <p class="label text-clay">Upcoming</p>
                <h2 class="mt-1 text-xl font-black">近期提醒</h2>
              </div>
              <RotateCcw class="h-5 w-5 text-water" />
            </div>
            <div class="space-y-3">
              <article v-for="reminder in upcomingReminders" :key="reminder.id" class="rounded-md border border-ink/10 bg-shell p-4">
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <p class="font-black">{{ reminder.title }}</p>
                    <p class="mt-1 text-sm text-ink/60">{{ reminder.pet_name }} · {{ formatDateTime(reminder.due_date) }}</p>
                    <p v-if="reminder.repeat_type === 'custom'" class="mt-1 text-xs font-bold text-water">
                      每 {{ reminder.repeat_interval_days }} 天
                    </p>
                  </div>
                  <button
                    class="rounded-md p-2 text-water hover:bg-water/10 disabled:text-ink/25"
                    :disabled="reminder.is_completed"
                    aria-label="完成提醒"
                    @click="completeReminder(reminder.id)"
                  >
                    <Check class="h-5 w-5" />
                  </button>
                </div>
              </article>
              <p v-if="!upcomingReminders.length" class="rounded-md bg-shell p-4 text-sm text-ink/60">暂无未完成提醒。</p>
            </div>
          </section>
        </aside>
      </div>
    </template>

    <div v-if="showSettings" class="fixed inset-0 z-40 bg-ink/35 p-4 backdrop-blur-sm" @click.self="showSettings = false">
      <aside class="ml-auto flex h-full max-w-lg flex-col overflow-auto rounded-lg bg-bone p-5 shadow-[0_30px_80px_rgba(23,33,27,.35)]">
        <div class="mb-5 flex items-start justify-between gap-4">
          <div>
            <p class="label text-clay">QQ Group</p>
            <h2 class="mt-1 text-2xl font-black">QQ群提醒设置</h2>
            <p class="mt-2 text-sm leading-6 text-ink/60">把机器人拉进群后，在群里 @ 机器人发送绑定命令即可接收每日养护汇总。</p>
          </div>
          <button class="rounded-md px-3 py-2 text-sm font-black text-ink/55 hover:bg-shell" @click="showSettings = false">关闭</button>
        </div>

        <div v-if="qqBinding" class="space-y-5">
          <section class="rounded-lg border border-ink/10 bg-shell p-4">
            <p class="label">群内绑定命令</p>
            <div class="mt-2 flex items-center gap-2 rounded-md bg-bone p-3">
              <code class="min-w-0 flex-1 truncate text-sm font-black">绑定鳞迹群 {{ qqBinding.binding_code }}</code>
              <button class="btn-secondary min-h-10 px-3" @click="copyBindingCommand">
                <Copy class="h-4 w-4" />
              </button>
            </div>
            <button class="btn-secondary mt-3" @click="regenerateCode">重新生成绑定码</button>
          </section>

          <section class="rounded-lg border border-ink/10 bg-shell p-4">
            <p class="label">提醒开关</p>
            <label class="mt-3 flex items-center justify-between rounded-md bg-bone p-3 text-sm font-black">
              启用 QQ 群每日汇总
              <input v-model="qqBinding.enabled" type="checkbox" />
            </label>
            <label class="mt-3 block">
              <span class="label">每日发送时间</span>
              <input v-model="qqBinding.daily_summary_time" class="field mt-1" type="time" />
            </label>
            <button class="btn-primary mt-3" @click="saveQQSettings">保存设置</button>
          </section>

          <section class="rounded-lg border border-ink/10 bg-shell p-4">
            <p class="label">调试绑定</p>
            <p class="mt-2 text-sm leading-6 text-ink/60">正式使用时由机器人自动写入 group_openid；开发调试时也可以手动填入。</p>
            <input v-model="manualGroupOpenid" class="field mt-3" placeholder="group_openid" />
            <button class="btn-secondary mt-3" @click="manualBind">手动绑定</button>
          </section>

          <section class="rounded-lg border border-ink/10 bg-shell p-4">
            <p class="label">测试</p>
            <button class="btn-primary mt-3" :disabled="testingQQ || !qqBinding.group_openid" @click="testQQ">
              <Send class="h-4 w-4" />
              {{ testingQQ ? '发送中' : '发送测试消息' }}
            </button>
            <p v-if="!qqBinding.group_openid" class="mt-2 text-sm text-clay">还没有绑定群，无法发送测试消息。</p>
          </section>

          <p v-if="qqStatus" class="rounded-md bg-water/10 px-3 py-2 text-sm font-black text-water">{{ qqStatus }}</p>
        </div>
      </aside>
    </div>
  </section>
</template>
