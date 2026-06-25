<script setup>
import { computed, ref } from 'vue'
import { ChevronDown, Check } from 'lucide-vue-next'
import PetAvatar from './PetAvatar.vue'

const props = defineProps({
  pets: { type: Array, required: true },
  modelValue: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])
const open = ref(false)
const selectedPet = computed(() => props.pets.find((pet) => pet.id === props.modelValue) || props.pets[0])

function choosePet(id) {
  emit('update:modelValue', id)
  open.value = false
}
</script>

<template>
  <div class="relative">
    <span class="label">选择宠物</span>
    <button
      class="mt-1 flex w-full items-center gap-3 rounded-lg border border-ink/10 bg-bone p-3 text-left shadow-soft transition hover:border-water focus:outline-none focus:ring-2 focus:ring-water/20"
      type="button"
      @click="open = !open"
    >
      <PetAvatar v-if="selectedPet" :pet="selectedPet" size="small" />
      <div class="min-w-0 flex-1">
        <p class="truncate text-sm font-black">{{ selectedPet?.name || '选择宠物' }}</p>
        <p class="mt-1 truncate text-xs font-semibold text-ink/55">
          {{ selectedPet?.species || '暂无宠物' }}
          <span v-if="selectedPet?.current_weight"> · {{ selectedPet.current_weight }}g</span>
        </p>
      </div>
      <ChevronDown class="h-5 w-5 text-ink/45 transition" :class="open ? 'rotate-180' : ''" />
    </button>

    <div
      v-if="open"
      class="absolute z-30 mt-2 max-h-80 w-full overflow-auto rounded-lg border border-ink/10 bg-bone p-2 shadow-[0_18px_50px_rgba(23,33,27,.18)]"
    >
      <button
        v-for="pet in pets"
        :key="pet.id"
        class="flex w-full items-center gap-3 rounded-md p-2 text-left transition hover:bg-shell"
        type="button"
        @click="choosePet(pet.id)"
      >
        <PetAvatar :pet="pet" size="small" />
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-black">{{ pet.name }}</p>
          <p class="mt-1 truncate text-xs font-semibold text-ink/55">
            {{ pet.species }}
            <span v-if="pet.current_weight"> · {{ pet.current_weight }}g</span>
          </p>
        </div>
        <Check v-if="pet.id === modelValue" class="h-4 w-4 text-water" />
      </button>
    </div>
  </div>
</template>
