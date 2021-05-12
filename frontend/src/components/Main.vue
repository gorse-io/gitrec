<template>
  <div>
    <div class="navbar-fixed">
      <nav :class="[primaryColor]">
        <div class="nav-wrapper container">
            <span style="font-weight: 300; font-size: 1.5rem">zhenghaoz/gorse</span>
        </div>
      </nav>
    </div>
    <div v-if="!login" class="container sign-in-body">
      <p class="center-align">
        <img src="surftocat.png" width="256px" />
      </p>
      <h5 class="center-align">
        Explore <a href="https://github.com" target="_blank">GitHub</a> with
        <a href="https://gorse.io" target="_blank">Gorse</a> recommender system
      </h5>
      <p class="center-align">
        <a :class="[primaryColor]" class="waves-effect waves-light btn"
          ><i class="fab fa-github material-icons left"></i>Sign in with
          GitHub</a
        >
      </p>
    </div>
    <div v-else class="container">
      <article class="markdown-body" v-html="readme"></article>
    </div>
    <footer v-if="!login" :class="[primaryColor]" class="page-footer">
      <div class="container">
        <div class="row">
          <div class="col l6 s12">
            <h5>About</h5>
            <p :class="[textColor]">
              GitRec is the missing discovery queue for GitHub built to test the
              usability of the Gorse recommender system engine.
            </p>
          </div>
          <div class="col l4 offset-l2 s12">
            <h5 :class="[textColor]">Links</h5>
            <ul>
              <li>
                <a
                  :class="[textColor]"
                  href="https://github.com/zhenghaoz/gitrec"
                  target="_blank"
                  >Source @ GitHub</a
                >
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div class="footer-copyright">
        <div class="container">© 2021 zhenghaoz</div>
      </div>
    </footer>
    <footer>
      <div class="toolbar-fixed" :class="[primaryColor]">
        <ul>
          <li class="waves-effect waves-light">
            <a href="#!"><i class="fa-lg fas fa-star"></i>&nbsp;&nbsp;121</a>
          </li>
          <li class="waves-effect waves-light">
            <a><i class="fa-lg fa fa-code-branch" aria-hidden="true"></i>&nbsp;&nbsp;121</a>
          </li>
          <li class="waves-effect waves-light">
            <a href="#!"><i class="material-icons">open_in_new</i></a>
          </li>
          <li class="waves-effect waves-light">
            <a href="#!"><i class="material-icons">favorite</i></a>
          </li>
          <li class="waves-effect waves-light">
            <a href="#!"><i class="material-icons">skip_next</i></a>
          </li>
        </ul>
      </div>
    </footer>
  </div>
</template>

<script>
const axios = require("axios");
export default {
  name: "HelloWorld",
  data() {
    return {
      login: true,
            readme: `
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
            `,
      primaryColor: "blue darken-1",
      textColor: "white-text text-lighten-3",
    };
  },
  props: {
    msg: String,
  },
  mounted() {
    axios.get("http://127.0.0.1:5000/repo/zhenghaoz:gorse").then((response) => {
      this.readme = response.data;
    });
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
}

.sign-in-body {
  box-sizing: border-box;
  min-width: 200px;
  max-width: 980px;
  margin: 0 auto;
  padding: 45px;
}

@media (max-width: 767px) {
  .markdown-body {
    padding: 15px;
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
</style>
