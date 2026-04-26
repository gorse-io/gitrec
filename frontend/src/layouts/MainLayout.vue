<template>
  <div>
    <v-navigation-drawer v-model="drawer" temporary>
      <v-list nav density="comfortable">
        <v-list-item title="Explore" :active="isExploreRoute" @click="goTo('/')" />
        <v-list-item title="Trending" :active="isTrendingRoute" @click="goTo('/trending')" />
        <v-list-item v-if="isAuthenticated" title="Favorites" :active="$route.path === '/favorites'" @click="goTo('/favorites')" />
        
        <v-list-group value="extensions">
          <template #activator="{ props }">
            <v-list-item
              v-bind="props"
              title="Extensions"
              prepend-icon="mdi-puzzle"
            />
          </template>
          
          <v-list-item
            title="Chrome"
            prepend-icon="mdi-google-chrome"
            href="https://chrome.google.com/webstore/detail/gitrec/eihokbaeiebdenibjophfipedicippfl"
            target="_blank"
          />
          <v-list-item
            title="Edge"
            prepend-icon="mdi-microsoft-edge"
            href="https://microsoftedge.microsoft.com/addons/detail/gitrec/cpcfbfpnagiffgpmfljmcdokmfjffdpa"
            target="_blank"
          />
          <v-list-item
            title="Firefox"
            prepend-icon="mdi-firefox"
            href="https://addons.mozilla.org/addon/gitrec/"
            target="_blank"
          />
        </v-list-group>
        
        <v-list-item v-if="isAuthenticated">
          <div class="d-flex align-center w-100">
            <v-btn variant="text" icon="mdi-github" href="https://github.com/gorse-io/gitrec" target="_blank" />
            <v-btn variant="text" icon="mdi-logout" @click="logout" />
          </div>
        </v-list-item>
        <v-list-item v-if="!isAuthenticated">
          <div class="d-flex align-center w-100">
            <v-btn variant="text" icon="mdi-github" href="https://github.com/gorse-io/gitrec" target="_blank" />
            <v-btn variant="text" icon="mdi-login" @click="goTo('/login')" />
          </div>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar color="primary" flat :extended="isExploreRoute || isTrendingRoute" extension-height="42">
      <template #prepend>
        <v-app-bar-nav-icon class="d-md-none" @click="drawer = !drawer" />
      </template>

      <v-container class="d-flex align-center">
        <span class="route-title">GitRec</span>
        <v-spacer />
        <div class="d-none d-md-flex align-center ga-1">
          <v-btn variant="text" :to="'/'" :active="isExploreRoute" color="white">Explore</v-btn>
          <v-btn variant="text" :to="'/trending'" :active="isTrendingRoute" color="white">Trending</v-btn>
          <v-btn v-if="isAuthenticated" variant="text" :to="'/favorites'" :active="$route.path === '/favorites'" color="white">Favorites</v-btn>

          <v-menu location="bottom end">
            <template #activator="{ props }">
              <v-btn v-bind="props" variant="text" color="white" append-icon="mdi-menu-down">
                Extensions
              </v-btn>
            </template>
            <v-list density="compact">
              <v-list-item
                title="Chrome Extension"
                href="https://chrome.google.com/webstore/detail/gitrec/eihokbaeiebdenibjophfipedicippfl"
                target="_blank"
              />
              <v-list-item
                title="Edge Add-on"
                href="https://microsoftedge.microsoft.com/addons/detail/gitrec/cpcfbfpnagiffgpmfljmcdokmfjffdpa"
                target="_blank"
              />
              <v-list-item
                title="Firefox Add-on"
                href="https://addons.mozilla.org/addon/gitrec/"
                target="_blank"
              />
            </v-list>
          </v-menu>

          <v-btn variant="text" href="https://github.com/gorse-io/gitrec" target="_blank" color="white" icon="mdi-github" />
          <v-btn v-if="isAuthenticated" variant="text" color="white" icon="mdi-logout" @click="logout" />
          <v-btn v-if="!isAuthenticated" variant="text" color="white" icon="mdi-login" to="/login" />
        </div>
      </v-container>

      <template v-if="isExploreRoute" #extension>
        <v-container class="topic-tabs-container">
          <v-tabs
            :model-value="activeTopicPath"
            bg-color="primary"
            color="white"
            slider-color="white"
            show-arrows
            class="topic-tabs"
          >
            <v-tab
              v-for="topic in visibleTopics"
              :key="topic"
              :value="topicToPath(topic)"
              :to="topicToPath(topic)"
              exact
            >
              {{ topicLabel(topic) }}
            </v-tab>
          </v-tabs>
        </v-container>
      </template>

      <template v-if="isTrendingRoute" #extension>
        <v-container class="topic-tabs-container">
          <v-tabs
            :model-value="activeLanguage"
            bg-color="primary"
            color="white"
            slider-color="white"
            show-arrows
            class="topic-tabs"
          >
            <v-tab
              v-for="lang in languages"
              :key="lang"
              :value="lang"
              :to="languageToPath(lang)"
            >
              {{ lang === 'all' ? 'GITHUB' : topicLabel(lang) }}
            </v-tab>
          </v-tabs>
        </v-container>
      </template>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      drawer: false,
      isAuthenticated: false,
      topics: [
        "all",
        "ai",
        "python",
        "java",
        "cpp",
        "go",
        "javascript",
        "typescript",
        "c",
        "rust",
      ],
      languages: [
        "all",
        "hackernews",
        "python",
        "java",
        "cpp",
        "go",
        "javascript",
        "typescript",
        "c",
        "rust",
      ],
    };
  },
  computed: {
    routeTitle() {
      if (this.isTrendingRoute) {
        return "Trending";
      }
      if (this.isExploreRoute) {
        return "Explore";
      }
      return this.$route.name;
    },
    isExploreRoute() {
      return this.$route.path === "/" || this.$route.path.startsWith("/topic/");
    },
    isTrendingRoute() {
      return this.$route.path === "/trending" || this.$route.path.startsWith("/trending/");
    },
    activeTopicPath() {
      return this.$route.params.topic ? `/topic/${this.$route.params.topic}` : "/";
    },
    activeLanguage() {
      return this.$route.params.language || "all";
    },
    // Filter topics: hide 'ai' for anonymous users
    visibleTopics() {
      if (this.isAuthenticated) {
        return this.topics;
      }
      return this.topics.filter(topic => topic !== "ai");
    },
  },
  async mounted() {
    await this.checkAuth();
  },
  methods: {
    async checkAuth() {
      const cached = localStorage.getItem("gitrec_auth_state");
      if (cached) {
        try {
          const { is_authenticated, timestamp } = JSON.parse(cached);
          if (Date.now() - timestamp < 5 * 60 * 1000) {
            this.isAuthenticated = is_authenticated;
            return;
          }
        } catch (error) {
          localStorage.removeItem("gitrec_auth_state");
        }
      }
      
      try {
        const response = await axios.get("/api/me", { withCredentials: true });
        this.isAuthenticated = response.data.is_authenticated;
        if (this.isAuthenticated) {
          localStorage.setItem("gitrec_auth_state", JSON.stringify({
            is_authenticated: true,
            login: response.data.login,
            timestamp: Date.now()
          }));
        } else {
          localStorage.removeItem("gitrec_auth_state");
        }
      } catch (error) {
        localStorage.removeItem("gitrec_auth_state");
        this.isAuthenticated = false;
      }
    },
    goTo(path) {
      this.drawer = false;
      if (this.$route.path !== path) {
        this.$router.push(path);
      }
    },
    topicToPath(topic) {
      return topic === "all" ? "/" : `/topic/${topic}`;
    },
    languageToPath(lang) {
      return lang === "all" ? "/trending" : `/trending/${lang}`;
    },
    topicLabel(topic) {
      return topic.replace("-", " ").toUpperCase();
    },
    async logout() {
      try {
        await axios.get("/api/logout");
        localStorage.removeItem("gitrec_auth_state");
        this.isAuthenticated = false;
        this.$router.push("/");
      } catch (error) {
        console.error("Logout failed:", error);
      }
    },
  },
};
</script>

<style>
.route-title {
  font-weight: 300;
  font-size: 1.2rem;
  color: #f5f5f5;
}

.topic-tabs {
  min-height: 42px;
}

.topic-tabs-container {
  padding-top: 0;
  padding-bottom: 0;
}
</style>
