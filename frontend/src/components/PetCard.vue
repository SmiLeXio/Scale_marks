<script setup>
import { CalendarDays, Pencil, Ruler, Scale, Trash2, Utensils } from 'lucide-vue-next'
import PetAvatar from './PetAvatar.vue'
import { formatDate } from '../utils/date'

defineProps({
  pet: { type: Object, required: true },
  compact: { type: Boolean, default: false },
  readonly: { type: Boolean, default: false }
})

defineEmits(['delete', 'edit'])
</script>

<template>
  <article
    class="group relative overflow-hidden rounded-lg border border-ink/10 bg-[#fbf8ee] shadow-[0_22px_45px_rgba(23,33,27,.14),inset_0_1px_0_rgba(255,255,255,.9)] transition duration-300 hover:-translate-y-1 hover:shadow-[0_30px_70px_rgba(23,33,27,.19),inset_0_1px_0_rgba(255,255,255,.95)]"
  >
    <div class="absolute inset-0 pointer-events-none opacity-55 [background-image:linear-gradient(rgba(23,33,27,.035)_1px,transparent_1px),linear-gradient(90deg,rgba(23,33,27,.03)_1px,transparent_1px)] [background-size:18px_18px]"></div>

    <div class="relative">
      <div class="relative h-52 overflow-hidden border-b border-ink/10 bg-shell sm:h-56">
        <PetAvatar :pet="pet" cover />
        <div class="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-ink/55 to-transparent"></div>
        <div class="absolute left-4 top-4 flex flex-wrap gap-2">
          <span class="rounded bg-bone/95 px-3 py-1 text-xs font-black text-ink shadow-sm">{{ pet.species }}</span>
          <span class="rounded bg-ink/80 px-3 py-1 text-xs font-black text-bone shadow-sm">{{ pet.gender || '未知性别' }}</span>
        </div>
        <div v-if="!readonly" class="absolute right-4 top-4 flex gap-2">
          <button
            class="grid h-9 w-9 place-items-center rounded-full bg-bone/95 text-ink shadow-sm transition hover:bg-water hover:text-bone"
            aria-label="编辑档案"
            @click="$emit('edit', pet.id)"
          >
            <Pencil class="h-4 w-4" />
          </button>
          <button
            class="grid h-9 w-9 place-items-center rounded-full bg-bone/95 text-ink shadow-sm transition hover:bg-clay hover:text-bone"
            aria-label="删除档案"
            @click="$emit('delete', pet.id)"
          >
            <Trash2 class="h-4 w-4" />
          </button>
        </div>
        <div class="absolute bottom-4 left-4 right-4">
          <h2 class="truncate text-3xl font-black leading-none text-bone drop-shadow">{{ pet.name }}</h2>
          <p class="mt-2 truncate text-sm font-semibold text-bone/85">{{ pet.morph || '未记录基因/表型' }}</p>
        </div>
      </div>

      <div class="p-4 sm:p-5">
        <div class="grid grid-cols-3 gap-3">
          <div class="rounded-lg border border-ink/10 bg-bone p-3 shadow-[inset_0_1px_0_rgba(255,255,255,.8)]">
            <div class="flex items-center gap-1.5 text-ink/45">
              <Scale class="h-3.5 w-3.5" />
              <span class="label">体重</span>
            </div>
            <p class="mt-2 text-xl font-black">{{ pet.weight ?? '-' }}g</p>
          </div>
          <div class="rounded-lg border border-ink/10 bg-bone p-3 shadow-[inset_0_1px_0_rgba(255,255,255,.8)]">
            <div class="flex items-center gap-1.5 text-ink/45">
              <Ruler class="h-3.5 w-3.5" />
              <span class="label">体长</span>
            </div>
            <p class="mt-2 text-xl font-black">{{ pet.length ?? '-' }}cm</p>
          </div>
          <div class="rounded-lg border border-ink/10 bg-bone p-3 shadow-[inset_0_1px_0_rgba(255,255,255,.8)]">
            <div class="flex items-center gap-1.5 text-ink/45">
              <Utensils class="h-3.5 w-3.5" />
              <span class="label">周期</span>
            </div>
            <p class="mt-2 text-xl font-black">{{ pet.feeding_cycle }}天</p>
          </div>
        </div>

        <div v-if="!compact" class="mt-4 flex items-center justify-between gap-3 rounded-lg border border-ink/10 bg-shell px-3 py-3">
          <div class="flex min-w-0 items-center gap-2">
            <CalendarDays class="h-4 w-4 shrink-0 text-water" />
            <div class="min-w-0">
              <p class="label">上次喂食</p>
              <p class="truncate text-sm font-black">{{ formatDate(pet.last_feeding_date) }}</p>
            </div>
          </div>
          <span class="shrink-0 rounded bg-bone px-2 py-1 text-xs font-black text-ink/55">档案卡</span>
        </div>

        <p v-if="pet.notes && !compact" class="mt-4 line-clamp-2 text-sm leading-6 text-ink/60">
          {{ pet.notes }}
        </p>
      </div>
    </div>
  </article>
</template>
