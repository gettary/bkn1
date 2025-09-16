<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2>Welcome to BUENGKAN HOSPITAL KPI System</h2>
        </div>
      </template>
      
      <el-form
        ref="loginForm"
        :model="loginData"
        :rules="rules"
        @submit.prevent="handleLogin"
        label-position="top"
      >
        <el-form-item label="ชื่อผู้ใช้" prop="username">
          <el-input
            v-model="loginData.username"
            placeholder="กรุณากรอกชื่อผู้ใช้"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item label="รหัสผ่าน" prop="password">
          <el-input
            v-model="loginData.password"
            type="password"
            placeholder="กรุณากรอกรหัสผ่าน"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
          >
            เข้าสู่ระบบ
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- Demo users info -->
      <el-divider />
      <div class="demo-users">
        <h4>ผู้ใช้งานตัวอย่าง:</h4>
        <p><strong>Admin:</strong> admin / admin123</p>
        <p><strong>Moderator:</strong> moderator / admin123</p>
        <p><strong>User:</strong> user1 / admin123</p>
      </div>
    </el-card>
  </div>
</template>

<script>
import { reactive, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

export default {
  name: 'Login',
  setup() {
    const store = useStore()
    const router = useRouter()
    const loginForm = ref()
    const loading = ref(false)

    const loginData = reactive({
      username: '',
      password: ''
    })

    const rules = {
      username: [
        { required: true, message: 'กรุณากรอกชื่อผู้ใช้', trigger: 'blur' }
      ],
      password: [
        { required: true, message: 'กรุณากรอกรหัสผ่าน', trigger: 'blur' }
      ]
    }

    const handleLogin = async () => {
      try {
        const valid = await loginForm.value.validate()
        if (!valid) return

        loading.value = true
        await store.dispatch('auth/login', {
          username: loginData.username,
          password: loginData.password
        })

        ElMessage.success('เข้าสู่ระบบสำเร็จ')
        router.push('/dashboard')
      } catch (error) {        
        ElMessage.error(error.response?.data?.error || 'เกิดข้อผิดพลาดในการเข้าสู่ระบบ')
      } finally {
        loading.value = false
      }
    }

    return {
      loginData,
      rules,
      loading,
      loginForm,
      handleLogin,
      User,
      Lock
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 400px;
  max-width: 100%;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  color: #409eff;
  margin: 0;
}

.demo-users {
  text-align: center;
  color: #666;
  font-size: 14px;
}

.demo-users h4 {
  margin-bottom: 10px;
  color: #409eff;
}

.demo-users p {
  margin: 5px 0;
}
</style>