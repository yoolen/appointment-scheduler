import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/views/LoginPage.vue'
import Dashboard from '@/views/Dashboard.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    beforeEnter: requireAuth
  }
]

async function requireAuth(to: any, from: any, next: any) {
  try {
    // Check auth status via API call since httpOnly cookies aren't accessible to JS
    const response = await fetch('/api/auth/me', {
      method: 'GET',
      credentials: 'include' // Include httpOnly cookies
    })

    if (response.ok) {
      console.log('Auth guard: user authenticated')
      next()
    } else {
      console.log('Auth guard: user not authenticated, redirecting to login')
      next('/login')
    }
  } catch (error) {
    console.log('Auth guard: error checking auth status, redirecting to login')
    next('/login')
  }
}

export default createRouter({
  history: createWebHistory(),
  routes
})