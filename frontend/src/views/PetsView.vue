<script setup>
import { Plus } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import EmptyState from '../components/EmptyState.vue'
import PageHeader from '../components/PageHeader.vue'
import PetCard from '../components/PetCard.vue'
import { usePetsStore } from '../stores/pets'

const router = useRouter()
const petsStore = usePetsStore()

async function removePet(id) {
  await petsStore.removePet(id)
}

function editPet(id) {
  router.push(`/pets/${id}/edit`)
}
</script>

<template>
  <section class="px-4 py-6 sm:px-6 lg:px-8">
    <PageHeader
      eyebrow="Pets"
      title="宠物档案"
      description="在这里管理档案，支持新增、编辑和删除。新增入口保留在右下角。"
    />

    <EmptyState
      v-if="!petsStore.pets.length"
      title="还没有宠物档案"
      description="创建第一份档案后，这里会展示头像、品种、体重体长和喂食周期。"
    >
      <RouterLink class="btn-primary" to="/pets/new">创建第一份档案</RouterLink>
    </EmptyState>

    <div v-else class="grid gap-4 xl:grid-cols-2">
      <PetCard v-for="pet in petsStore.pets" :key="pet.id" :pet="pet" @delete="removePet" @edit="editPet" />
    </div>

    <RouterLink
      class="fixed bottom-24 right-5 z-20 grid h-14 w-14 place-items-center rounded-full bg-ink text-bone shadow-soft transition hover:bg-moss lg:bottom-8"
      to="/pets/new"
      aria-label="新增档案"
    >
      <Plus class="h-6 w-6" />
    </RouterLink>
  </section>
</template>
