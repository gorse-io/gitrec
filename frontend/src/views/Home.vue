<template>
  <div>
    <v-container>
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
            {{ stargazers_count }}
          </a>
          <a :href="html_url + '/network/members'" target="_blank" class="repo-meta-link">
            <v-icon size="16">mdi-source-fork</v-icon>
            {{ forks_count }}
          </a>
          <a :href="html_url + '/watchers'" target="_blank" class="repo-meta-link">
            <v-icon size="16">mdi-eye</v-icon>
            {{ subscribers_count }}
          </a>
        </div>
      </div>
      <Preloader v-if="readme == null" />
      <article v-else class="markdown-body" v-html="readme"></article>
    </v-container>

    <v-btn
      icon
      size="large"
      :color="like_pressed ? 'red' : 'primary'"
      class="fab-btn fab-like"
      @click="like"
    >
      <v-icon>{{ like_pressed ? "mdi-heart" : "mdi-heart-outline" }}</v-icon>
    </v-btn>

    <v-btn icon size="large" color="primary" class="fab-btn fab-next" @click="next">
      <v-icon>mdi-play</v-icon>
    </v-btn>
  </div>
</template>


<script>
import Preloader from "../components/Preloader.vue";
import axios from "axios";

export default {
  components: {
    Preloader
  },
  data() {
    return {
      like_pressed: false,
      item_id: null,
      full_name: "",
      html_url: null,
      stargazers_url: null,
      forks_url: null,
      stargazers_count: 0,
      forks_count: 0,
      subscribers_count: 0,
      language: "",
      readme: null,
      primaryColor: "blue darken-1",
      textColor: "white-text text-lighten-3",
      topic: "",
    };
  },
  watch: {
    $route() {
      if (this.$route.params.topic != null) {
        this.topic = "/" + this.$route.params.topic;
      } else {
        this.topic = "";
      }
      this.clearRepository();
      this.recommend();
    },
  },
  created() {
    if (this.$route.params.topic != null) {
      this.topic = "/" + this.$route.params.topic;
    } else {
      this.topic = "";
    }
    this.clearRepository();
  },
  mounted() {
    this.recommend();
  },
  methods: {
    recommend() {
      let topic = this.topic;
      if (topic == "/cpp") {
        topic = "/c%2B%2B";
      }
      console.log("/api/repo" + topic);
      axios
        .get("/api/repo" + topic, { withCredentials: true })
        .then((response) => {
          this.setRepository(response.data);
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
      this.stargazers_count = 0;
      this.forks_count = 0;
      this.subscribers_count = 0;
      this.language = "";
      this.like_pressed = false;
    },
    like() {
      axios
        .post("/api/like/" + this.item_id, { withCredentials: true })
        .then(() => {
          this.like_pressed = true;
        });
    },
    next() {
      axios
        .post("/api/read/" + this.item_id, { withCredentials: true })
        .then(() => {
          // load next repo
          this.clearRepository();
          axios
            .get("/api/repo" + this.topic, { withCredentials: true })
            .then((response) => {
              this.setRepository(response.data);
            });
        });
    },
  },
};
</script>

<style>
.markdown-body {
  box-sizing: border-box;
  min-width: 200px;
  max-width: 980px;
  margin: 0 auto;
  padding-left: 45px;
  padding-right: 45px;
  padding-top: 20px;
  padding-bottom: 45px;
}

@media (max-width: 767px) {
  .markdown-body {
    padding: 15px;
    padding-bottom: 45px;
  }
}

.repo-header {
  padding-top: 10px;
  padding-left: 45px;
  padding-right: 45px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 767px) {
  .repo-header {
    padding-top: 10px;
    padding-left: 15px;
    padding-right: 15px;
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
