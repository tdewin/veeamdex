<script setup>
 const props = defineProps({
    linkData: {
      required: true,
    },
    displayRedirect: {
      required: true,
    }
 })
</script>
<script>
</script>

<template>
      <div id="bgblur" v-if="displayRedirect !=0">
      </div>
      <div id="redirect" v-if="displayRedirect !=0">
        <div class="spacer"></div>
        <div class="redirectmsg">mid</div>
        <div class="spacer"></div>
      </div>
</template>

<style scoped>
.spacer {
  flex-grow:1;
  min-width:0.1rem;
}
.redirectmsg {
  flex-grow:10;
  max-width:90vw;
  align-self:center;
}
#bgblur {
  position: fixed;
  top: 0rem;
  bottom: 0rem;
  left: 0rem;
  right: 0rem;
  background-color: var(--color-text);
  opacity: 0.5;
  z-index:999998;
}
#redirect {
  display:flex;
  gap:0.5rem;
  flex-wrap: wrap;
  position: fixed;
  top: 5rem;
  bottom: 5rem;
  left: 5rem;
  right: 5rem;
  background-color: var(--color-background);
  opacity: 0.9;
  z-index:999999;
}

@media screen and (max-width: 1000px), screen and (max-height: 700px) {
}
</style>
