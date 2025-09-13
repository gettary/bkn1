import { createStore } from 'vuex'
import auth from './modules/auth'
import assessment from './modules/assessment'

export default createStore({
  modules: {
    auth,
    assessment
  }
})