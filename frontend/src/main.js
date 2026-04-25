import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";

import "github-markdown-css/github-markdown-light.css";
import vuetify from "./plugins/vuetify";

import App from "./App.vue";
import MainLayout from "./layouts/MainLayout.vue";
import Home from "./views/Home.vue";
import Favorites from "./views/Favorites.vue";
import Trending from "./views/Trending.vue";
import Login from "./views/Login.vue";
import Privacy from "./views/Privacy.vue";
import NotFound from "./views/NotFound.vue";

const routes = [
  { path: '/', component: MainLayout, children: [
    { name: 'Explore', path: '', component: Home },
    { name: 'Favorites', path: 'favorites', component: Favorites },
    { name: 'Trending', path: 'trending', component: Trending },
    { name: 'Trending Language', path: 'trending/:language', component: Trending },
    { name: 'Explore Topic', path: 'topic/:topic', component: Home },
  ]},
  { name: 'Login', path: '/login', component: Login },
  { name: 'Privacy', path: '/privacy', component: Privacy },
  { path: '/logout', redirect: '/login' },
  { name: 'NotFound', path: '/:pathMatch(.*)*', component: NotFound },
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

const app = createApp(App);
app.use(router);
app.use(vuetify);
app.mount("#app");
