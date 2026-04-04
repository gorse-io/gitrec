<template>
  <div class="preloader-background">
    <v-progress-circular indeterminate color="primary" size="64" width="6" />
  </div>
</template>

<style>
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
</style>