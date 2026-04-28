<template>
  <div>
    <!-- Login prompt for anonymous users -->
    <v-alert
      v-if="authChecked && !isAuthenticated && !error"
      type="info"
      variant="tonal"
      class="login-alert"
      role="button"
      tabindex="0"
      @click="goToLogin"
      @keydown.enter="goToLogin"
      @keydown.space.prevent="goToLogin"
    >
      <div class="login-alert__text">
        Login with GitHub to get personalized recommendations based on your starred repositories
      </div>
    </v-alert>

    <v-alert v-if="!loading && error" type="error" variant="tonal">
      <div class="login-alert__text">
        {{ error }}
      </div>
    </v-alert>

    <v-container v-else>
      <div v-if="full_name" class="repo-header">
        <a :href="html_url" target="_blank" class="repo-link">
          <v-icon size="18">mdi-link-variant</v-icon>
          {{ full_name }}
        </a>
        <div class="repo-meta">
          <span v-if="language" class="repo-meta-link">
            <v-icon size="16">mdi-code-tags</v-icon>
            {{ language }}
          </span>
          <a :href="html_url + '/stargazers'" target="_blank" class="repo-meta-link">
            <v-icon size="16">mdi-star</v-icon>
            {{ formatNumber(stargazers_count) }}
          </a>
          <a :href="html_url + '/network/members'" target="_blank" class="repo-meta-link">
            <v-icon size="16">mdi-source-fork</v-icon>
            {{ formatNumber(forks_count) }}
          </a>
          <a :href="html_url + '/watchers'" target="_blank" class="repo-meta-link">
            <v-icon size="16">mdi-eye</v-icon>
            {{ formatNumber(subscribers_count) }}
          </a>
        </div>
      </div>
      <Preloader v-if="loading" />
      <article v-else-if="!error && readme" class="markdown-body" v-html="readme"></article>
    </v-container>

    <v-btn
      icon
      size="large"
      :color="like_pressed ? 'red' : 'primary'"
      :loading="likeLoading"
      class="fab-btn fab-like"
      @click="like"
    >
      <v-icon>{{ like_pressed ? "mdi-heart" : "mdi-heart-outline" }}</v-icon>
    </v-btn>

    <v-btn 
      icon 
      size="large" 
      color="primary" 
      :loading="nextLoading"
      class="fab-btn fab-next" 
      @click="next"
    >
      <v-icon>mdi-play</v-icon>
    </v-btn>
  </div>
</template>


<script>
import Preloader from "../components/Preloader.vue";
import axios from "axios";
import authMixin from "../mixins/authMixin";

export default {
  components: {
    Preloader
  },
  mixins: [authMixin],
  data() {
    return {
      like_pressed: false,
      likeLoading: false,
      nextLoading: false,
      loading: false,
      authChecked: false,
      item_id: null,
      full_name: "",
      html_url: null,
      stargazers_count: 0,
      forks_count: 0,
      subscribers_count: 0,
      language: "",
      readme: null,
      error: null,
      topic: "",
    };
  },
  computed: {
    topicPath() {
      let path = this.topic;
      if (path === "/cpp") {
        path = "/c%2B%2B";
      }
      return path;
    },
  },
  watch: {
    $route() {
      this.topic = this.$route.params.topic ? "/" + this.$route.params.topic : "";
      this.clearRepository();
      this.recommend();
    },
  },
  created() {
    this.topic = this.$route.params.topic ? "/" + this.$route.params.topic : "";
    this.clearRepository();
  },
  async mounted() {
    await this.checkAuth();
    this.authChecked = true;
    this.recommend();
  },
  methods: {
    goToLogin() {
      this.$router.push("/login");
    },
    formatNumber(num) {
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + "k";
      }
      return num.toString();
    },
    recommend() {
      this.error = null;
      this.loading = true;
      return axios
        .get("/api/repo" + this.topicPath, { withCredentials: true })
        .then((response) => {
          this.setRepository(response.data);
        })
        .catch((error) => {
          this.error = error.response?.data?.error || "Failed to fetch repository. Please try again.";
        })
        .finally(() => {
          this.loading = false;
        });
    },
    setRepository(repo) {
      this.item_id = repo.item_id;
      this.full_name = repo.full_name;
      this.readme = repo.readme;
      this.html_url = repo.html_url;
      this.stargazers_count = repo.stargazers_count;
      this.forks_count = repo.forks_count;
      this.subscribers_count = repo.subscribers_count;
      this.language = repo.language;
    },
    clearRepository() {
      this.item_id = null;
      this.full_name = "";
      this.readme = null;
      this.error = null;
      this.loading = false;
      this.stargazers_count = 0;
      this.forks_count = 0;
      this.subscribers_count = 0;
      this.language = "";
      this.like_pressed = false;
    },
    like() {
      if (!this.isAuthenticated) {
        this.$router.push("/login");
        return;
      }
      this.likeLoading = true;
      axios
        .post("/api/like/" + this.item_id, null, { withCredentials: true })
        .then(() => {
          this.like_pressed = true;
        })
        .catch((error) => {
          this.error = error.response?.data?.error || "Failed to like repository.";
        })
        .finally(() => {
          this.likeLoading = false;
        });
    },
    next() {
      if (!this.item_id) return;

      this.nextLoading = true;
      this.error = null;
      axios
        .post("/api/read/" + this.item_id, null, { withCredentials: true })
        .then(() => {
          this.clearRepository();
          return this.recommend();
        })
        .catch((error) => {
          this.error = error.response?.data?.error || "Failed to fetch next repository.";
        })
        .finally(() => {
          this.nextLoading = false;
        });
    },
  },
};
</script>

<style scoped>
.login-alert {
  cursor: pointer;
}

.login-alert__text {
  white-space: normal;
  line-height: 1.5;
}

.markdown-body {
  box-sizing: border-box;
  min-width: 200px;
  max-width: 980px;
  margin: 0 auto;
  padding: 20px 45px 45px;
}

@media (max-width: 767px) {
  .markdown-body {
    padding: 15px;
    padding-bottom: 45px;
  }
}

.repo-header {
  padding: 10px 45px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 767px) {
  .repo-header {
    padding: 10px 15px 0;
  }
}

.repo-link,
.repo-meta-link {
  color: #26a69a;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.repo-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.fab-btn {
  position: fixed !important;
  right: 24px;
  z-index: 30;
}

.fab-like {
  bottom: 92px;
}

.fab-next {
  bottom: 24px;
}

@media (max-width: 767px) {
  .fab-btn {
    right: 16px;
  }
}
</style>
