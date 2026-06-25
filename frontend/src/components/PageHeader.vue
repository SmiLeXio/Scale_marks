<script setup>
defineProps({
  eyebrow: { type: String, default: '' },
  title: { type: String, required: true },
  description: { type: String, default: '' }
})
</script>

<template>
  <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
    <div>
      <p v-if="eyebrow" class="label text-clay">{{ eyebrow }}</p>
      <h1 class="mt-1 text-3xl font-black leading-tight text-ink sm:text-4xl">{{ title }}</h1>
      <p v-if="description" class="mt-2 max-w-2xl text-sm leading-6 text-ink/65">{{ description }}</p>
    </div>
    <slot />
  </div>
</template>
