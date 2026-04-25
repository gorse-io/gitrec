<template>
  <div>
    <v-container>
      <Preloader v-if="loading" />

      <v-list v-else class="repo-list" lines="one">
        <v-list-item
          v-for="repo in repos"
          :key="repo.id || repo.url || repo.title || repo.full_name"
          rounded="lg"
          class="repo-item"
        >
          <div class="repo-card">
            <div class="repo-main">
              <v-row>
                <v-col class="repo-title-row">
                  <v-icon color="primary" size="18" class="repo-icon">mdi-git</v-icon>
                  <a class="repo-name" :href="repoUrl(repo)" target="_blank" rel="noopener noreferrer">
                    {{ repoTitle(repo) }}
                  </a>
                </v-col>

                <v-btn
                  color="primary"
                  variant="outlined"
                  size="small"
                  class="repo-action"
                  :href="repoUrl(repo)"
                  target="_blank"
                  prepend-icon="mdi-github"
                >
                  View
                </v-btn>
              </v-row>

              <p class="repo-description">{{ repo.description || 'No description available' }}</p>

              <div class="repo-footer">
                <div class="repo-meta">
                  <span v-if="isHackerNews && repo.points" class="repo-meta-item">
                    <v-icon size="16">mdi-arrow-up</v-icon>
                    {{ formatNumber(repo.points) }} points
                  </span>
                  <span v-else-if="repo.language" class="repo-meta-item">
                    <span class="language-dot" :style="{ backgroundColor: getLanguageColor(repo.language) }"></span>
                    {{ repo.language }}
                  </span>
                  <span v-if="!isHackerNews" class="repo-meta-item">
                    <v-icon size="16">mdi-star</v-icon>
                    {{ formatNumber(repoStars(repo)) }}
                  </span>
                  <span v-if="!isHackerNews && repo.forks" class="repo-meta-item">
                    <v-icon size="16">mdi-source-fork</v-icon>
                    {{ formatNumber(repo.forks) }}
                  </span>
                  <div v-if="!isHackerNews && repoContributors(repo).length > 0" class="built-by">
                    <span class="built-by-label">Built by</span>
                    <v-avatar size="24" v-for="user in repoContributors(repo).slice(0, 5)" :key="user.username || user.name" class="built-by-avatar">
                      <img :src="user.avatar" :alt="user.username || user.name" />
                    </v-avatar>
                  </div>
                  <span v-if="!isHackerNews && repo.points" class="repo-meta-item">
                    <v-icon size="16">mdi-message</v-icon>
                    {{ repo.points }} comments
                  </span>
                </div>

                <span v-if="!isHackerNews && repoAddedStars(repo)" class="repo-trending-score">
                  <v-icon size="16">mdi-star</v-icon>
                  {{ formatNumber(repoAddedStars(repo)) }} stars today
                </span>
              </div>
            </div>
          </div>
        </v-list-item>
      </v-list>

      <v-row v-if="!loading && repos.length === 0">
        <v-col cols="12" class="text-center">
          <p class="text-h6">{{ isHackerNews ? 'No GitHub repositories found in Hacker News' : 'No trending repositories found' }}</p>
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
  computed: {
    isHackerNews() {
      return this.language === "hackernews";
    },
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
      
      if (this.isHackerNews) {
        // Fetch Hacker News stories with GitHub repos
        this.fetchHackerNews();
      } else {
        // Fetch GitHub Trending
        let lang = this.language;
        if (lang === "cpp") lang = "c++";
        if (lang === "ai") lang = "all";
        
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
      }
    },
    fetchHackerNews() {
      axios
        .get("/api/hackernews", { withCredentials: true })
        .then((response) => {
          this.repos = response.data;
          this.loading = false;
        })
        .catch((error) => {
          console.error("Error fetching Hacker News:", error);
          this.loading = false;
        });
    },
    formatNumber(num) {
      if (typeof num === "string") {
        return num;
      }
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + "k";
      }
      return num;
    },
    repoTitle(repo) {
      if (this.isHackerNews) {
        return repo.full_name || repo.title || "";
      }
      return repo.title || repo.full_name || "";
    },
    repoUrl(repo) {
      return repo.url || repo.html_url || "";
    },
    repoStars(repo) {
      return repo.stars || repo.stargazers_count || repo.score || 0;
    },
    repoAddedStars(repo) {
      return repo.addStars || repo.current_period_stars || 0;
    },
    repoContributors(repo) {
      return repo.contributors || repo.builtBy || repo.built_by || [];
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
        Scala: "c22d40",
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
.repo-list {
  padding: 0;
}

.repo-item {
  margin-bottom: 4px;
  padding: 0;
  border: 1px solid #e5e7eb;
  align-items: stretch;
  overflow: hidden;
}

.repo-card {
  width: 100%;
  padding: 24px;
}

.repo-main {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.repo-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.repo-name {
  color: rgb(var(--v-theme-primary));
  font-size: 1.25rem;
  font-weight: 600;
  text-decoration: none;
  line-height: 1.3;
}

.repo-name:hover {
  text-decoration: underline;
}

.repo-icon {
  flex: 0 0 auto;
  margin-top: 3px;
}

.repo-description {
  color: #57606a;
  margin: 0;
  line-height: 1.5;
  font-size: 0.975rem;
}

.repo-action {
  flex-shrink: 0;
}

.repo-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.repo-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 0.875rem;
  color: #57606a;
}

.repo-meta-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.language-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex: 0 0 auto;
}

.built-by {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.built-by-label {
  color: #57606a;
}

.built-by-avatar {
  margin-left: 0;
  border: 1px solid #d0d7de;
}

.repo-trending-score {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  font-size: 0.875rem;
  color: #57606a;
  white-space: nowrap;
}

@media (max-width: 600px) {
  .repo-card {
    padding: 18px 16px;
  }

  .repo-action {
    align-self: flex-start;
  }

  .repo-footer {
    align-items: flex-start;
  }

  .repo-trending-score {
    margin-left: 0;
  }
}
</style>
