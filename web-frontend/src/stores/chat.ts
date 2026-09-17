import { defineStore } from 'pinia'

export const useChatStore = defineStore('chat', {
  state: () => ({
    prefilledQuery: '',
    currentSessionId: 'sess_' + Date.now(),
    historySessions: [
      { id: 'sess_1', title: '高血压合并干咳用药咨询', date: '2026-09-15 18:30' },
      { id: 'sess_2', title: '华法林与阿司匹林配伍禁忌', date: '2026-09-15 17:45' },
      { id: 'sess_3', title: '左氧氟沙星与茶碱代谢冲突', date: '2026-09-15 15:20' }
    ]
  }),
  actions: {
    setPrefilledQuery(q: string) {
      this.prefilledQuery = q
    },
    clearPrefilledQuery() {
      this.prefilledQuery = ''
    }
  }
})
