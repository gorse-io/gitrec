<template>
  <div>
    <v-app-bar color="primary" flat>
      <v-container>
        <span class="page-title">GitRec</span>
      </v-container>
    </v-app-bar>

    <v-main>
      <v-container class="sign-in-body">
        <p class="text-center">
        <img src="/logo.png" width="256px" />
        </p>
        <h5 class="text-center">
          Explore <a href="https://github.com" target="_blank">GitHub</a> with
          <a href="https://gorse.io" target="_blank">Gorse</a> recommender system
        </h5>
        <p class="text-center">
          <v-btn color="primary" size="large" href="/login/github" prepend-icon="mdi-github" class="text-none" variant="flat">
            Sign in with GitHub
          </v-btn>
        </p>
        <h5 class="text-center">Browser Extensions</h5>
        <br>

        <v-row class="text-center" justify="center">
          <v-col cols="4" sm="3" md="2">
            <a href="https://chrome.google.com/webstore/detail/gitrec/eihokbaeiebdenibjophfipedicippfl" target="_blank">
              <img src="https://i.loli.net/2021/04/23/IqpU7COKQvzrcyG.png" class="extension-icon" />
            </a>
          </v-col>
          <v-col cols="4" sm="3" md="2">
            <a href="https://microsoftedge.microsoft.com/addons/detail/gitrec/cpcfbfpnagiffgpmfljmcdokmfjffdpa" target="_blank">
              <img src="https://i.loli.net/2021/04/23/EnS3eDi4I86Yv2N.png" class="extension-icon" />
            </a>
          </v-col>
          <v-col cols="4" sm="3" md="2">
            <a href="https://addons.mozilla.org/addon/gitrec/" target="_blank">
              <img src="/firefox.png" class="extension-icon" />
            </a>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <v-footer color="primary" class="page-footer">
      <v-container>
        <v-row>
          <v-col cols="12" md="7">
            <h5>About</h5>
            <p class="text-on-primary">
              GitRec is the missing recommender system for GitHub built to test the
              usability of the Gorse open recommender system engine.
            </p>
          </v-col>
          <v-col cols="12" md="5">
            <h5 class="text-on-primary">Links</h5>
            <ul class="footer-links">
              <li>
                <router-link class="text-on-primary" to="/privacy">Privacy Policy</router-link>
              </li>
              <li>
                <a class="text-on-primary" href="https://github.com/gorse-io/gitrec" target="_blank">Source @ GitHub</a>
              </li>
            </ul>
          </v-col>
        </v-row>
        <div class="copyright">© {{ currentYear }} zhenghaoz</div>
      </v-container>
    </v-footer>
  </div>
</template>

<script>
export default {
  computed: {
    currentYear() {
      return new Date().getFullYear();
    },
  },
};
</script>

<style>
.page-title {
  font-weight: 300;
  font-size: 1.5rem;
  color: #f5f5f5;
}

.sign-in-body {
  box-sizing: border-box;
  min-width: 200px;
  max-width: 980px;
  margin: 0 auto;
  padding: 45px;
}

.extension-icon {
  max-width: 100%;
}

.page-footer {
  margin-top: 24px;
}

.text-on-primary {
  color: #f5f5f5;
}

.footer-links {
  list-style: none;
  padding-left: 0;
}

.footer-links li {
  margin-bottom: 6px;
}

.copyright {
  padding-top: 8px;
  color: #f5f5f5;
}
</style>
