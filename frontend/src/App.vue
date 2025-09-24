<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// Router outlet only
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f5f5f5;
}

#app {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

header {
  text-align: center;
  margin-bottom: 40px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

header p {
  color: #666;
}

.api-status {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}

.status-ok {
  color: #27ae60;
  font-weight: bold;
}

.status-error {
  color: #e74c3c;
  font-weight: bold;
}

.coming-soon {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  text-align: center;
}

.coming-soon ul {
  list-style: none;
  margin-top: 20px;
}

.coming-soon li {
  padding: 5px 0;
}
</style>