import { createApp } from "vue";
import { createRouter, createWebHashHistory } from "vue-router";

import "@materializecss/materialize/dist/css/materialize.min.css";
import "github-markdown-css/github-markdown.css";
import 'material-design-icons-iconfont/dist/material-design-icons.css';
import "@fortawesome/fontawesome-free/css/all.css";

import App from "./App.vue";
import Home from "./views/Home.vue";
import Favorites from "./views/Favorites.vue";

const routes = [
  { name: 'Explore', path: '/', component: Home },
  { name: 'Favorites', path: '/favorites', component: Favorites },
  { name: 'Explore', path: '/topic/:topic', component: Home }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

const app = createApp(App);
app.use(router);
app.mount("#app");
