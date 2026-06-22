import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

interface User {
  id: number
  username: string
  email: string
  full_name: string | null
  role: string
  company_id: number | null
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  
  async function login(username: string, password: string) {
    try {
      const response = await axios.post('/api/auth/login', {
        username,
        password
      })
      
      const { access_token, user: userData } = response.data
      
      token.value = access_token
      user.value = userData
      
      localStorage.setItem('token', access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Login failed'
      }
    }
  }
  
  async function register(data: {
    username: string
    email: string
    password: string
    full_name?: string
    company_id?: number
  }) {
    try {
      const response = await axios.post('/api/auth/register', data)
      return { success: true, user: response.data }
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Registration failed'
      }
    }
  }
  
  async function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }
  
  async function fetchUser() {
    try {
      const response = await axios.get('/api/auth/me')
      user.value = response.data
    } catch (error) {
      logout()
    }
  }
  
  // Initialize auth state
  if (token.value) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    fetchUser()
  }
  
  return {
    user,
    token,
    isAuthenticated,
    isAdmin,
    login,
    register,
    logout,
    fetchUser
  }
})