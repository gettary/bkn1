import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

// Views
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue'
import CreateAssessment from '@/views/CreateAssessment.vue'
import AssessmentList from '@/views/AssessmentList.vue'
import DataEntry from '@/views/DataEntry.vue'
import SummaryReport from '@/views/SummaryReport.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    component: Dashboard,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        redirect: '/dashboard/assessments'
      },
      {
        path: 'create-assessment',
        name: 'CreateAssessment',
        component: CreateAssessment,
        meta: { 
          requiresAuth: true,
          roles: ['Admin', 'Moderator']
        }
      },
      {
        path: 'assessments',
        name: 'AssessmentList',
        component: AssessmentList,
        meta: { requiresAuth: true }
      },
      {
        path: 'data-entry/:assessmentId',
        name: 'DataEntry',
        component: DataEntry,
        meta: { requiresAuth: true },
        props: true
      },
      {
        path: 'summary-report',
        name: 'SummaryReport',
        component: SummaryReport,
        meta: { requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated']
  const userRole = store.getters['auth/userRole']

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.roles && !to.meta.roles.includes(userRole)) {
    next('/assessments') // Redirect to assessments if no permission
  } else if (to.name === 'Login' && isAuthenticated) {
    next('/assessments')
  } else {
    next()
  }
})

export default router