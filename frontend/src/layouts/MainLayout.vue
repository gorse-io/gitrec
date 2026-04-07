<template>
  <div>
    <v-navigation-drawer v-model="drawer" temporary>
      <v-list nav density="comfortable">
        <v-list-item title="Explore" :active="isExploreRoute" @click="goTo('/')" />
        <v-list-item title="Favorites" :active="$route.path === '/favorites'" @click="goTo('/favorites')" />
        <v-list-item title="Logout" href="/logout" />
      </v-list>
    </v-navigation-drawer>

    <v-app-bar color="primary" flat :extended="isExploreRoute">
      <template #prepend>
        <v-app-bar-nav-icon class="d-md-none" @click="drawer = !drawer" />
      </template>

      <v-container class="d-flex align-center">
        <span class="route-title">{{ $route.name }}</span>
        <v-spacer />
        <div class="d-none d-md-flex align-center ga-1">
          <v-btn variant="text" :to="'/'" :active="isExploreRoute" color="white">Explore</v-btn>
          <v-btn variant="text" :to="'/favorites'" :active="$route.path === '/favorites'" color="white">Favorites</v-btn>

          <v-menu location="bottom end">
            <template #activator="{ props }">
              <v-btn v-bind="props" variant="text" color="white" append-icon="mdi-menu-down">
                Extensions
              </v-btn>
            </template>
            <v-list density="compact">
              <v-list-item
                title="Chrome Extension"
                href="https://chrome.google.com/webstore/detail/gitrec/eihokbaeiebdenibjophfipedicippfl"
                target="_blank"
              />
              <v-list-item
                title="Edge Add-on"
                href="https://microsoftedge.microsoft.com/addons/detail/gitrec/cpcfbfpnagiffgpmfljmcdokmfjffdpa"
                target="_blank"
              />
              <v-list-item
                title="Firefox Add-on"
                href="https://addons.mozilla.org/addon/gitrec/"
                target="_blank"
              />
            </v-list>
          </v-menu>

          <v-btn variant="text" href="/logout" color="white">Logout</v-btn>
        </div>
      </v-container>

      <template v-if="isExploreRoute" #extension>
        <v-container>
          <v-tabs
            :model-value="activeTopic"
            bg-color="primary"
            color="white"
            slider-color="white"
            show-arrows
            class="topic-tabs"
          >
            <v-tab
              v-for="topic in topics"
              :key="topic"
              :value="topic"
              :to="topicToPath(topic)"
            >
              {{ topicLabel(topic) }}
            </v-tab>
          </v-tabs>
        </v-container>
      </template>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </div>
</template>

<script>
export default {
  data() {
    return {
      drawer: false,
      topics: [
        "all",
        "ai",
        "python",
        "java",
        "cpp",
        "go",
        "javascript",
        "typescript",
        "c",
        "rust",
      ],
    };
  },
  computed: {
    isExploreRoute() {
      return this.$route.path === "/" || this.$route.path.startsWith("/topic/");
    },
    activeTopic() {
      return this.$route.params.topic || "all";
    },
  },
  methods: {
    goTo(path) {
      this.drawer = false;
      if (this.$route.path !== path) {
        this.$router.push(path);
      }
    },
    topicToPath(topic) {
      return topic === "all" ? "/" : `/topic/${topic}`;
    },
    topicLabel(topic) {
      return topic.replace("-", " ").toUpperCase();
    },
  },
};
</script>

<style>
.route-title {
  font-weight: 300;
  font-size: 1.2rem;
  color: #f5f5f5;
}

.topic-tabs {
  min-height: 42px;
}
</style>
