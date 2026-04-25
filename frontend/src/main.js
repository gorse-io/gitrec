import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import axios from "axios";

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
    { name: 'Explore', path: '', component: Home, meta: { requiresAuth: true } },
    { name: 'Favorites', path: 'favorites', component: Favorites, meta: { requiresAuth: true } },
    { name: 'Trending', path: 'trending', component: Trending },
    { name: 'Trending Language', path: 'trending/:language', component: Trending },
    { name: 'Explore Topic', path: 'topic/:topic', component: Home, meta: { requiresAuth: true } },
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

// Router guard: check authentication before accessing protected routes
router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    try {
      const response = await axios.get("/api/me", { withCredentials: true });
      if (response.data.is_authenticated) {
        next();
      } else {
        next("/login");
      }
    } catch (error) {
      next("/login");
    }
  } else {
    next();
  }
});

const app = createApp(App);
app.use(router);
app.use(vuetify);
app.mount("#app");
