import "vuetify/styles";
import "@mdi/font/css/materialdesignicons.css";

import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { aliases, mdi } from "vuetify/iconsets/mdi";

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: "mdi",
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: "gitrec",
    themes: {
      gitrec: {
        dark: false,
        colors: {
          primary: "#1e88e5",
          secondary: "#26a69a",
          accent: "#26a69a",
          background: "#ffffff",
          surface: "#ffffff",
          "on-primary": "#f5f5f5",
          "on-surface": "#1f2937",
        },
      },
    },
  },
});