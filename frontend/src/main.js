//import Vue from 'vue'
import { createApp } from 'vue'

import {
  Button,
  Modal,
} from 'ant-design-vue'
import 'ant-design-vue/dist/antd.css'

import App from './App.vue'
let app = createApp(App)

// ===== Plugins
app.config.productionTip = false
app.use(Button)
app.use(Modal)

// ===== Directive : v-swipe
// vue2 binding example: https://codepen.io/lisilinhart/pen/wxRQBo?editors=0010
import Hammer from 'hammerjs'
app.directive('swipe', {
	mounted: function(el, binding) {
		if (typeof binding.value === "function") {
			const mc = new Hammer(el)
      const direction = (
        ((binding.arg !== 'left') ? Hammer.DIRECTION_RIGHT : 0) |
        ((binding.arg !== 'right') ? Hammer.DIRECTION_LEFT : 0)
      )
			mc.get("swipe").set({ direction: direction })
			mc.on("swipe", binding.value)
		}
	}
})

// ===== Store (Vuex)
import store from './store.js'
app.use(store)

// ===== Router
import router from './router.js'
app.use(router)

// ===== Fontawesome Icons
import fontawesome from '@fortawesome/fontawesome'
fontawesome.library.add(
  import('@fortawesome/fontawesome-free-solid'),
  import('@fortawesome/fontawesome-free-regular'),
)


app.mount('#app')
