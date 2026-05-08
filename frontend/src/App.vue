<template>
  <div class="app">
    <header class="header">
      <h1>中证红利相对国证A股</h1>
      <h2 class="subtitle2">轮动三棱镜</h2>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #333;
}

.app {
  min-height: 100vh;
}

.header {
  background: #1a3a6b;
  color: white;
  padding: 24px 32px;
  text-align: center;
}

.header h1 {
  font-size: 24px;
  font-weight: 600;
}

.header .subtitle2 {
  font-size: 20px;
  font-weight: 400;
  color: #e63946;
  margin-top: 4px;
}
</style>
