<template>
  <div class="dashboard-container">
    <!-- Sidebar -->
    <el-aside :width="sidebarWidth" class="sidebar">
      <div class="logo">
        <h3 v-if="!isCollapsed">BKN1 Assessment</h3>
        <h3 v-else>BKN11111</h3>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :router="true"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        @select="handleMenuSelect"
      >
        <!-- Create Assessment (Admin, Moderator only) -->
        <el-menu-item 
          v-if="canManageAssessments" 
          index="/dashboard/create-assessment"
        >
          <el-icon><DocumentAdd /></el-icon>
          <template #title>สร้างแบบประเมิน</template>
        </el-menu-item>
        
        <!-- Assessment List -->
        <el-menu-item index="/dashboard/assessments">
          <el-icon><Document /></el-icon>
          <template #title>รายการแบบประเมิน</template>
        </el-menu-item>
        
        <!-- Summary Report -->
        <el-menu-item index="/dashboard/summary-report">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>สรุปรายงาน</template>
        </el-menu-item>
      </el-menu>
      
      <!-- Sidebar toggle button -->
      <div class="sidebar-toggle">
        <el-button
          type="text"
          @click="toggleSidebar"
          class="toggle-btn"
        >
          <el-icon>
            <Expand v-if="isCollapsed" />
            <Fold v-else />
          </el-icon>
        </el-button>
      </div>
    </el-aside>
    
    <!-- Main content area -->
    <el-container class="main-container">
      <!-- Header -->
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">หน้าหลัก</el-breadcrumb-item>
            <el-breadcrumb-item v-if="breadcrumbTitle">{{ breadcrumbTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleUserAction">
            <span class="user-info">
              <el-icon><Avatar /></el-icon>
              {{ user?.full_name || 'ผู้ใช้งาน' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  ข้อมูลส่วนตัว
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  ออกจากระบบ
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- Content -->
      <el-main class="content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  DocumentAdd,
  Document,
  DataAnalysis,
  Expand,
  Fold,
  Avatar,
  ArrowDown,
  User,
  SwitchButton
} from '@element-plus/icons-vue'

export default {
  name: 'Dashboard',
  components: {
    DocumentAdd,
    Document,
    DataAnalysis,
    Expand,
    Fold,
    Avatar,
    ArrowDown,
    User,
    SwitchButton
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    const isCollapsed = ref(false)
    const activeMenu = ref(route.path)
    
    const user = computed(() => store.getters['auth/user'])
    const canManageAssessments = computed(() => store.getters['auth/canManageAssessments'])
    
    const sidebarWidth = computed(() => isCollapsed.value ? '64px' : '200px')
    
    const breadcrumbTitle = computed(() => {
      const routeMap = {
        '/dashboard/create-assessment': 'สร้างแบบประเมิน',
        '/dashboard/assessments': 'รายการแบบประเมิน',
        '/dashboard/summary-report': 'สรุปรายงาน'
      }
      return routeMap[route.path] || ''
    })
    
    // Watch route changes to update active menu
    watch(() => route.path, (newPath) => {
      activeMenu.value = newPath
    })
    
    const toggleSidebar = () => {
      isCollapsed.value = !isCollapsed.value
    }
    
    const handleMenuSelect = (index) => {
      activeMenu.value = index
    }
    
    const handleUserAction = async (command) => {
      if (command === 'logout') {
        try {
          await ElMessageBox.confirm(
            'คุณต้องการออกจากระบบใช่หรือไม่?',
            'ยืนยันการออกจากระบบ',
            {
              confirmButtonText: 'ออกจากระบบ',
              cancelButtonText: 'ยกเลิก',
              type: 'warning'
            }
          )
          
          store.dispatch('auth/logout')
          ElMessage.success('ออกจากระบบสำเร็จ')
          router.push('/login')
        } catch (error) {
          // User cancelled
        }
      } else if (command === 'profile') {
        ElMessage.info('ฟีเจอร์ข้อมูลส่วนตัวยังไม่เปิดให้บริการ')
      }
    }    
    
    return {
      isCollapsed,
      activeMenu,
      user,
      canManageAssessments,
      sidebarWidth,
      breadcrumbTitle,
      toggleSidebar,
      handleMenuSelect,
      handleUserAction
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  display: flex;
  height: 100vh;
}

.sidebar {
  position: relative;
  background-color: #304156;
  transition: width 0.3s;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #434343;
}

.logo h3 {
  color: #bfcbd9;
  margin: 0;
  font-size: 18px;
}

.sidebar-toggle {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  text-align: center;
}

.toggle-btn {
  color: #bfcbd9 !important;
  background: none !important;
  border: none !important;
  font-size: 18px;
}

.toggle-btn:hover {
  color: #409eff !important;
}

.main-container {
  flex: 1;
  background-color: #f0f2f5;
}

.header {
  background-color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #666;
  font-size: 14px;
}

.user-info .el-icon {
  margin: 0 5px;
}

.content {
  padding: 20px;
  background-color: #f0f2f5;
  overflow-y: auto;
}
</style>