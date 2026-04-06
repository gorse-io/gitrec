<template>
  <v-app>
    <router-view />
  </v-app>
</template>

<script>
export default {
  name: "App",
  mounted() {
    this.updateThemeColor();
  },
  methods: {
    updateThemeColor() {
      const theme = this.$vuetify.theme;
      const primaryColor = theme.current.value.colors.primary;
      
      let metaThemeColor = document.querySelector('meta[name="theme-color"]');
      if (!metaThemeColor) {
        metaThemeColor = document.createElement('meta');
        metaThemeColor.name = 'theme-color';
        document.head.appendChild(metaThemeColor);
      }
      metaThemeColor.content = primaryColor;
    }
  }
};
</script>
