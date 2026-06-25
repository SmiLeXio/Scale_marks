<script setup>
defineProps({
  pets: { type: Array, required: true },
  modelValue: { type: String, default: '' }
})

defineEmits(['update:modelValue'])
</script>

<template>
  <label class="block">
    <span class="label">选择宠物</span>
    <select
      class="field mt-1"
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <option v-for="pet in pets" :key="pet.id" :value="pet.id">
        {{ pet.name }} · {{ pet.species }}
      </option>
    </select>
  </label>
</template>
