<template>
  <div class="summary-report">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>สรุปรายงาน</h3>
          <el-button type="primary" @click="openDashboard">
            <el-icon><DataAnalysis /></el-icon>
            สรุปผลแบบ Dashboard
          </el-button>
        </div>
      </template>

      <div v-loading="loading">
        <div v-if="publishedAssessments.length === 0" class="no-data">
          <el-empty description="ไม่มีแบบประเมินที่เผยแพร่แล้ว" />
        </div>

        <div v-else>
          <el-collapse v-model="activeAssessments" accordion>
            <el-collapse-item
              v-for="assessment in publishedAssessments"
              :key="assessment.id"
              :title="assessment.name"
              :name="assessment.id"
              @click="loadAssessmentReport(assessment.id)"              
            >
              <div v-if="reportData[assessment.id]" class="report-content">
                <div
                  v-for="(item, itemIndex) in reportData[assessment.id]"
                  :key="`item-${itemIndex}`"
                  class="report-item"
                >
                  <h3 class="item-title">{{ item.title }}</h3>

                  <el-collapse>                  
                    <el-collapse-item 
                      v-for="(indicator, indicatorIndex) in item.indicators"
                      :key="`indicator-${indicatorIndex}`"
                      :title="indicator?.title || 'ไม่มีชื่อ'"
                      :name="indicatorIndex"
                    >
                      <el-card class="indicator-card">
                        <template #header>                          
                          <div class="indicator-header">                              
                          </div>
                        </template>

                        <div class="indicator-items">
                          <el-table
                            :data="indicator.items"
                            style="width: 100%"
                            size="small"
                          >
                            <el-table-column
                              prop="title"
                              label="รายการตัวชี้วัด"
                              min-width="200"
                            />
                            <el-table-column
                              prop="target_value"
                              label="ค่าเป้าหมาย"
                              width="120"
                              align="center"
                            />
                            <el-table-column
                              label="ผลงาน 3 ปีย้อนหลัง"
                              align="center"
                            >
                              <el-table-column 
                                prop="past_2565" 
                                label="ปี 2565"
                                width="60"
                                align="center" 
                              />
                              <el-table-column 
                                prop="past_2566" 
                                label="ปี 2566"
                                width="60"
                                align="center" 
                              />
                              <el-table-column 
                                prop="past_2567" 
                                label="ปี 2567" 
                                width="60"
                                align="center"
                              />        
                            </el-table-column>
                            <el-table-column
                              label="ผลงาน 3 ปีย้อนหลัง"
                              align="center"
                            >
                              <el-table-column
                                prop="actual_target"
                                label="เป้าหมายจริง"
                                width="60"
                                align="center"
                              />
                              <el-table-column
                                prop="performance"
                                label="ผลงาน"
                                width="60"
                                align="center"
                              >
                                <template #default="{ row }">
                                  <div v-if="getItemUserData(indicator.user_data, row.id).length > 0">
                                    {{ getItemUserData(indicator.user_data, row.id)[0].data.performance || '-' }}
                                  </div>
                                  <div v-else>
                                    -
                                  </div>
                                </template>
                              </el-table-column>
                              <el-table-column
                                prop="rate"
                                label="อัตรา"
                                width="60"
                                align="center"
                              >
                                <template #default="{ row }">
                                  <div v-if="getItemUserData(indicator.user_data, row.id).length > 0">
                                    {{ getItemUserData(indicator.user_data, row.id)[0].data.rate || '-' }}
                                  </div>
                                  <div v-else>
                                    -
                                  </div>
                                </template>
                              </el-table-column>
                            </el-table-column>
                            <el-table-column
                              prop="score"
                              label="คะแนน"
                              width="60"
                              align="center"
                            >
                              <template #default="{ row }">
                                <div v-if="getItemUserData(indicator.user_data, row.id).length > 0">
                                  {{ getItemUserData(indicator.user_data, row.id)[0].data.score || '-' }}
                                </div>
                                <div v-else>
                                  -
                                </div>
                              </template>
                            </el-table-column>
                            <el-table-column
                              label="รูปภาพ"
                              width="60"
                              align="center"
                            >
                              <template #default="{ row }">
                                <div v-if="getItemUserData(indicator.user_data, row.id).length > 0">
                                  <div v-if="getItemUserData(indicator.user_data, row.id)[0].data.image_path">
                                    <el-button
                                      type="primary"
                                      size="small"
                                      @click="viewImage(getItemUserData(indicator.user_data, row.id)[0].data.image_path)"
                                    >
                                      <el-icon><View /></el-icon>
                                      ดูรูปภาพ
                                    </el-button>
                                  </div>
                                  <div v-else>
                                    ไม่มีรูปภาพ
                                  </div>
                                </div>
                                <div v-else>
                                  ไม่มีข้อมูล
                                </div>
                              </template>
                            </el-table-column>
                            <el-table-column
                              label="สถานะการกรอกข้อมูล"
                              width="100"
                              align="center"
                            >
                              <template #default="{ row }">
                                <div class="status-info">
                                  <div
                                    v-for="userData in getItemUserData(indicator.user_data, row.id)"
                                    :key="userData.user_name"
                                    class="user-status"
                                  >
                                    <span class="user-name">{{ userData.user_name }}:</span>
                                    <el-tag
                                      :type="userData.status === 'complete' ? 'success' : 'warning'"
                                      size="small"
                                    >
                                      {{ userData.status === 'complete' ? 'เสร็จสิ้น' : 'ร่าง' }}
                                    </el-tag>
                                  </div>
                                  <div v-if="getItemUserData(indicator.user_data, row.id).length === 0" class="no-data-text">
                                    ยังไม่มีข้อมูล
                                  </div>
                                </div>
                              </template>
                            </el-table-column>
                          </el-table>
                        </div>
                      </el-card>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </div>

              <el-skeleton v-else :loading="loadingReports[assessment.id]" animated>
                <template #template>
                  <el-skeleton-item variant="h3" style="width:50%;" />
                  <el-skeleton-item variant="text" />
                  <el-skeleton-item variant="text" />
                </template>
              </el-skeleton>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </el-card>

    <!-- Image Preview Dialog -->
    <el-dialog
      v-model="imageDialogVisible"
      title="ดูรูปภาพ"
      width="50%"
    >
      <div class="image-preview">
        <img :src="previewImageSrc" alt="Uploaded Image" style="max-width: 100%; height: auto;" />
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { ElMessage } from 'element-plus';
import { DataAnalysis, View } from '@element-plus/icons-vue';
import { userDataService } from '@/services';

export default {
  name: 'SummaryReport',
  components: {
    DataAnalysis,
    View,
  },
  setup() {
    const store = useStore();

    const loading = ref(false);
    const activeAssessments = ref([]);
    const activeIndicators = reactive({});
    const activeUserData = reactive({});
    const reportData = reactive({});
    const loadingReports = reactive({});
    const imageDialogVisible = ref(false);
    const previewImageSrc = ref('');

    const publishedAssessments = computed(() => store.getters['assessment/publishedAssessments']);
    const canManageAssessments = computed(() => store.getters['auth/canManageAssessments']);
    
    const loadAssessments = async () => {
      try {
        loading.value = true;
        await store.dispatch('assessment/fetchAssessments');        
        publishedAssessments.value.forEach((assessment) => {          
          if (!activeIndicators[assessment.id]) {
            activeIndicators[assessment.id] = [];
          }
          //console.log(`Key created for assessment ID: ${assessment.id}`);
          
        });
      } catch (error) {
        ElMessage.error('ไม่สามารถโหลดรายการแบบประเมินได้');
      } finally {
        loading.value = false;
      }
    };

    const loadAssessmentReport = async (assessmentId) => {
      if (reportData[assessmentId]) {
        console.log(`Report Data for Assessment ID ${assessmentId}:`, reportData[assessmentId]);
        return; // Already loaded
      }

      try {
        loadingReports[assessmentId] = true;
        const response = await userDataService.getAssessmentReport(assessmentId);
        reportData[assessmentId] = response.report;        
      } catch (error) {
        ElMessage.error('ไม่สามารถโหลดรายงานได้');
      } finally {
        loadingReports[assessmentId] = false;
      }
    };

    const getItemUserData = (userData, indicatorItemId) => {
      return userData.filter((ud) => ud.data.indicator_item_id === indicatorItemId);
    };

    const viewImage = (imagePath) => {
      previewImageSrc.value = `/uploads/${imagePath}`;
      imageDialogVisible.value = true;
    };

    const openDashboard = () => {
      // Open Metabase dashboard in new tab
      const dashboardUrl = "http://affiliate-nikon-raw-tomato.trycloudflare.com/metabase/public/dashboard/22c10365-6cf0-4f1f-b7a7-798e6283e3a4";
      window.open(dashboardUrl, '_blank');
    };

    onMounted(() => {
      loadAssessments();
    });

    return {
      loading,
      activeAssessments,
      activeIndicators,
      activeUserData,
      reportData,
      loadingReports,
      imageDialogVisible,
      previewImageSrc,
      publishedAssessments,
      canManageAssessments,
      loadAssessmentReport,      
      getItemUserData,
      viewImage,
      openDashboard,
    };
  },
};
</script>

<style scoped>

.summary-report {
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

.no-data {
  text-align: center;
  padding: 40px;
}

.report-content {
  padding: 20px 0;  
}

.report-item {
  margin-bottom: 30px;
}

.item-title {
  color: #409eff;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}

.report-indicator {
  margin-bottom: 20px;
}

.indicator-card {
  border-left: 4px solid #67c23a;
}

.indicator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;  
}

.indicator-header h5 {
  margin: 0;
  color: #67c23a;
}

.permissions-info {
  display: flex;
  gap: 5px;
}

.indicator-items {
  margin-bottom: 20px;
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.user-status {
  display: flex;
  align-items: center;
  gap: 5px;
  justify-content: center;
}

.user-name {
  font-size: 12px;
  color: #666;
}

.no-data-text {
  color: #999;
  font-size: 12px;
  text-align: center;
}

.user-data-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.user-data-section h6 {
  margin-bottom: 15px;
  color: #606266;
}

.user-data-details {
  padding: 15px;
  background-color: #fafafa;
  border-radius: 6px;
}

.image-preview {
  text-align: center;
}

</style>
