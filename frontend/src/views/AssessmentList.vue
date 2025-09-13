<template>
  <div class="assessment-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>รายการแบบประเมิน</h3>
          <el-button
            v-if="canManageAssessments"
            type="primary"
            @click="$router.push('/dashboard/create-assessment')"
          >
            <el-icon><Plus /></el-icon>
            สร้างแบบประเมินใหม่
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="assessments"
        style="width: 100%"
        empty-text="ไม่มีข้อมูลแบบประเมิน"
      >
        <el-table-column
          prop="name"
          label="ชื่อแบบประเมิน"
          min-width="200"
        />
        
        <el-table-column
          prop="fiscal_year"
          label="ปีงบประมาณ"
          width="120"
          align="center"
        />
        
        <el-table-column
          prop="status"
          label="สถานะ"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'published' ? 'success' : 'warning'"
              size="small"
            >
              {{ row.status === 'published' ? 'เผยแพร่แล้ว' : 'ร่าง' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column
          prop="created_at"
          label="วันที่สร้าง"
          width="150"
          align="center"
        >
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column
          label="การจัดการ"
          width="250"
          align="center"
        >
          <template #default="{ row }">
            <!-- Fill Data button (all users) -->
            <el-button
              v-if="row.status === 'published'"
              type="primary"
              size="small"
              @click="goToDataEntry(row.id)"
            >
              <el-icon><Edit /></el-icon>
              กรอกข้อมูล
            </el-button>
            
            <!-- Edit button (Admin, Moderator only) -->
            <el-button
              v-if="canManageAssessments"
              type="warning"
              size="small"
              @click="editAssessment(row)"
            >
              <el-icon><EditPen /></el-icon>
              แก้ไข
            </el-button>
            
            <!-- Publish button (Admin, Moderator only) -->
            <el-button
              v-if="canManageAssessments && row.status === 'draft'"
              type="success"
              size="small"
              @click="publishAssessment(row)"
            >
              <el-icon><Upload /></el-icon>
              เผยแพร่
            </el-button>
            
            <!-- Delete button (Admin, Moderator only) -->
            <el-button
              v-if="canManageAssessments"
              type="danger"
              size="small"
              @click="deleteAssessment(row)"
            >
              <el-icon><Delete /></el-icon>
              ลบ
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, EditPen, Upload, Delete } from '@element-plus/icons-vue'

export default {
  name: 'AssessmentList',
  components: {
    Plus,
    Edit,
    EditPen,
    Upload,
    Delete
  },
  setup() {
    const store = useStore()
    const router = useRouter()

    const loading = computed(() => store.getters['assessment/loading'])
    const assessments = computed(() => store.getters['assessment/assessments'])
    const canManageAssessments = computed(() => store.getters['auth/canManageAssessments'])

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleDateString('th-TH', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const goToDataEntry = (assessmentId) => {
      router.push(`/dashboard/data-entry/${assessmentId}`)
    }

    const editAssessment = (assessment) => {
      router.push({
        name: 'CreateAssessment',
        query: { edit: assessment.id }
      })
    }

    const publishAssessment = async (assessment) => {
      try {
        await ElMessageBox.confirm(
          `คุณต้องการเผยแพร่แบบประเมิน "${assessment.name}" ใช่หรือไม่?`,
          'ยืนยันการเผยแพร่',
          {
            confirmButtonText: 'เผยแพร่',
            cancelButtonText: 'ยกเลิก',
            type: 'warning'
          }
        )

        await store.dispatch('assessment/publishAssessment', assessment.id)
        ElMessage.success('เผยแพร่แบบประเมินสำเร็จ')
      } catch (error) {
        if (error !== 'cancel') {
          if (error.response?.data?.details) {
            ElMessage.error({
              message: 'ไม่สามารถเผยแพร่ได้: กรุณากรอกข้อมูลให้ครบถ้วน',
              duration: 5000
            })
          } else {
            ElMessage.error(error.response?.data?.error || 'เกิดข้อผิดพลาดในการเผยแพร่')
          }
        }
      }
    }

    const deleteAssessment = async (assessment) => {
      try {
        await ElMessageBox.confirm(
          `คุณต้องการลบแบบประเมิน "${assessment.name}" ใช่หรือไม่?`,
          'ยืนยันการลบ',
          {
            confirmButtonText: 'ลบ',
            cancelButtonText: 'ยกเลิก',
            type: 'error'
          }
        )

        await store.dispatch('assessment/deleteAssessment', assessment.id)
        ElMessage.success('ลบแบบประเมินสำเร็จ')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(error.response?.data?.error || 'เกิดข้อผิดพลาดในการลบ')
        }
      }
    }

    onMounted(() => {
      store.dispatch('assessment/fetchAssessments')
    })

    return {
      loading,
      assessments,
      canManageAssessments,
      formatDate,
      goToDataEntry,
      editAssessment,
      publishAssessment,
      deleteAssessment
    }
  }
}
</script>

<style scoped>
.assessment-list {
  max-width: 1200px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
}
</style>