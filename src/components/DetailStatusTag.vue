<template>
  <el-tag :type="type" :effect="effect">
    {{ text }}
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { DetailStatus } from '@/types/detail'

const props = defineProps<{
  status: number
  effect?: 'light' | 'dark' | 'plain'
}>()

const type = computed(() => {
  const types: Record<number, '' | 'success' | 'warning' | 'danger'> = {
    [DetailStatus.PENDING]: '',        // 待处理
    [DetailStatus.ORDERED]: 'warning', // 已下单
    [DetailStatus.REVIEWED]: 'success',// 已评价
    [DetailStatus.CANCELLED]: 'danger' // 已取消
  }
  return types[props.status] || ''
})

const text = computed(() => {
  const texts: Record<number, string> = {
    [DetailStatus.PENDING]: '待处理',
    [DetailStatus.ORDERED]: '已下单',
    [DetailStatus.REVIEWED]: '已评价',
    [DetailStatus.CANCELLED]: '已取消'
  }
  return texts[props.status] || '未知'
})
</script> 