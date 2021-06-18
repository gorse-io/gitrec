<template>
  <div id="app">
    <div class="navbar-fixed">
      <nav :class="[primaryColor]">
        <div class="nav-wrapper container">
          <span style="font-weight: 300; font-size: 1.5rem">{{ title }}</span>
        </div>
      </nav>
    </div>
    <div class="container">
      <article class="markdown-body" v-html="readme"></article>
    </div>
    <footer>
      <div class="toolbar-fixed" :class="[primaryColor]">
        <ul>
          <li class="waves-effect waves-light">
            <a :href="html_url + '/stargazers'" target="__blank"
              ><i class="fa-lg fas fa-star"></i>&nbsp;&nbsp;{{ stargazers }}</a
            >
          </li>
          <li class="waves-effect waves-light">
            <a :href="html_url + '/network/members'" target="__blank"
              ><i class="fa-lg fa fa-code-branch" aria-hidden="true"></i
              >&nbsp;&nbsp;{{ forks }}</a
            >
          </li>
          <li class="waves-effect waves-light">
            <a :href="html_url" target="__blank"
              ><i class="material-icons">open_in_new</i></a
            >
          </li>
          <li class="waves-effect waves-light">
            <a @click="like"
              ><i class="material-icons" :class="[iconColoer]">favorite</i></a
            >
          </li>
          <li class="waves-effect waves-light">
            <a @click="next"><i class="material-icons">skip_next</i></a>
          </li>
        </ul>
      </div>
    </footer>
  </div>
</template>

<script>
import M from "materialize-css";
const axios = require("axios");
const titleDefault = "Loading...";
const readmeDefault = `
      <div class="preloader-background">
      	<div class="preloader-wrapper big active">
      		<div class="spinner-layer spinner-blue-only">
      			<div class="circle-clipper left">
      				<div class="circle"></div>
      			</div>
      			<div class="gap-patch">
      				<div class="circle"></div>
      			</div>
      			<div class="circle-clipper right">
      				<div class="circle"></div>
      			</div>
      		</div>
      	</div>
      </div>
            `;
export default {
  data() {
    return {
      iconColoer: null,
      item_id: null,
      title: titleDefault,
      html_url: null,
      stargazers_url: null,
      forks_url: null,
      stargazers: 0,
      forks: 0,
      readme: readmeDefault,
      primaryColor: "blue darken-1",
      textColor: "white-text text-lighten-3",
    };
  },
  mounted() {
    M.AutoInit();
    axios.get("/api/repo", { withCredentials: true }).then((response) => {
      this.setRepository(response.data);
    });
  },
  methods: {
    setRepository(repo) {
      this.item_id = repo.item_id;
      this.readme = repo.readme;
      this.title = repo.full_name;
      this.html_url = repo.html_url;
      this.stargazers = repo.stargazers;
      this.forks = repo.forks;
    },
    like() {
      axios
        .get("/api/like/" + this.item_id, { withCredentials: true })
        .then(() => {
          this.iconColoer = "red-icon";
        });
    },
    next() {
      axios
        .get("/api/read/" + this.item_id, { withCredentials: true })
        .then(() => {
          // load next repo
          this.title = titleDefault;
          this.readme = readmeDefault;
          (this.iconColoer = null),
            axios
              .get("/api/repo", { withCredentials: true })
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
  padding: 45px;
  padding-bottom: 100px;
}

@media (max-width: 767px) {
  .markdown-body {
    padding: 15px;
    padding-bottom: 100px;
  }
}

.preloader-background {
  display: flex;
  align-items: center;
  justify-content: center;

  position: fixed;
  z-index: 100;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.toolbar-fixed {
  width: 100%;
  padding: 0;
  height: 56px;
  position: fixed;
  bottom: 0px;
}

.toolbar-fixed.active > a i {
  opacity: 0;
}

.toolbar-fixed ul {
  display: -webkit-flex;
  display: -ms-flexbox;
  display: flex;
  top: 0;
  bottom: 0;
}

.toolbar-fixed ul li {
  -webkit-flex: 1;
  -ms-flex: 1;
  flex: 1;
  display: inline-block;
  margin: -;
  height: 100%;
  transition: none;
  position: relative;
  top: -15px;
}

.toolbar-fixed ul li a {
  display: block;
  overflow: hidden;
  position: relative;

  width: 100%;
  height: 100%;
  background-color: transparent;
  box-shadow: none;
  color: #fff;
  line-height: 56px;
  z-index: 1;
}

.toolbar-fixed ul li a i {
  line-height: inherit;
}

.toolbar-fixed ul {
  left: 0;
  right: 0;
  text-align: center;
}

.toolbar-fixed ul li {
  margin-bottom: 15px;
}

.material-icons.red-icon {
  color: red;
}
</style>
