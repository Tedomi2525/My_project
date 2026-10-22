<script setup lang="ts">
import katex from 'katex'
import 'katex/dist/katex.min.css'

const props = defineProps<{
  content: string
  imageUrl?: string | null
  codeSnippet?: string | null
  codeLanguage?: string | null
}>()

const escapeHtml = (value: string) => value
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')

const renderedContent = computed(() => {
  const source = props.content || ''
  const pattern = /(\$\$[\s\S]+?\$\$|\$[^$\n]+?\$)/g
  let cursor = 0
  let result = ''
  for (const match of source.matchAll(pattern)) {
    const index = match.index || 0
    result += escapeHtml(source.slice(cursor, index)).replaceAll('\n', '<br>')
    const token = match[0]
    const displayMode = token.startsWith('$$')
    const latex = displayMode ? token.slice(2, -2) : token.slice(1, -1)
    try {
      result += katex.renderToString(latex, { displayMode, throwOnError: false })
    } catch {
      result += escapeHtml(token)
    }
    cursor = index + token.length
  }
  result += escapeHtml(source.slice(cursor)).replaceAll('\n', '<br>')
  return result
})
</script>

<template>
  <div class="question-content space-y-4">
    <div class="leading-7 text-slate-900" v-html="renderedContent" />
    <img
      v-if="imageUrl"
      :src="imageUrl"
      alt="Hình minh họa câu hỏi"
      class="max-h-[28rem] max-w-full rounded-xl border border-slate-200 object-contain"
      loading="lazy"
    />
    <div v-if="codeSnippet" class="overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
      <div class="border-b border-slate-800 px-4 py-2 text-xs font-medium uppercase tracking-wide text-slate-400">
        {{ codeLanguage || 'code' }}
      </div>
      <pre class="overflow-x-auto p-4 text-sm leading-6 text-slate-100"><code>{{ codeSnippet }}</code></pre>
    </div>
  </div>
</template>
