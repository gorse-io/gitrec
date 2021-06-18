<template>
  <div id="app">
    <div class="navbar-fixed">
      <nav :class="[primaryColor]">
        <div class="nav-wrapper container">
          <span style="font-weight: 300; font-size: 1.5rem">GitRec</span>
        </div>
      </nav>
    </div>
    <div class="container sign-in-body">
      <p class="center-align">
        <img src="surftocat.png" width="256px" />
      </p>
      <h5 class="center-align">
        Explore <a href="https://github.com" target="_blank">GitHub</a> with
        <a href="https://gorse.io" target="_blank">Gorse</a> recommender system
      </h5>
      <p class="center-align">
        <a
          :class="[primaryColor]"
          class="waves-effect waves-light btn"
          href="/login/github"
          ><i class="fab fa-github material-icons left"></i>Sign in with
          GitHub</a
        >
      </p>
    </div>
    <footer :class="[primaryColor]" class="page-footer">
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
  </div>
</template>

<script>
import M from "materialize-css";
export default {
  data() {
    return {
      primaryColor: "blue darken-1",
      textColor: "white-text text-lighten-3",
    };
  },
  mounted() {
    M.AutoInit();
  },
};
</script>

<style>
.sign-in-body {
  box-sizing: border-box;
  min-width: 200px;
  max-width: 980px;
  margin: 0 auto;
  padding: 45px;
}
</style>
