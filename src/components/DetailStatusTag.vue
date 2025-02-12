<template>
  <el-tag :type="type" :effect="effect">{{ text }}</el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: number
  effect?: 'light' | 'dark' | 'plain'
}>()

const type = computed(() => {
  const types: Record<number, '' | 'warning' | 'success'> = {
    1: '',        // 待评论
    2: 'warning', // 已评论
    3: 'success'  // 已完成
  }
  return types[props.status] || ''
})

const text = computed(() => {
  const texts: Record<number, string> = {
    1: '待评论',
    2: '已评论',
    3: '已完成'
  }
  return texts[props.status] || '未知'
})
</script> 