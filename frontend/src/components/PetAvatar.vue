<script setup>
import { computed } from 'vue'
import { getSpeciesGroupBySpecies, getSpeciesInitial } from '../data/species'

const props = defineProps({
  pet: { type: Object, required: true },
  size: { type: String, default: 'large' },
  cover: { type: Boolean, default: false }
})

const group = computed(() => getSpeciesGroupBySpecies(props.pet.species))
const initial = computed(() => getSpeciesInitial(props.pet.species))
const sizeClass = computed(() => {
  if (props.cover) return 'h-full w-full text-6xl'
  if (props.size === 'small') return 'h-14 w-14 text-xl'
  if (props.size === 'medium') return 'h-20 w-20 text-3xl'
  return 'h-28 w-28 text-5xl'
})
</script>

<template>
  <div
    class="relative shrink-0 overflow-hidden bg-bone"
    :class="[sizeClass, cover ? '' : 'rounded-lg border border-ink/10 shadow-sm']"
  >
    <img
      v-if="pet.avatar_url"
      :src="pet.avatar_url"
      :alt="`${pet.name} 头像`"
      class="h-full w-full object-cover"
    />
    <div
      v-else
      class="relative grid h-full w-full place-items-center overflow-hidden font-black text-bone"
      :style="{ background: `radial-gradient(circle at 22% 18%, rgba(255,255,255,.28), transparent 26%), linear-gradient(135deg, ${group.accent}, #17211b)` }"
    >
      <div class="absolute inset-0 opacity-20 [background-image:linear-gradient(45deg,rgba(255,255,255,.35)_1px,transparent_1px)] [background-size:14px_14px]"></div>
      {{ initial }}
    </div>
    <span class="absolute bottom-2 right-2 rounded bg-bone/90 px-2 py-1 text-[10px] font-black text-ink shadow-sm">
      {{ group.label }}
    </span>
  </div>
</template>
