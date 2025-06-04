<template>
  <div id="app">
    <div>
      <nav :class="[primaryColor]">
        <div class="nav-wrapper container">
          <span style="font-weight: 300; font-size: 1.5rem">GitRec</span>
        </div>
      </nav>
    </div>
    <div class="container sign-in-body">
      <p class="center-align">
        <img src="logo.png" width="256px" />
      </p>
      <h5 class="center-align">
        Explore <a href="https://github.com" target="_blank">GitHub</a> with
        <a href="https://gorse.io" target="_blank">Gorse</a> recommender system
      </h5>
      <p class="center-align">
        <a :class="[primaryColor]" class="waves-effect waves-light btn" href="/login/github"><i
            class="fab fa-github material-icons left"></i>Sign in with
          GitHub</a>
      </p>
      <h5 class="center-align">
        Browser Extensions
      </h5>
      <br>
      <div class="row center-align">
        <div class="col m2 s4 offset-m3">
          <a href="https://chrome.google.com/webstore/detail/gitrec/eihokbaeiebdenibjophfipedicippfl" target="_blank">
            <img src="https://i.loli.net/2021/04/23/IqpU7COKQvzrcyG.png" />
          </a>
        </div>
        <div class="col m2 s4">
          <a href="https://microsoftedge.microsoft.com/addons/detail/gitrec/cpcfbfpnagiffgpmfljmcdokmfjffdpa"
            target="_blank">
            <img src="https://i.loli.net/2021/04/23/EnS3eDi4I86Yv2N.png" />
          </a>
        </div>
        <div class="col m2 s4">
          <a href="https://addons.mozilla.org/addon/gitrec/" target="_blank">
            <img src="firefox.png" />
          </a>
        </div>
      </div>
    </div>
    <footer :class="[primaryColor]" class="page-footer">
      <div class="container">
        <div class="row">
          <div class="col l6 s12">
            <h5>About</h5>
            <p :class="[textColor]">
              GitRec is the missing recommender system for GitHub built to test the
              usability of the Gorse open recommender system engine.
            </p>
          </div>
          <div class="col l4 offset-l2 s12">
            <h5 :class="[textColor]">Links</h5>
            <ul>
              <li>
                <a :class="[textColor]" href="/privacy">Privacy Policy</a>
              </li>
              <li>
                <a :class="[textColor]" href="https://github.com/gorse-io/gitrec" target="_blank">Source @ GitHub</a>
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div class="footer-copyright">
        <div class="container">© {{ new Date().getFullYear() }} zhenghaoz</div>
      </div>
    </footer>
  </div>
</template>

<script>
import M from "@materializecss/materialize";

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
