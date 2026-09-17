<template>
  <div class="login-container">
    <div class="login-box">
      <div class="header">
        <el-icon class="icon"><Connection /></el-icon>
        <h2>MedGraphRAG 医药大数据智能问答系统</h2>
        <p>基于知识图谱与多模态数仓的 Graph RAG 关联分析平台</p>
      </div>
      <el-form :model="form" class="form">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名 (admin / user)" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码 (admin123 / user123)" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-button type="primary" class="submit-btn" :loading="loading" @click="handleLogin">立即登录</el-button>
        <div class="quick-fill">
          <el-link type="primary" @click="quickFill('admin')">填充管理员账号</el-link>
          <el-link type="success" @click="quickFill('user')">填充医师账号</el-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const form = reactive({
  username: 'admin',
  password: 'admin123'
})

const quickFill = (role: 'admin' | 'user') => {
  if (role === 'admin') {
    form.username = 'admin'
    form.password = 'admin123'
  } else {
    form.username = 'user'
    form.password = 'user123'
  }
}

const handleLogin = async () => {
  loading.value = true
  setTimeout(() => {
    userStore.setLogin('mock_jwt_token', form.username, form.username === 'admin' ? ['ROLE_ADMIN', 'ROLE_USER'] : ['ROLE_USER'])
    ElMessage.success('登录成功，进入系统')
    router.push('/dashboard')
    loading.value = false
  }, 400)
}
</script>

<style scoped lang="scss">
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: radial-gradient(circle at center, #102a43 0%, #06111c 100%);
}
.login-box {
  width: 440px;
  background: rgba(16, 42, 67, 0.75);
  border: 1px solid rgba(22, 119, 255, 0.3);
  backdrop-filter: blur(12px);
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
  color: #fff;
  text-align: center;
}
.header .icon {
  font-size: 48px;
  color: #1677ff;
  margin-bottom: 12px;
}
.header h2 {
  font-size: 20px;
  margin-bottom: 8px;
}
.header p {
  font-size: 13px;
  color: #8c8c8c;
  margin-bottom: 28px;
}
.submit-btn {
  width: 100%;
  height: 42px;
  margin-top: 12px;
  font-size: 15px;
}
.quick-fill {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}
</style>
