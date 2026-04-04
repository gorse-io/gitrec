import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";

import "github-markdown-css/github-markdown.css";
import vuetify from "./plugins/vuetify";

import App from "./App.vue";
import MainLayout from "./layouts/MainLayout.vue";
import Home from "./views/Home.vue";
import Favorites from "./views/Favorites.vue";
import Login from "./views/Login.vue";
import Privacy from "./views/Privacy.vue";

const routes = [
  { path: '/', component: MainLayout, children: [
    { name: 'Explore', path: '', component: Home },
    { name: 'Favorites', path: 'favorites', component: Favorites },
    { name: 'Explore Topic', path: 'topic/:topic', component: Home },
  ]},
  { name: 'Login', path: '/login', component: Login },
  { name: 'Privacy', path: '/privacy', component: Privacy },
  { path: '/logout', redirect: '/login' },
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

const app = createApp(App);
app.use(router);
app.use(vuetify);
app.mount("#app");
