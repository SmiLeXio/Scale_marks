<script setup>
import { computed, ref, watch } from 'vue'
import { SPECIES_GROUPS, getSpeciesGroupBySpecies } from '../data/species'

const props = defineProps({
  modelValue: { type: String, default: '玉米蛇' }
})

const emit = defineEmits(['update:modelValue'])
const activeGroupId = ref(getSpeciesGroupBySpecies(props.modelValue).id)

const activeGroup = computed(() => SPECIES_GROUPS.find((group) => group.id === activeGroupId.value) || SPECIES_GROUPS[0])

watch(
  () => props.modelValue,
  (species) => {
    activeGroupId.value = getSpeciesGroupBySpecies(species).id
  }
)

function selectGroup(group) {
  activeGroupId.value = group.id
  if (!group.species.includes(props.modelValue)) {
    emit('update:modelValue', group.species[0])
  }
}
</script>

<template>
  <div class="field-shell">
    <div class="mb-3 flex items-center justify-between gap-3">
      <div>
        <p class="label">种类</p>
        <p class="mt-1 text-sm font-bold text-ink">先选大类，再选具体品种</p>
      </div>
      <span class="rounded bg-bone px-2 py-1 text-xs font-black text-ink/60">{{ modelValue }}</span>
    </div>

    <div class="grid grid-cols-4 gap-2">
      <button
        v-for="group in SPECIES_GROUPS"
        :key="group.id"
        type="button"
        class="chip"
        :class="activeGroupId === group.id ? 'chip-active' : ''"
        @click="selectGroup(group)"
      >
        {{ group.label }}
      </button>
    </div>

    <div class="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
      <button
        v-for="species in activeGroup.species"
        :key="species"
        type="button"
        class="rounded-md border px-3 py-3 text-left text-sm font-black transition"
        :class="modelValue === species ? 'border-water bg-water/10 text-water' : 'border-ink/10 bg-bone text-ink/70 hover:border-water'"
        @click="$emit('update:modelValue', species)"
      >
        {{ species }}
      </button>
    </div>
  </div>
</template>
