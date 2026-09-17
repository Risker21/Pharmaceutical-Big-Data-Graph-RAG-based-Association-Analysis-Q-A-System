import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    username: localStorage.getItem('username') || 'admin',
    roles: JSON.parse(localStorage.getItem('roles') || '["ROLE_ADMIN","ROLE_USER"]')
  }),
  actions: {
    setLogin(token: string, username: string, roles: string[]) {
      this.token = token
      this.username = username
      this.roles = roles
      localStorage.setItem('token', token)
      localStorage.setItem('username', username)
      localStorage.setItem('roles', JSON.stringify(roles))
    },
    logout() {
      this.token = ''
      this.username = ''
      this.roles = []
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('roles')
    }
  }
})
