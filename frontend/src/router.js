import { createRouter, createWebHistory } from "vue-router";

import Home from "./views/Home.vue";
import Favorites from "./views/Favorites.vue";
import Login from "./views/Login.vue";
import Privacy from "./views/Privacy.vue";

const routes = [
  {
    path: "/",
    name: "Explore",
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: "/favorites",
    name: "Favorites",
    component: Favorites,
    meta: { requiresAuth: true }
  },
  {
    path: "/topic/:topic",
    name: "Topic",
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
    meta: { guest: true }
  },
  {
    path: "/privacy",
    name: "Privacy",
    component: Privacy
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  // Check if route requires auth
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // For now, let the backend handle auth redirect
    // The Flask backend will redirect to /login if not authenticated
    next();
  } else {
    next();
  }
});

export default router;
