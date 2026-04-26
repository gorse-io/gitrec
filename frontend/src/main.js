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

// Auth state cache with expiration (5 minutes)
const AUTH_CACHE_KEY = "gitrec_auth_state";
const AUTH_CACHE_EXPIRY = 5 * 60 * 1000; // 5 minutes in milliseconds

function getCachedAuthState() {
  const cached = localStorage.getItem(AUTH_CACHE_KEY);
  if (!cached) return null;
  
  const { is_authenticated, login, timestamp } = JSON.parse(cached);
  if (Date.now() - timestamp > AUTH_CACHE_EXPIRY) {
    localStorage.removeItem(AUTH_CACHE_KEY);
    return null;
  }
  return { is_authenticated, login };
}

function setCachedAuthState(is_authenticated, login) {
  localStorage.setItem(AUTH_CACHE_KEY, JSON.stringify({
    is_authenticated,
    login,
    timestamp: Date.now()
  }));
}

function clearCachedAuthState() {
  localStorage.removeItem(AUTH_CACHE_KEY);
}

// Global axios interceptor for 401 errors
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearCachedAuthState();
      if (window.location.pathname !== "/login") {
        router.push("/login");
      }
    }
    return Promise.reject(error);
  }
);

// Router guard: check authentication before accessing protected routes
router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    // First check cache
    const cached = getCachedAuthState();
    if (cached && cached.is_authenticated) {
      next();
      return;
    }
    
    // Cache expired or missing, check with API
    try {
      const response = await axios.get("/api/me", { withCredentials: true });
      if (response.data.is_authenticated) {
        setCachedAuthState(response.data.is_authenticated, response.data.login);
        next();
      } else {
        clearCachedAuthState();
        next("/login");
      }
    } catch (error) {
      clearCachedAuthState();
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
