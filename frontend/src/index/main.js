import Vue from "vue";
import VueRouter from 'vue-router'

Vue.config.productionTip = false;
Vue.use(VueRouter)

import "@materializecss/materialize/dist/css/materialize.min.css";
import "github-markdown-css/github-markdown.css";
import 'material-design-icons-iconfont/dist/material-design-icons.css'
import "@fortawesome/fontawesome-free/css/all.css";

import App from "./App.vue";
import Home from "./views/Home.vue";
import Favorites from "./views/Favorites.vue";

const routes = [
  { name: 'Explore', path: '/', component: Home },
  { name: 'Favorites', path: '/favorites', component: Favorites },
  { name: 'Explore', path: '/topic/:topic', component: Home }
]

const router = new VueRouter({
  routes
})

new Vue({
  router,
  render: h => h(App),
}).$mount("#app");
