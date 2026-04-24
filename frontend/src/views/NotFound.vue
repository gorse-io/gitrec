<template>
  <div>
    <v-app-bar color="primary" flat>
      <v-container>
        <span class="page-title">GitRec</span>
      </v-container>
    </v-app-bar>

    <v-main>
      <v-container class="not-found-body">
        <p class="text-center">
          <img src="/logo.png" width="256px" alt="GitRec logo" />
        </p>
        <h1 class="text-center text-h2 mb-4">404</h1>
        <h5 class="text-center mb-6">
          Page not found
        </h5>
        <p class="text-center">
          <v-btn color="primary" size="large" to="/" prepend-icon="mdi-home" class="text-none">
            Go Home
          </v-btn>
        </p>
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
                <a class="text-on-primary" href="https://github.com/gorse-io/gitrec" target="_blank" rel="noopener noreferrer">Source @ GitHub</a>
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

.not-found-body {
  box-sizing: border-box;
  min-width: 200px;
  max-width: 980px;
  margin: 0 auto;
  padding: 45px;
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
