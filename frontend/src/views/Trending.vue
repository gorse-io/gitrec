<template>
  <div>
    <v-container>
      <v-row>
        <v-col cols="12">
          <h2 class="text-h4 mb-4">Trending Repositories</h2>
        </v-col>
      </v-row>

      <Preloader v-if="loading" />

      <v-row v-else>
        <v-col cols="12" md="6" lg="4" v-for="repo in repos" :key="repo.full_name">
          <v-card class="repo-card" :href="repo.html_url" target="_blank">
            <v-card-title class="d-flex align-center ga-2">
              <v-icon color="primary">mdi-book-open-variant</v-icon>
              <span class="repo-name">{{ repo.full_name }}</span>
            </v-card-title>

            <v-card-text>
              <p class="repo-description">{{ repo.description || 'No description available' }}</p>

              <div class="repo-meta mt-3">
                <span v-if="repo.language" class="d-flex align-center ga-1">
                  <span class="language-dot" :style="{ backgroundColor: getLanguageColor(repo.language) }"></span>
                  {{ repo.language }}
                </span>
                <span class="d-flex align-center ga-1">
                  <v-icon size="16">mdi-star</v-icon>
                  {{ formatNumber(repo.stargazers_count) }}
                </span>
                <span class="d-flex align-center ga-1">
                  <v-icon size="16">mdi-source-fork</v-icon>
                  {{ formatNumber(repo.forks) }}
                </span>
              </div>

              <div v-if="repo.built_by && repo.built_by.length > 0" class="built-by mt-3">
                <span class="text-caption">Built by</span>
                <v-avatar size="24" v-for="user in repo.built_by.slice(0, 5)" :key="user.username" class="ml-1">
                  <img :src="user.avatar" :alt="user.username" />
                </v-avatar>
              </div>
            </v-card-text>

            <v-card-actions>
              <v-btn
                color="primary"
                variant="text"
                :href="repo.html_url"
                target="_blank"
                prepend-icon="mdi-github"
              >
                View on GitHub
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>

      <v-row v-if="!loading && repos.length === 0">
        <v-col cols="12" class="text-center">
          <p class="text-h6">No trending repositories found</p>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import Preloader from "../components/Preloader.vue";
import axios from "axios";

export default {
  components: {
    Preloader,
  },
  data() {
    return {
      loading: true,
      repos: [],
      language: "",
    };
  },
  watch: {
    $route() {
      this.language = this.$route.params.language || "";
      this.fetchTrending();
    },
  },
  created() {
    this.language = this.$route.params.language || "";
  },
  mounted() {
    this.fetchTrending();
  },
  methods: {
    fetchTrending() {
      this.loading = true;
      let lang = this.language;
      // Map topic names to language names for the API
      if (lang === "cpp") lang = "c++";
      if (lang === "ai") lang = ""; // AI is not a language, show all
      
      const params = new URLSearchParams();
      if (lang) params.append("language", lang);
      
      axios
        .get("/api/trending?" + params.toString(), { withCredentials: true })
        .then((response) => {
          this.repos = response.data;
          this.loading = false;
        })
        .catch((error) => {
          console.error("Error fetching trending:", error);
          this.loading = false;
        });
    },
    formatNumber(num) {
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + "k";
      }
      return num;
    },
    getLanguageColor(language) {
      const colors = {
        JavaScript: "#f1e05a",
        TypeScript: "#2b7489",
        Python: "#3572A5",
        Java: "#b07219",
        "C++": "#f34b7d",
        C: "#555555",
        Go: "#00ADD8",
        Rust: "#dea584",
        Ruby: "#701516",
        PHP: "#4F5D95",
        Swift: "#ffac45",
        Kotlin: "#A97BFF",
        Scala: "#c22d40",
        Shell: "#89e051",
        HTML: "#e34c26",
        CSS: "#563d7c",
      };
      return colors[language] || "#8e8e8e";
    },
  },
};
</script>

<style>
.repo-card {
  height: 100%;
  transition: transform 0.2s;
}

.repo-card:hover {
  transform: translateY(-4px);
}

.repo-name {
  font-size: 1rem;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.repo-description {
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  min-height: 60px;
}

.repo-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 0.875rem;
  color: #666;
}

.language-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.built-by {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
