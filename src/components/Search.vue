<script setup>


 const emit = defineEmits(['changed']);
 const props = defineProps({
    search: {
      type: String,
      required: true,
    },
 })


function emitChange(ev) {
   emit('changed',ev.target.value);
}

document.addEventListener("DOMContentLoaded", (event) => {
        const search = document.getElementById("search");
        search.value = "";
        search.focus();
})
document.addEventListener("keydown", (event) => {
        if (event.key == '/') {
          const search = document.getElementById("search");
          search.value = "";
          search.focus();
          event.preventDefault();
          emitChange({target:search});
          return false;
        }
})


</script>

<template>
        <div id="wrapper">
        <input @input="emitChange" id="search" placeholder="/" :value="search">
        </div>
</template>

<style scoped>
#wrapper {
 margin: 0rem;
 height: 3rem;
 display:flex;
}


#header {
  display:inline-block;
  font-size: 2rem;
  margin-right:1rem;
  color: var(--green);
}

#search {
  display:inline-block;
  flex-grow:10;
  max-height:2rem;
  font-size: 1.5rem;
}
</style>
