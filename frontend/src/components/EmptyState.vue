<script setup>
import { Archive } from 'lucide-vue-next'

defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' }
})
</script>

<template>
  <div class="panel rounded-lg p-8 text-center">
    <Archive class="mx-auto h-9 w-9 text-ink/35" />
    <h2 class="mt-3 text-lg font-black">{{ title }}</h2>
    <p class="mx-auto mt-2 max-w-md text-sm leading-6 text-ink/60">{{ description }}</p>
    <div class="mt-5">
      <slot />
    </div>
  </div>
</template>
