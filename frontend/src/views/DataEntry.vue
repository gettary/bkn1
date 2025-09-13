<template>
  <div class="data-entry">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <h3>กรอกข้อมูลแบบประเมิน</h3>
          <el-tag v-if="assessment" type="info">{{ assessment.name }}</el-tag>
        </div>
      </template>

      <div v-if="assessment && visibleItems.length > 0">
        <div
          v-for="(item, itemIndex) in visibleItems"
          :key="`item-${itemIndex}`"
          class="assessment-item"
        >
          <el-card class="item-card">
            <template #header>
              <h4>{{ item.title }}</h4>
            </template>

            <div
              v-for="(indicator, indicatorIndex) in item.indicators"
              :key="`indicator-${indicatorIndex}`"
              class="indicator"
            >
              <el-card class="indicator-card">
                <template #header>
                  <h5>{{ indicator.title }}</h5>
                </template>

                <div
                  v-for="(indicatorItem, itemIdx) in indicator.items"
                  :key="`item-${itemIdx}`"
                  class="indicator-item"
                >
                  <div class="item-info">
                    <h6>{{ indicatorItem.title }}</h6>
                    <el-row :gutter="20" class="target-info">
                      <el-col :span="12">
                        <el-text type="info">ค่าเป้าหมาย: {{ indicatorItem.target_value || '-' }}</el-text>
                      </el-col>
                      <el-col :span="12">
                        <el-text type="info">เป้าหมายจริง: {{ indicatorItem.actual_target || '-' }}</el-text>
                      </el-col>
                    </el-row>
                  </div>

                  <el-form
                    :ref="el => setFormRef(`form-${itemIndex}-${indicatorIndex}-${itemIdx}`, el)"
                    :model="userDataMap[indicatorItem.id] || {}"
                    label-position="top"
                    class="data-form"
                  >
                    <el-row :gutter="20">
                      <el-col :span="6">
                        <el-form-item label="ผลงาน">
                          <el-input
                            v-model="userDataMap[indicatorItem.id].performance"
                            placeholder="กรอกผลงาน"
                            type="textarea"
                            :rows="2"
                            @change="updateUserData(indicatorItem.id)"
                          />
                        </el-form-item>
                      </el-col>
                      <el-col :span="6">
                        <el-form-item label="อัตรา">
                          <el-input
                            v-model="userDataMap[indicatorItem.id].rate"
                            placeholder="กรอกอัตรา"
                            @change="updateUserData(indicatorItem.id)"
                          />
                        </el-form-item>
                      </el-col>
                      <el-col :span="6">
                        <el-form-item label="คะแนน">
                          <el-input
                            v-model="userDataMap[indicatorItem.id].score"
                            placeholder="กรอกคะแนน"
                            @change="updateUserData(indicatorItem.id)"
                          />
                        </el-form-item>
                      </el-col>
                      <el-col :span="6">
                        <el-form-item label="อัพโหลดรูปภาพ">
                          <el-upload
                            :action="`/api/user-data/${indicatorItem.id}/upload`"
                            :headers="uploadHeaders"
                            :before-upload="beforeUpload"
                            :on-success="(response) => onUploadSuccess(response, indicatorItem.id)"
                            :on-error="onUploadError"
                            :show-file-list="false"
                            accept="image/*"
                          >
                            <el-button type="primary" size="small">
                              <el-icon><Upload /></el-icon>
                              เลือกไฟล์
                            </el-button>
                          </el-upload>
                          <div v-if="userDataMap[indicatorItem.id].image_path" class="uploaded-image">
                            <el-text type="success" size="small">
                              <el-icon><Check /></el-icon>
                              อัพโหลดสำเร็จ
                            </el-text>
                          </div>
                        </el-form-item>
                      </el-col>
                    </el-row>

                    <div class="form-actions">
                      <el-button
                        @click="saveData(indicatorItem.id, 'draft')"
                        :loading="savingMap[indicatorItem.id]"
                      >
                        บันทึก
                      </el-button>
                      <el-button
                        type="success"
                        @click="submitData(indicatorItem.id)"
                        :loading="submittingMap[indicatorItem.id]"
                      >
                        ส่งข้อมูล
                      </el-button>
                      <el-tag
                        v-if="userDataMap[indicatorItem.id].status"
                        :type="userDataMap[indicatorItem.id].status === 'complete' ? 'success' : 'warning'"
                        size="small"
                      >
                        {{ userDataMap[indicatorItem.id].status === 'complete' ? 'ส่งแล้ว' : 'ร่าง' }}
                      </el-tag>
                    </div>
                  </el-form>
                </div>
              </el-card>
            </div>
          </el-card>
        </div>
      </div>

      <el-empty v-else-if="!loading" description="ไม่มีข้อมูลแบบประเมินที่สามารถกรอกได้" />
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Upload, Check } from '@element-plus/icons-vue'
import { userDataService } from '@/services'

export default {
  name: 'DataEntry',
  components: {
    Upload,
    Check
  },
  props: {
    assessmentId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const store = useStore()
    const route = useRoute()
    
    const loading = ref(false)
    const assessment = ref(null)
    const userDataMap = reactive({})
    const savingMap = reactive({})
    const submittingMap = reactive({})
    const formRefs = reactive({})
    
    const user = computed(() => store.getters['auth/user'])
    const uploadHeaders = computed(() => ({
      Authorization: `Bearer ${localStorage.getItem('token')}`
    }))

    const setFormRef = (key, el) => {
      if (el) {
        formRefs[key] = el
      }
    }

    // Filter items/indicators that user has permission to see
    const visibleItems = computed(() => {
      if (!assessment.value || !user.value) return []
      
      return assessment.value.items.map(item => ({
        ...item,
        indicators: item.indicators.filter(indicator => {
          // Admin and Moderator can see all
          if (user.value.role === 'Admin' || user.value.role === 'Moderator') {
            return true
          }
          
          // Check if user has permission for this indicator
          return indicator.permissions?.some(p => p.user_id === user.value.id && p.can_view)
        })
      })).filter(item => item.indicators.length > 0)
    })

    const loadAssessment = async () => {
      try {
        loading.value = true
        const response = await store.dispatch('assessment/fetchAssessment', props.assessmentId)
        assessment.value = response.assessment
        
        // Initialize user data for all indicator items
        await loadUserData()
      } catch (error) {
        ElMessage.error('ไม่สามารถโหลดข้อมูลแบบประเมินได้')
      } finally {
        loading.value = false
      }
    }

    const loadUserData = async () => {
      const promises = []
      
      visibleItems.value.forEach(item => {
        item.indicators.forEach(indicator => {
          indicator.items.forEach(indicatorItem => {
            promises.push(loadUserDataForItem(indicatorItem.id))
          })
        })
      })
      
      await Promise.all(promises)
    }

    const loadUserDataForItem = async (indicatorItemId) => {
      try {
        const response = await userDataService.getUserData(indicatorItemId)
        userDataMap[indicatorItemId] = response.user_data || {
          performance: '',
          rate: '',
          score: '',
          image_path: '',
          status: 'draft'
        }
      } catch (error) {
        userDataMap[indicatorItemId] = {
          performance: '',
          rate: '',
          score: '',
          image_path: '',
          status: 'draft'
        }
      }
    }

    const updateUserData = (indicatorItemId) => {
      // Auto-save after 1 second of no typing
      clearTimeout(userDataMap[indicatorItemId]?.saveTimeout)
      userDataMap[indicatorItemId].saveTimeout = setTimeout(() => {
        saveData(indicatorItemId, 'draft', false)
      }, 1000)
    }

    const saveData = async (indicatorItemId, status = 'draft', showMessage = true) => {
      try {
        savingMap[indicatorItemId] = true
        
        const data = {
          performance: userDataMap[indicatorItemId].performance,
          rate: userDataMap[indicatorItemId].rate,
          score: userDataMap[indicatorItemId].score,
          status: status
        }
        
        await userDataService.saveUserData(indicatorItemId, data)
        userDataMap[indicatorItemId].status = status
        
        if (showMessage) {
          ElMessage.success('บันทึกข้อมูลสำเร็จ')
        }
      } catch (error) {
        if (showMessage) {
          ElMessage.error(error.response?.data?.error || 'เกิดข้อผิดพลาดในการบันทึก')
        }
      } finally {
        savingMap[indicatorItemId] = false
      }
    }

    const submitData = async (indicatorItemId) => {
      try {
        submittingMap[indicatorItemId] = true
        
        const data = {
          performance: userDataMap[indicatorItemId].performance,
          rate: userDataMap[indicatorItemId].rate,
          score: userDataMap[indicatorItemId].score,
          status: 'complete'
        }
        
        // Validate required fields
        const requiredFields = ['performance', 'rate', 'score']
        const missingFields = requiredFields.filter(field => !data[field] || !data[field].trim())
        
        if (missingFields.length > 0) {
          ElMessage.error('กรุณากรอกข้อมูลให้ครบถ้วน (ผลงาน, อัตรา, คะแนน)')
          return
        }
        
        await userDataService.saveUserData(indicatorItemId, data)
        userDataMap[indicatorItemId].status = 'complete'
        
        ElMessage.success('ส่งข้อมูลสำเร็จ')
      } catch (error) {
        ElMessage.error(error.response?.data?.error || 'เกิดข้อผิดพลาดในการส่งข้อมูล')
      } finally {
        submittingMap[indicatorItemId] = false
      }
    }

    const beforeUpload = (file) => {
      const isImage = file.type.startsWith('image/')
      const isLt2M = file.size / 1024 / 1024 < 2

      if (!isImage) {
        ElMessage.error('กรุณาเลือกไฟล์รูปภาพเท่านั้น!')
        return false
      }
      
      if (!isLt2M) {
        ElMessage.error('ขนาดไฟล์ต้องไม่เกิน 2MB!')
        return false
      }
      
      return true
    }

    const onUploadSuccess = (response, indicatorItemId) => {
      userDataMap[indicatorItemId].image_path = response.image_path
      ElMessage.success('อัพโหลดรูปภาพสำเร็จ')
    }

    const onUploadError = (error) => {
      ElMessage.error('เกิดข้อผิดพลาดในการอัพโหลดรูปภาพ')
    }

    onMounted(() => {
      loadAssessment()
    })

    return {
      loading,
      assessment,
      visibleItems,
      userDataMap,
      savingMap,
      submittingMap,
      uploadHeaders,
      setFormRef,
      updateUserData,
      saveData,
      submitData,
      beforeUpload,
      onUploadSuccess,
      onUploadError
    }
  }
}
</script>

<style scoped>
.data-entry {
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

.assessment-item {
  margin-bottom: 20px;
}

.item-card {
  border-left: 4px solid #409eff;
}

.indicator {
  margin-bottom: 15px;
}

.indicator-card {
  border-left: 4px solid #67c23a;
  margin-left: 20px;
}

.indicator-item {
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  margin-bottom: 15px;
  background-color: #fafafa;
}

.item-info {
  margin-bottom: 20px;
}

.item-info h6 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
}

.target-info {
  margin-top: 10px;
}

.data-form {
  background: white;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #dcdfe6;
}

.form-actions {
  margin-top: 15px;
  text-align: right;
}

.form-actions .el-button {
  margin-left: 10px;
}

.uploaded-image {
  margin-top: 8px;
}
</style>