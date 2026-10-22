<script setup lang="ts">
import { Bell } from 'lucide-vue-next'
const config=useRuntimeConfig(); const token=useCookie<string|null>('token'); const {user}=useAuth()
const items=ref<any[]>([]); const open=ref(false); let refreshTimer: ReturnType<typeof setInterval> | null = null; const unread=computed(()=>items.value.filter(x=>!x.is_read).length)
const headers=computed(()=>({Authorization:`Bearer ${token.value}`,'x-user-id':String(user.value?.id||''),'x-user-role':String(user.value?.role||'')}))
const load=async()=>{ if(!user.value||!token.value)return; try{items.value=await $fetch('/notifications',{baseURL:config.public.apiBase,headers:headers.value}) as any[]}catch{} }
const read=async(n:any)=>{if(!n.is_read){await $fetch(`/notifications/${n.id}/read`,{method:'PATCH',baseURL:config.public.apiBase,headers:headers.value});n.is_read=true}}
onMounted(()=>{load();refreshTimer=setInterval(load,60000)}); onUnmounted(()=>{if(refreshTimer)clearInterval(refreshTimer)})
</script>
<template><div class="relative"><button class="btn-secondary relative" @click="open=!open"><Bell class="w-5 h-5"/><span v-if="unread" class="absolute -top-2 -right-2 rounded-full bg-red-500 px-1.5 text-xs text-white">{{unread}}</span></button><div v-if="open" class="absolute right-0 mt-2 w-80 max-h-96 overflow-auto rounded-xl border bg-white p-2 shadow-xl z-50"><p class="px-3 py-2 font-semibold">Thông báo</p><button v-for="n in items" :key="n.id" @click="read(n)" class="block w-full rounded-lg p-3 text-left hover:bg-slate-50" :class="!n.is_read?'bg-blue-50':''"><span class="block text-sm font-medium">{{n.title}}</span><span class="block text-xs text-slate-500">{{n.message}}</span></button><p v-if="!items.length" class="p-4 text-sm text-slate-500">Chưa có thông báo.</p></div></div></template>