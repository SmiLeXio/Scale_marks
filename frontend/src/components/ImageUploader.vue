<script setup>
import { Upload, X } from 'lucide-vue-next'

defineProps({
  modelValue: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

function handleFile(event) {
  const file = event.target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = () => emit('update:modelValue', reader.result)
  reader.readAsDataURL(file)
}
</script>

<template>
  <div class="field-shell">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
      <div class="h-28 w-28 overflow-hidden rounded-lg border border-ink/10 bg-bone">
        <img v-if="modelValue" :src="modelValue" alt="宠物头像预览" class="h-full w-full object-cover" />
        <div v-else class="grid h-full w-full place-items-center text-ink/35">
          <Upload class="h-8 w-8" />
        </div>
      </div>
      <div class="min-w-0 flex-1">
        <p class="label">头像</p>
        <p class="mt-1 text-sm leading-6 text-ink/60">
          上传宠物头像会直接显示在总览和档案卡片中。暂不上传时会按品种生成临时头像。
        </p>
        <div class="mt-3 flex flex-wrap gap-2">
          <label class="btn-secondary cursor-pointer">
            <Upload class="h-4 w-4" />
            选择图片
            <input class="hidden" type="file" accept="image/*" @change="handleFile" />
          </label>
          <button v-if="modelValue" type="button" class="btn-secondary" @click="$emit('update:modelValue', '')">
            <X class="h-4 w-4" />
            移除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
