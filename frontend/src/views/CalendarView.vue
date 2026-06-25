<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { Bell, Check, ChevronLeft, ChevronRight, Clock3, Copy, Plus, RotateCcw, Send, Settings, X } from 'lucide-vue-next'
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
const showCreate = ref(false)
const selectedDay = ref(null)
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
  return calendarOccurrences.value.reduce((groups, reminder) => {
    const key = reminder.occurrence_date
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

const calendarRange = computed(() => {
  const year = currentMonth.value.getFullYear()
  const month = currentMonth.value.getMonth()
  const first = new Date(year, month, 1)
  const start = new Date(first)
  start.setDate(first.getDate() - first.getDay())
  const end = new Date(start)
  end.setDate(start.getDate() + 41)
  return {
    start,
    end
  }
})

const calendarOccurrences = computed(() => {
  const { start, end } = calendarRange.value
  return reminders.value.flatMap((reminder) => expandReminderOccurrences(reminder, start, end))
})

const upcomingReminders = computed(() => {
  const now = new Date()
  const rangeEnd = new Date(now)
  rangeEnd.setDate(now.getDate() + 60)
  return reminders.value
    .filter((reminder) => !reminder.is_completed)
    .flatMap((reminder) => expandReminderOccurrences(reminder, now, rangeEnd))
    .sort((a, b) => new Date(a.occurrence_at) - new Date(b.occurrence_at))
    .slice(0, 6)
})

const selectedDayReminders = computed(() => {
  if (!selectedDay.value) return []
  return remindersByDate.value[selectedDay.value.key] || []
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
  showCreate.value = false
  await loadReminders()
}

function openCreate() {
  form.due_date = toDateTimeLocal()
  showCreate.value = true
}

async function completeReminder(id) {
  const { data } = await remindersApi.complete(id)
  const index = reminders.value.findIndex((reminder) => reminder.id === id)
  if (index >= 0) {
    reminders.value[index] = data
  }
}

function parseDateKey(key) {
  const [year, month, day] = key.split('-').map(Number)
  return new Date(year, month - 1, day)
}

function repeatIntervalDays(reminder) {
  if (reminder.repeat_type === 'daily') return 1
  if (reminder.repeat_type === 'weekly') return 7
  if (reminder.repeat_type === 'biweekly') return 14
  if (reminder.repeat_type === 'custom') return Number(reminder.repeat_interval_days)
  return null
}

function addMonth(date) {
  const next = new Date(date)
  const sourceDay = next.getDate()
  next.setDate(1)
  next.setMonth(next.getMonth() + 1)
  const lastDay = new Date(next.getFullYear(), next.getMonth() + 1, 0).getDate()
  next.setDate(Math.min(sourceDay, lastDay))
  return next
}

function occurrenceFrom(reminder, date) {
  const source = new Date(reminder.due_date)
  const occurrenceAt = new Date(date)
  occurrenceAt.setHours(source.getHours(), source.getMinutes(), 0, 0)
  return {
    ...reminder,
    occurrence_date: toLocalDateKey(occurrenceAt),
    occurrence_at: toDateTimeLocal(occurrenceAt),
    is_occurrence: occurrenceAt.getTime() !== source.getTime()
  }
}

function expandReminderOccurrences(reminder, rangeStart, rangeEnd) {
  const due = new Date(reminder.due_date)
  const firstDate = new Date(due)
  firstDate.setHours(0, 0, 0, 0)
  const start = new Date(rangeStart)
  start.setHours(0, 0, 0, 0)
  const end = new Date(rangeEnd)
  end.setHours(23, 59, 59, 999)

  if (reminder.repeat_type === 'once') {
    return due >= start && due <= end ? [occurrenceFrom(reminder, due)] : []
  }

  if (end < firstDate) return []

  if (reminder.repeat_type === 'monthly') {
    const results = []
    let cursor = new Date(firstDate)
    while (cursor <= end) {
      if (cursor >= start) {
        results.push(occurrenceFrom(reminder, cursor))
      }
      cursor = addMonth(cursor)
    }
    return results
  }

  const interval = repeatIntervalDays(reminder)
  if (!interval) return []

  const results = []
  const cursor = new Date(firstDate)
  if (cursor < start) {
    const daysBehind = Math.floor((start - cursor) / 86400000)
    cursor.setDate(cursor.getDate() + Math.floor(daysBehind / interval) * interval)
    while (cursor < start) cursor.setDate(cursor.getDate() + interval)
  }
  while (cursor <= end) {
    results.push(occurrenceFrom(reminder, cursor))
    cursor.setDate(cursor.getDate() + interval)
  }
  return results
}

function repeatLabel(reminder) {
  if (reminder.repeat_type === 'daily') return '每天'
  if (reminder.repeat_type === 'weekly') return '每周'
  if (reminder.repeat_type === 'biweekly') return '双周'
  if (reminder.repeat_type === 'monthly') return '每月'
  if (reminder.repeat_type === 'custom') return `每 ${reminder.repeat_interval_days} 天`
  return '一次'
}

function formatTime(value) {
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value))
}

function openDay(day) {
  selectedDay.value = day
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
              class="min-h-28 cursor-pointer border-b border-r border-ink/10 bg-bone/80 p-2 text-sm first:border-l hover:bg-water/5"
              :class="[
                day.isCurrentMonth ? '' : 'bg-shell/50 text-ink/30',
                selectedDay?.key === day.key ? 'ring-2 ring-inset ring-water' : ''
              ]"
              @click="openDay(day)"
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
                  :key="`${reminder.id}-${reminder.occurrence_at}`"
                  class="min-w-0 rounded bg-water/10 px-2 py-1 text-xs font-bold text-water"
                  :class="reminder.is_completed ? 'opacity-45 line-through' : ''"
                >
                  <span class="block truncate">{{ formatTime(reminder.occurrence_at) }} · {{ reminder.title }}</span>
                  <span class="block truncate text-[11px] text-ink/45">{{ reminder.pet_name }}</span>
                </div>
                <p v-if="day.reminders.length > 3" class="px-2 text-xs font-bold text-ink/45">
                  +{{ day.reminders.length - 3 }}
                </p>
              </div>
            </div>
          </div>
        </section>

        <aside class="space-y-6">
          <section class="panel rounded-lg p-5">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <p class="label text-clay">Upcoming</p>
                <h2 class="mt-1 text-xl font-black">近期提醒</h2>
              </div>
              <RotateCcw class="h-5 w-5 text-water" />
            </div>
            <div class="space-y-3">
              <article v-for="reminder in upcomingReminders" :key="`${reminder.id}-${reminder.occurrence_at}`" class="rounded-md border border-ink/10 bg-shell p-4">
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <p class="font-black">{{ reminder.title }}</p>
                    <p class="mt-1 text-sm text-ink/60">{{ reminder.pet_name }} · {{ formatDateTime(reminder.occurrence_at) }}</p>
                    <p class="mt-1 text-xs font-bold text-water">{{ repeatLabel(reminder) }}</p>
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

    <div v-if="showCreate" class="fixed inset-0 z-40 bg-ink/35 p-4 backdrop-blur-sm" @click.self="showCreate = false">
      <aside class="ml-auto flex h-full max-w-lg flex-col overflow-auto rounded-lg bg-bone p-5 shadow-[0_30px_80px_rgba(23,33,27,.35)]">
        <div class="mb-5 flex items-start justify-between gap-4">
          <div>
            <p class="label text-clay">Create</p>
            <h2 class="mt-1 text-2xl font-black">新增提醒</h2>
            <p class="mt-2 text-sm leading-6 text-ink/60">设置首次提醒时间和循环规则，循环任务会自动出现在后续日历日期上。</p>
          </div>
          <button class="rounded-md p-2 text-ink/55 hover:bg-shell" aria-label="关闭新增提醒" @click="showCreate = false">
            <X class="h-5 w-5" />
          </button>
        </div>

        <form class="space-y-4" @submit.prevent="addReminder">
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
            <textarea v-model="form.description" class="field mt-1 min-h-24" placeholder="可选"></textarea>
          </label>
          <button class="btn-primary w-full">
            <Plus class="h-4 w-4" />
            新增提醒
          </button>
        </form>
      </aside>
    </div>

    <div v-if="selectedDay" class="fixed inset-0 z-30 bg-ink/25 p-4 backdrop-blur-sm" @click.self="selectedDay = null">
      <aside class="ml-auto flex h-full max-w-xl flex-col overflow-hidden rounded-lg bg-bone shadow-[0_30px_80px_rgba(23,33,27,.35)]">
        <div class="flex items-start justify-between gap-4 border-b border-ink/10 p-5">
          <div>
            <p class="label text-clay">Day Detail</p>
            <h2 class="mt-1 text-2xl font-black">{{ selectedDay.key }} 的提醒</h2>
            <p class="mt-2 text-sm text-ink/60">共 {{ selectedDayReminders.length }} 个任务</p>
          </div>
          <button class="rounded-md p-2 text-ink/55 hover:bg-shell" aria-label="关闭日期详情" @click="selectedDay = null">
            <X class="h-5 w-5" />
          </button>
        </div>

        <div class="flex-1 overflow-auto p-5">
          <div v-if="selectedDayReminders.length" class="space-y-3">
            <article
              v-for="reminder in selectedDayReminders"
              :key="`${reminder.id}-${reminder.occurrence_at}`"
              class="rounded-lg border border-ink/10 bg-shell p-4"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <div class="flex flex-wrap items-center gap-2">
                    <p class="font-black">{{ reminder.title }}</p>
                    <span class="rounded bg-water/10 px-2 py-1 text-xs font-black text-water">{{ repeatLabel(reminder) }}</span>
                  </div>
                  <p class="mt-2 flex items-center gap-2 text-sm text-ink/60">
                    <Clock3 class="h-4 w-4 text-clay" />
                    {{ formatDateTime(reminder.occurrence_at) }}
                  </p>
                  <p class="mt-1 text-sm text-ink/60">{{ reminder.pet_name }}</p>
                  <p v-if="reminder.description" class="mt-3 rounded-md bg-bone p-3 text-sm leading-6 text-ink/70">
                    {{ reminder.description }}
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
          </div>
          <p v-else class="rounded-md bg-shell p-4 text-sm text-ink/60">这一天没有提醒。</p>
        </div>
      </aside>
    </div>

    <button
      v-if="petsStore.pets.length"
      class="fixed bottom-24 right-5 z-20 grid h-14 w-14 place-items-center rounded-full bg-ink text-bone shadow-soft transition hover:bg-moss lg:bottom-8"
      type="button"
      aria-label="新增提醒"
      @click="openCreate"
    >
      <Plus class="h-6 w-6" />
    </button>
  </section>
</template>
