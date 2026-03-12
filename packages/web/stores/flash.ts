export const useFlashStore = defineStore('flash', {
  state: () => ({
    messages: [] as Array<{ text: string; category: string }>,
  }),
  actions: {
    add(text: string, category: 'success' | 'danger' | 'warning' | 'info' = 'info') {
      this.messages.push({ text, category: category === 'error' ? 'danger' : category })
    },
    dismiss(index: number) {
      this.messages.splice(index, 1)
    },
    clear() {
      this.messages = []
    },
  },
})
