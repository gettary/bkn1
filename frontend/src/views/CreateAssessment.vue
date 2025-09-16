<template>
  <div class="create-assessment">
    <el-card>
      <template #header>
        <h3>{{ isEdit ? 'แก้ไขแบบประเมิน' : 'สร้างแบบประเมิน' }}</h3>
      </template>

      <el-form
        ref="assessmentForm"
        :model="formData"
        :rules="rules"
        label-position="top"
        @submit.prevent
      >
        <!-- Fiscal Year -->
        <el-form-item label="ปีงบประมาณ" prop="fiscal_year">
          <el-select
            v-model="formData.fiscal_year"
            placeholder="เลือกปีงบประมาณ"
            style="width: 200px"
          >
            <el-option
              v-for="year in fiscalYears"
              :key="year"
              :label="year"
              :value="year"
            />
          </el-select>
        </el-form-item>

        <!-- Assessment Items (ประเด็น) -->
        <div class="section-header">
          <h4>รายการประเด็น</h4>
          <el-button type="primary" @click="addAssessmentItem">
            <el-icon><Plus /></el-icon>
            เพิ่มประเด็น
          </el-button>
        </div>

        <div
          v-for="(item, itemIndex) in formData.items"
          :key="`item-${itemIndex}`"
          class="assessment-item"
        >
          <el-card class="item-card">
            <template #header>
              <div class="item-header">
                <span>ประเด็นที่ {{ itemIndex + 1 }}</span>
                <el-button
                  type="danger"
                  size="small"
                  @click="removeAssessmentItem(itemIndex)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </template>

            <!-- Item Title -->
            <el-form-item :label="`ประเด็น ${itemIndex + 1}`">
              <el-input
                v-model="item.title"
                placeholder="กรอกหัวข้อประเด็น"
              />
            </el-form-item>

            <!-- Indicators (ตัวชี้วัด) -->
            <div class="indicators-section">
              <div class="subsection-header">
                <h5>ตัวชี้วัด</h5>
                <el-button
                  type="success"
                  size="small"
                  @click="addIndicator(itemIndex)"
                >
                  <el-icon><Plus /></el-icon>
                  เพิ่มตัวชี้วัด
                </el-button>
              </div>

              <div
                v-for="(indicator, indicatorIndex) in item.indicators"
                :key="`indicator-${itemIndex}-${indicatorIndex}`"
                class="indicator"
              >
                <el-card class="indicator-card">
                  <template #header>
                    <div class="indicator-header">
                      <span>ตัวชี้วัดที่ {{ indicatorIndex + 1 }}</span>
                      <el-button
                        type="danger"
                        size="small"
                        @click="removeIndicator(itemIndex, indicatorIndex)"
                      >
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </template>

                  <!-- Indicator Title -->
                  <el-form-item :label="`ตัวชี้วัด ${indicatorIndex + 1}`">
                    <el-input
                      v-model="indicator.title"
                      placeholder="กรอกหัวข้อตัวชี้วัด"
                    />
                  </el-form-item>

                  <!-- User Permissions -->
                  <el-form-item label="สิทธิการเข้าถึงข้อมูล">
                    <el-select
                      v-model="indicator.selectedUsers"
                      multiple
                      placeholder="เลือกผู้ใช้ที่สามารถเข้าถึงข้อมูลได้"
                      style="width: 100%"
                    >
                      <el-option
                        v-for="user in allUsers"
                        :key="user.id"
                        :label="user.full_name"
                        :value="user.id"
                      />
                    </el-select>
                  </el-form-item>

                  <!-- Indicator Items (รายการตัวชี้วัด) -->
                  <div class="indicator-items-section">
                    <div class="subsection-header">
                      <h6>รายการตัวชี้วัด</h6>
                      <el-button
                        type="info"
                        size="small"
                        @click="addIndicatorItem(itemIndex, indicatorIndex)"
                      >
                        <el-icon><Plus /></el-icon>
                        เพิ่มรายการ
                      </el-button>
                    </div>

                    <div
                      v-for="(indicatorItem, itemIdx) in indicator.items"
                      :key="`indicator-item-${itemIndex}-${indicatorIndex}-${itemIdx}`"
                      class="indicator-item"
                    >
                      <div class="indicator-item-header">
                        <span>รายการที่ {{ itemIdx + 1 }}</span>
                        <el-button
                          type="danger"
                          size="small"
                          @click="removeIndicatorItem(itemIndex, indicatorIndex, itemIdx)"
                        >
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </div>

                      <el-row :gutter="20">
                        <el-col :span="8">
                          <el-form-item label="รายการตัวชี้วัด">
                            <el-input
                              v-model="indicatorItem.title"
                              placeholder="กรอกรายการตัวชี้วัด"
                            />
                          </el-form-item>
                        </el-col>
                        <el-col :span="8">
                          <el-form-item label="ค่าเป้าหมาย">
                            <el-input
                              v-model="indicatorItem.target_value"
                              placeholder="กรอกค่าเป้าหมาย"
                            />
                          </el-form-item>
                        </el-col>
                        <el-col :span="8">
                          <el-form-item label="เป้าหมายจริง">
                            <el-input
                              v-model="indicatorItem.actual_target"
                              placeholder="กรอกเป้าหมายจริง"
                            />
                          </el-form-item>
                        </el-col>
                      </el-row>
                    </div>
                  </div>
                </el-card>
              </div>
            </div>
          </el-card>
        </div>

        <!-- Action Buttons -->
        <div class="action-buttons">
          <el-button @click="clearForm">ยกเลิก</el-button>
          <el-button type="warning" :loading="saving" @click="saveAsDraft">
            บันทึก
          </el-button>
          <el-button type="success" :loading="publishing" @click="publish">
            เผยแพร่
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { authService } from '@/services'

export default {
  name: 'CreateAssessment',
  components: {
    Plus,
    Delete
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    const assessmentForm = ref()
    const saving = ref(false)
    const publishing = ref(false)
    const allUsers = ref([])
    const isEdit = computed(() => !!route.query.edit)

    // Generate fiscal years (Buddhist calendar)
    const currentYear = new Date().getFullYear() + 543 // Convert to Buddhist year
    const fiscalYears = Array.from({ length: 7 }, (_, i) => currentYear - 3 + i)

    const formData = reactive({
      fiscal_year: currentYear,
      items: []
    })

    const rules = {
      fiscal_year: [
        { required: true, message: 'กรุณาเลือกปีงบประมาณ', trigger: 'change' }
      ]
    }

    const addAssessmentItem = () => {
      formData.items.push({
        title: '',
        indicators: []
      })
    }

    const removeAssessmentItem = (index) => {
      formData.items.splice(index, 1)
    }

    const addIndicator = (itemIndex) => {
      formData.items[itemIndex].indicators.push({
        title: '',
        selectedUsers: [],
        items: []
      })
      console.log('Indicators after adding:', formData.items[itemIndex].indicators) // Debugging indicators
    }

    const removeIndicator = (itemIndex, indicatorIndex) => {
      formData.items[itemIndex].indicators.splice(indicatorIndex, 1)
    }

    const addIndicatorItem = (itemIndex, indicatorIndex) => {
      formData.items[itemIndex].indicators[indicatorIndex].items.push({
        title: '',
        target_value: '',
        actual_target: ''
      })
    }

    const removeIndicatorItem = (itemIndex, indicatorIndex, itemIdx) => {
      formData.items[itemIndex].indicators[indicatorIndex].items.splice(itemIdx, 1)
    }

    const validateForm = () => {
      const errors = []
      
      if (!formData.fiscal_year) {
        errors.push('กรุณาเลือกปีงบประมาณ')
      }

      formData.items.forEach((item, itemIndex) => {
        if (!item.title.trim()) {
          errors.push(`กรุณากรอกหัวข้อประเด็นที่ ${itemIndex + 1}`)
        }
        
        item.indicators.forEach((indicator, indicatorIndex) => {
          if (!indicator.title.trim()) {
            errors.push(`กรุณากรอกหัวข้อตัวชี้วัดที่ ${indicatorIndex + 1} ของประเด็นที่ ${itemIndex + 1}`)
          }
          
          indicator.items.forEach((indicatorItem, itemIdx) => {
            if (!indicatorItem.title.trim()) {
              errors.push(`กรุณากรอกรายการตัวชี้วัดที่ ${itemIdx + 1} ของตัวชี้วัดที่ ${indicatorIndex + 1}`)
            }
          })
        })
      })

      return errors
    }

    const prepareFormData = () => {
      const data = {
        fiscal_year: formData.fiscal_year,
        items: formData.items.map((item, itemIndex) => ({
          title: item.title || 'Untitled',
          order_index: itemIndex,
          indicators: item.indicators
            .filter(indicator => indicator.title.trim() !== '')
            .map((indicator, indicatorIndex) => ({
              title: indicator.title,
              order_index: indicatorIndex,
              assessment_item_id: item.id, // Pass assessment_item_id to backend
              permissions: indicator.selectedUsers.map(userId => ({
                user_id: userId,
                can_view: true,
                can_edit: true
              })),
              items: indicator.items.map((indicatorItem, itemIdx) => ({
                title: indicatorItem.title || 'Untitled Item',
                target_value: indicatorItem.target_value || '',
                actual_target: indicatorItem.actual_target || '',
                order_index: itemIdx
              }))
            }))
        }))
      }
      console.log('Prepared data for API:', JSON.stringify(data, null, 2)) // Debugging prepared data
      return data
    }

    const saveAsDraft = async () => {
      try {
        saving.value = true
        const assessmentData = prepareFormData()
        console.log('Prepared assessment data:', assessmentData) // Debugging prepared data

        const response = isEdit.value
          ? await store.dispatch('assessment/updateAssessment', {
              id: route.query.edit,
              assessment: assessmentData
            })
          : await store.dispatch('assessment/createAssessment', assessmentData)

        console.log('Response from API:', response) // Debugging API response
      } catch (error) {
        console.error('Error saving assessment:', error)
        ElMessage.error(error.response?.data?.error || 'เกิดข้อผิดพลาดในการบันทึก')
      } finally {
        saving.value = false
      }
    }

    const publish = async () => {
      try {
        const errors = validateForm()
        if (errors.length > 0) {
          ElMessage.error({
            message: `กรุณาตรวจสอบข้อมูล:\n${errors.join('\n')}`,
            duration: 5000
          })
          return
        }

        publishing.value = true
        const assessmentData = prepareFormData()

        if (isEdit.value) {
          await store.dispatch('assessment/updateAssessment', {
            id: route.query.edit,
            assessment: { ...assessmentData, status: 'published' }
          })
          ElMessage.success('เผยแพร่แบบประเมินสำเร็จ')
          router.push('/dashboard/assessments')
        } else {
          const response = await store.dispatch('assessment/createAssessment', assessmentData)
          console.log('Create response:', response) // Debugging response from createAssessment

          if (response && response.id) {
            const publishResponse = await store.dispatch('assessment/publishAssessment', response.id)
            console.log('Publish response:', publishResponse) // Debugging response from publishAssessment
            ElMessage.success('เผยแพร่แบบประเมินสำเร็จ')
            router.push('/dashboard/assessments')
          } else {
            console.error('Invalid assessment object:', response)
            ElMessage.error('ไม่สามารถเผยแพร่แบบประเมินได้: ข้อมูลไม่สมบูรณ์')
          }
        }
      } catch (error) {
        console.error('Error publishing assessment:', error)
        ElMessage.error(error.response?.data?.error || 'เกิดข้อผิดพลาดในการเผยแพร่แบบประเมิน')
      } finally {
        publishing.value = false
      }
    }

    const clearForm = async () => {
      try {
        await ElMessageBox.confirm(
          'คุณต้องการยกเลิกการสร้างแบบประเมินใช่หรือไม่?',
          'ยืนยันการยกเลิก',
          {
            confirmButtonText: 'ยกเลิก',
            cancelButtonText: 'กลับไป',
            type: 'warning'
          }
        )
        
        // Clear form data
        formData.fiscal_year = currentYear
        formData.items = []
        
        ElMessage.success('ยกเลิกการสร้างแบบประเมินสำเร็จ')
        router.push('/dashboard/assessments')
      } catch (error) {
        // User cancelled
      }
    }

    const loadUsers = async () => {
      try {
        const response = await authService.getUsers()
        console.log('Response from getUsers:', response) // Debugging API response
        if (!Array.isArray(response) || !response[0] || !response[0].users) {
          console.error('Invalid response structure:', response)
          return
        }
        allUsers.value = response[0].users.filter(user => user.role === 'User')
        console.log('Filtered Users:', allUsers.value) // Debugging filtered users
      } catch (error) {
        console.error('Error loading users:', error)
      }
    }

    const loadAssessmentForEdit = async () => {
      if (isEdit.value) {
        try {
          const response = await store.dispatch('assessment/fetchAssessment', route.query.edit)
          const assessment = response.assessment
          console.log('Assessment data:', assessment) // Debugging assessment data

          formData.fiscal_year = assessment.fiscal_year
          formData.items = assessment.items.map(item => ({
            title: item.title,
            indicators: item.indicators.map(indicator => ({
              title: indicator.title,
              selectedUsers: indicator.permissions?.map(p => p.user_id) || [],
              items: indicator.items.map(indicatorItem => ({
                title: indicatorItem.title,
                target_value: indicatorItem.target_value || '',
                actual_target: indicatorItem.actual_target || ''
              }))
            }))
          }))
          console.log('Updated formData:', JSON.stringify(formData, null, 2)) // Debugging updated formData
        } catch (error) {
          console.error('Error loading assessment for edit:', error)
          ElMessage.error('ไม่สามารถโหลดข้อมูลแบบประเมินได้')
          router.push('/dashboard/assessments')
        }
      }
    }

    onMounted(() => {
      loadUsers()
      loadAssessmentForEdit()
      
      // Add initial item if creating new
      if (!isEdit.value) {
        addAssessmentItem()
      }
    })

    return {
      assessmentForm,
      saving,
      publishing,
      allUsers,
      isEdit,
      fiscalYears,
      formData,
      rules,
      addAssessmentItem,
      removeAssessmentItem,
      addIndicator,
      removeIndicator,
      addIndicatorItem,
      removeIndicatorItem,
      saveAsDraft,
      publish,
      clearForm
    }
  }
}
</script>

<style scoped>
.create-assessment {
  max-width: 1200px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0 10px 0;
}

.section-header h4 {
  margin: 0;
  color: #303133;
}

.subsection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px 0;
}

.subsection-header h5,
.subsection-header h6 {
  margin: 0;
  color: #606266;
}

.assessment-item {
  margin-bottom: 20px;
}

.item-card {
  border-left: 4px solid #409eff;
}

.item-header,
.indicator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.indicators-section {
  margin-top: 15px;
}

.indicator {
  margin-bottom: 15px;
}

.indicator-card {
  border-left: 4px solid #67c23a;
  margin-left: 20px;
}

.indicator-items-section {
  margin-top: 15px;
}

.indicator-item {
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  margin-bottom: 10px;
  background-color: #fafafa;
}

.indicator-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.action-buttons {
  margin-top: 30px;
  text-align: center;
}

.action-buttons .el-button {
  margin: 0 10px;
  min-width: 100px;
}
</style>