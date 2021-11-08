<template>
  <div id="app">
    <div class="navbar-fixed">
      <nav :class="[primaryColor]">
        <div class="nav-wrapper container">
          <a href="#" data-target="mobile-navbar" class="sidenav-trigger"><i class="material-icons">menu</i></a>
          <span style="font-weight: 300; font-size: 1.2rem">{{ title }}</span>
          <ul id="nav-mobile" class="right hide-on-med-and-down">
            <li><router-link to="/">Home</router-link></li>
            <li><router-link to="/favorites">Favorites</router-link></li>
          </ul>
        </div>
      </nav>
      <ul class="sidenav" id="mobile-navbar">
        <li><router-link to="/">Home</router-link></li>
        <li><router-link to="/favorites">Favorites</router-link></li>
      </ul>
    </div>
    <router-view @setTitle="setTitle"></router-view>
  </div>
</template>

<script>
export default {
  data() {
    return {
      title: null,
      primaryColor: "blue darken-1",
      textColor: "white-text text-lighten-3",
    };
  },
  methods: {
    setTitle(title) {
      this.title = title;
    }
  }
};
</script>
