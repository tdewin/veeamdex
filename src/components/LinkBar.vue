<script setup>
 const props = defineProps({
    linkData: {
      required: true,
    },
 })
</script>
<script>
function smoothScroll(id) {
        console.log(id);
        let q = document.getElementById(id);
        const s = document.getElementById("topnav").getBoundingClientRect().height;
        
        
        window.scrollTo({
                top:Math.max(q.getBoundingClientRect().top+window.pageYOffset-s-4,0),
                behavior:'smooth'})
}
</script>

<template>
      <div id="linkbar">
        <template v-for="cat in linkData"> 
        <div class="linkbardiv" @click="smoothScroll('cat-'+cat.catname.replace(' ','_'))">
            {{cat.catname}} <span class="rnumber">{{cat.catlinks.length}}</span>
        </div>
        </template>
      </div>
</template>

<style scoped>
.rnumber {
  display: inline-block;
  color: var(--color-background);
  background-color: var(--green);
  border-radius: 2rem;
  min-width: 2rem;
  /* font-size: small; */
  padding-left: 0.2rem;
  padding-right: 0.2rem;
  float: right;
}
#linkbar {
  display:flex;
  gap:0.5rem;
  flex-wrap: wrap;
}
.linkbardiv {
  min-width:11.35rem;
  padding:0.2rem;
  border-radius: 0.2rem;
  border: 0.15rem solid var(--green);
  color: var(--green);
  text-align:center;
  cursor: pointer;
}

@media screen and (max-width: 1000px), screen and (max-height: 700px) {
        .linkbardiv {
          border: unset;
          padding-top:0rem !important;
          padding-bottom:0rem !important;
          padding-left: 0.2rem !important;
          padding-right: 0.2rem !important;
          background-color: var(--green);
          color: var(--color-background);
          min-width:unset;
        }
       .rnumber {
          display:none;
        }
}
</style>
