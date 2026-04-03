<template>
  <v-app>
    <!-- Navigation Bar -->
    <v-app-bar color="primary" density="comfortable">
      <v-container class="d-flex align-center">
        <span class="text-h5 font-weight-light">GitRec</span>
      </v-container>
    </v-app-bar>

    <!-- Main Content -->
    <v-main>
      <v-container class="py-8">
        <v-row justify="center">
          <v-col cols="12" md="8" lg="6">
            <!-- Logo -->
            <div class="text-center mb-4">
              <img src="/logo.png" width="256" alt="GitRec Logo" />
            </div>

            <!-- Description -->
            <h5 class="text-center text-h5 mb-4">
              Explore
              <a href="https://github.com" target="_blank" class="text-primary">GitHub</a>
              with
              <a href="https://gorse.io" target="_blank" class="text-primary">Gorse</a>
              recommender system
            </h5>

            <!-- Sign In Button -->
            <div class="text-center mb-6">
              <v-btn
                color="primary"
                size="large"
                href="/login/github"
                prepend-icon="mdi-github"
              >
                Sign in with GitHub
              </v-btn>
            </div>

            <!-- Browser Extensions -->
            <h5 class="text-center text-h5 mb-4">Browser Extensions</h5>
            
            <v-row justify="center" class="mb-8">
              <v-col cols="4" md="2" class="text-center">
                <a
                  href="https://chrome.google.com/webstore/detail/gitrec/eihokbaeiebdenibjophfipedicippfl"
                  target="_blank"
                >
                  <img
                    src="https://i.loli.net/2021/04/23/IqpU7COKQvzrcyG.png"
                    alt="Chrome Extension"
                    style="max-width: 100%"
                  />
                </a>
              </v-col>
              <v-col cols="4" md="2" class="text-center">
                <a
                  href="https://microsoftedge.microsoft.com/addons/detail/gitrec/cpcfbfpnagiffgpmfljmcdokmfjffdpa"
                  target="_blank"
                >
                  <img
                    src="https://i.loli.net/2021/04/23/EnS3eDi4I86Yv2N.png"
                    alt="Edge Add-on"
                    style="max-width: 100%"
                  />
                </a>
              </v-col>
              <v-col cols="4" md="2" class="text-center">
                <a href="https://addons.mozilla.org/addon/gitrec/" target="_blank">
                  <img
                    src="/firefox.png"
                    alt="Firefox Add-on"
                    style="max-width: 100%"
                  />
                </a>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <!-- Footer -->
    <v-footer color="primary" class="pa-0">
      <v-container>
        <v-row>
          <v-col cols="12" md="6">
            <h5 class="text-h5 mb-2">About</h5>
            <p class="text-white">
              GitRec is the missing recommender system for GitHub built to test the
              usability of the Gorse open recommender system engine.
            </p>
          </v-col>
          <v-col cols="12" md="4" class="offset-md-2">
            <h5 class="text-h5 text-white mb-2">Links</h5>
            <ul class="list-unstyled">
              <li class="mb-2">
                <a class="text-white" href="/privacy">Privacy Policy</a>
              </li>
              <li class="mb-2">
                <a class="text-white" href="https://github.com/gorse-io/gitrec" target="_blank">
                  Source @ GitHub
                </a>
              </li>
            </ul>
          </v-col>
        </v-row>
      </v-container>
      <v-divider></v-divider>
      <v-container>
        <div class="text-center">
          © {{ new Date().getFullYear() }} zhenghaoz
        </div>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script>
export default {
  name: "Login",
};
</script>

<style scoped>
a {
  text-decoration: none;
}
.list-unstyled {
  list-style: none;
  padding: 0;
}
</style>
