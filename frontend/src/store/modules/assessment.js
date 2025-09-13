import { assessmentService, userDataService } from '../../services'

const state = {
  assessments: [],
  currentAssessment: null,
  loading: false
}

const mutations = {
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ASSESSMENTS(state, assessments) {
    state.assessments = assessments
  },
  SET_CURRENT_ASSESSMENT(state, assessment) {
    state.currentAssessment = assessment
  },
  ADD_ASSESSMENT(state, assessment) {
    state.assessments.push(assessment)
  },
  UPDATE_ASSESSMENT(state, updatedAssessment) {
    const index = state.assessments.findIndex(a => a.id === updatedAssessment.id)
    if (index !== -1) {
      state.assessments.splice(index, 1, updatedAssessment)
    }
  },
  REMOVE_ASSESSMENT(state, assessmentId) {
    state.assessments = state.assessments.filter(a => a.id !== assessmentId)
  }
}

const actions = {
  async fetchAssessments({ commit }) {
    commit('SET_LOADING', true)
    try {
      const response = await assessmentService.getAssessments()
      commit('SET_ASSESSMENTS', response.assessments)
      return response
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchAssessment({ commit }, id) {
    commit('SET_LOADING', true)
    try {
      const response = await assessmentService.getAssessment(id)
      commit('SET_CURRENT_ASSESSMENT', response.assessment)
      return response
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async createAssessment({ commit }, assessment) {
    try {
      const response = await assessmentService.createAssessment(assessment)
      commit('ADD_ASSESSMENT', response.assessment)
      return response
    } catch (error) {
      throw error
    }
  },

  async updateAssessment({ commit }, { id, assessment }) {
    try {
      const response = await assessmentService.updateAssessment(id, assessment)
      commit('UPDATE_ASSESSMENT', response.assessment)
      return response
    } catch (error) {
      throw error
    }
  },

  async deleteAssessment({ commit }, id) {
    try {
      await assessmentService.deleteAssessment(id)
      commit('REMOVE_ASSESSMENT', id)
    } catch (error) {
      throw error
    }
  },

  async publishAssessment({ commit }, id) {
    try {
      const response = await assessmentService.publishAssessment(id)
      commit('UPDATE_ASSESSMENT', response.assessment)
      return response
    } catch (error) {
      throw error
    }
  }
}

const getters = {
  assessments: state => state.assessments,
  currentAssessment: state => state.currentAssessment,
  loading: state => state.loading,
  draftAssessments: state => state.assessments.filter(a => a.status === 'draft'),
  publishedAssessments: state => state.assessments.filter(a => a.status === 'published')
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}