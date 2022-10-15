<template>
  <div>
    <div class="container">
      <div v-if="full_name" class="header">
        <a :href="html_url" target="__blank"><i class="material-icons feedback-icon">link</i>&nbsp;{{ full_name }}</a>
        <div class="secondary-content">
          <a v-if="language"><i class="material-icons feedback-icon">code</i>&nbsp;{{ language }}&nbsp;</a>
          <a :href="html_url + '/stargazers'" target="__blank"><i class="material-icons feedback-icon">star</i>&nbsp;{{
          stargazers }}</a>&nbsp;
          <a :href="html_url + '/network/members'" target="__blank"><i
              class="material-icons feedback-icon">fork_right</i>&nbsp;{{ forks }}</a>&nbsp;
          <a :href="html_url + '/watchers'" target="__blank"><i
              class="material-icons feedback-icon">remove_red_eye</i>&nbsp;{{ watchers }}</a>
        </div>
      </div>
      <Preloader v-if="readme == null"/>
      <article v-else class="markdown-body" v-html="readme"></article>
    </div>
    <div class="fixed-action-btn" style="bottom: 86px;">
      <a class="btn-floating" :class="{'red': like_pressed}">
        <i class="material-icons" @click="like">favorite</i>
      </a>
    </div>
    <div class="fixed-action-btn">
      <a class="btn-floating">
        <i class="material-icons" @click="next">play_arrow</i>
      </a>
    </div>
  </div>
</template>


<script>
import Preloader from "../components/Preloader.vue";
import M from "@materializecss/materialize";
const axios = require("axios");

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
      stargazers: 0,
      forks: 0,
      watchers: 0,
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
    if (this.$route.params.category != null) {
      this.category = "/" + this.$route.params.category;
    } else {
      this.category = "";
    }
    this.clearRepository();
  },
  mounted() {
    M.AutoInit();
    this.recommend();
  },
  methods: {
    recommend() {
      axios
        .get("/api/repo" + this.topic, { withCredentials: true })
        .then((response) => {
          this.setRepository(response.data);
        });
    },
    setRepository(repo) {
      this.item_id = repo.item_id;
      this.full_name = repo.full_name;
      this.readme = repo.readme;
      this.html_url = repo.html_url;
      this.stargazers = repo.stargazers;
      this.forks = repo.forks;
      this.watchers = repo.watchers;
      this.language = repo.language;
    },
    clearRepository() {
      this.item_id = null;
      this.full_name = "";
      this.readme = null;
      this.stargazers = 0;
      this.forks = 0;
      this.watchers = 0;
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
            .get("/api/repo" + this.category, { withCredentials: true })
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

.header {
  padding-top: 10px;
  padding-left: 45px;
  padding-right: 45px;
}

@media (max-width: 767px) {
  .header {
    padding-top: 10px;
    padding-left: 15px;
    padding-right: 15px;
  }
}

.header a {
  color: #26a69a;
}
</style>
