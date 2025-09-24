<template>
  <div class="login-container">
    <div class="login-card">
      <!-- Show logout option if user is already logged in -->
      <div v-if="isLoggedIn" class="logout-section">
        <h1>Already Signed In</h1>
        <p>You are already logged in to your account.</p>
        <button @click="goToDashboard" class="dashboard-button">
          Go to Dashboard
        </button>
        <button @click="handleLogout" class="logout-button">
          Sign Out
        </button>
      </div>

      <!-- Regular login form (show only if not logged in) -->
      <div v-else>
        <h1>Appointment Scheduler</h1>
        <p>Sign in to your account</p>

        <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            placeholder="Enter your email"
          />
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            placeholder="Enter your password"
          />
        </div>
        
        <button type="submit" :disabled="isLoading" class="login-button">
          {{ isLoading ? 'Signing in...' : 'Sign In' }}
        </button>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const email = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')
const isLoggedIn = ref(false)

const handleLogin = async () => {
  isLoading.value = true
  error.value = ''
  
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Important for cookies
      body: JSON.stringify({
        email: email.value,
        password: password.value,
      }),
    })
    
    if (response.ok) {
      // Login successful, redirect to dashboard
      console.log('Login successful, redirecting...')
      await router.push('/')
      console.log('Redirect complete')
    } else {
      const data = await response.json()
      error.value = data.detail || 'Login failed'
    }
  } catch (err) {
    error.value = 'Network error. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const handleLogout = async () => {
  try {
    await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include'
    })
    isLoggedIn.value = false
    error.value = ''
  } catch (err) {
    console.error('Logout failed:', err)
    error.value = 'Logout failed. Please try again.'
  }
}

const goToDashboard = () => {
  router.push('/')
}

// Check if user is already logged in when component mounts
onMounted(async () => {
  try {
    const response = await fetch('/api/auth/me', { credentials: 'include' })
    isLoggedIn.value = response.ok
  } catch (err) {
    isLoggedIn.value = false
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  padding: 20px;
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.login-card h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.login-card p {
  color: #666;
  margin-bottom: 30px;
}

.login-form {
  text-align: left;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #333;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
}

.login-button {
  width: 100%;
  padding: 12px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-button:hover:not(:disabled) {
  background-color: #2980b9;
}

.login-button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.error-message {
  margin-top: 15px;
  padding: 10px;
  background-color: #fee;
  color: #e74c3c;
  border-radius: 4px;
  text-align: center;
}

.logout-section {
  text-align: center;
}

.logout-section h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.logout-section p {
  color: #666;
  margin-bottom: 30px;
}

.dashboard-button {
  width: 100%;
  padding: 12px;
  background-color: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-bottom: 10px;
}

.dashboard-button:hover {
  background-color: #219a52;
}

.logout-button {
  width: 100%;
  padding: 12px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-button:hover {
  background-color: #c0392b;
}
</style>