import axios from 'axios';

const AUTH_CACHE_KEY = 'gitrec_auth_state';
const AUTH_CACHE_EXPIRY_MS = 5 * 60 * 1000; // 5 minutes

export default {
  data() {
    return {
      isAuthenticated: false,
      authLogin: null,
    };
  },
  methods: {
    async checkAuth() {
      const cached = localStorage.getItem(AUTH_CACHE_KEY);
      if (cached) {
        try {
          const data = JSON.parse(cached);
          if (Date.now() - data.timestamp < AUTH_CACHE_EXPIRY_MS) {
            this.isAuthenticated = data.is_authenticated;
            this.authLogin = data.login;
            return;
          }
        } catch {
          localStorage.removeItem(AUTH_CACHE_KEY);
        }
      }

      try {
        const response = await axios.get('/api/me', { withCredentials: true });
        this.isAuthenticated = response.data.is_authenticated;
        this.authLogin = response.data.login;
        if (this.isAuthenticated) {
          localStorage.setItem(AUTH_CACHE_KEY, JSON.stringify({
            is_authenticated: true,
            login: response.data.login,
            timestamp: Date.now()
          }));
          this.dispatchAuthChange(true);
        } else {
          localStorage.removeItem(AUTH_CACHE_KEY);
        }
      } catch {
        this.isAuthenticated = false;
        this.authLogin = null;
        localStorage.removeItem(AUTH_CACHE_KEY);
      }
    },
    async logout() {
      try {
        await axios.get('/api/logout', { withCredentials: true });
      } catch (error) {
        console.error('Logout failed:', error);
      }
      localStorage.removeItem(AUTH_CACHE_KEY);
      this.isAuthenticated = false;
      this.authLogin = null;
      this.dispatchAuthChange(false);
    },
    dispatchAuthChange(authenticated) {
      window.dispatchEvent(new CustomEvent('gitrec-auth-change', {
        detail: { authenticated }
      }));
    },
    handleAuthChange(event) {
      this.isAuthenticated = event.detail.authenticated;
      if (!event.detail.authenticated) {
        this.authLogin = null;
      }
    },
  },
  mounted() {
    this.checkAuth();
    window.addEventListener('gitrec-auth-change', this.handleAuthChange);
  },
  beforeUnmount() {
    window.removeEventListener('gitrec-auth-change', this.handleAuthChange);
  },
};
