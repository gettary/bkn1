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
    console.log("SET_ASSESSMENTS called with:", assessments) // Log the input data
    if (!assessments || !Array.isArray(assessments)) {
      console.error('Invalid assessments data:', assessments)
      state.assessments = []
      return
    }
    console.log("Valid assessments data. Updating state.") // Log before updating state
    state.assessments = assessments  
    console.log("State updated. Current assessments:", state.assessments) // Log the updated state
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
    if (!assessmentId) {
      console.error('Invalid assessmentId:', assessmentId)
      return
    }

    if (Array.isArray(state.assessments)) {
      state.assessments = state.assessments.filter(a => a.id !== assessmentId)
    } else {
      console.error('state.assessments is not an array:', state.assessments)
    }
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
      console.log("Sending data to API:", assessment);
      const response = await assessmentService.createAssessment(assessment)
      console.log('API Response:', response) // Log the full response for debugging

      // Validate the response structure
      if (!response || !response.assessment) {
        throw new Error('Invalid API response: Missing assessment data')
      }

      commit('ADD_ASSESSMENT', response.assessment)
      return response.assessment // Return the assessment object
    } catch (error) {
      console.error('Error creating assessment:', error)
      throw error
    }
  },

  async updateAssessment({ commit }, { id, assessment }) {
  try {
    console.log("updateAssessment called with ID:", id);
    console.log("Assessment data:", assessment);
    await assessmentService.updateAssessment(id, assessment);
    console.log("Assessment updated successfully:", assessment);
  } catch (error) {
    console.error("Error updating assessment:", error);
    throw error;
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