import { authService } from '@/services'

const state = {
  user: JSON.parse(localStorage.getItem('user')) || null,
  token: localStorage.getItem('token') || null,
  isAuthenticated: !!localStorage.getItem('token')
}

const mutations = {
  SET_USER(state, user) {
    state.user = user
    localStorage.setItem('user', JSON.stringify(user))
  },
  SET_TOKEN(state, token) {
    state.token = token
    state.isAuthenticated = !!token
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
  },
  LOGOUT(state) {
    state.user = null
    state.token = null
    state.isAuthenticated = false
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }
}

const actions = {
  async login({ commit }, { username, password }) {
    try {
      const response = await authService.login(username, password)
      commit('SET_TOKEN', response.access_token)
      commit('SET_USER', response.user)
      return response
    } catch (error) {
      throw error
    }
  },

  async getProfile({ commit }) {
    try {
      const response = await authService.getProfile()
      commit('SET_USER', response.user)
      return response
    } catch (error) {
      commit('LOGOUT')
      throw error
    }
  },

  logout({ commit }) {
    authService.logout()
    commit('LOGOUT')
  }
}

const getters = {
  user: state => state.user,
  isAuthenticated: state => state.isAuthenticated,
  userRole: state => state.user?.role,
  canManageAssessments: state => state.user?.role && ['Admin', 'Moderator'].includes(state.user.role)
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}