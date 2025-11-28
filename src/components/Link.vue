<script setup>
 import { computed } from 'vue'
 const props = defineProps({
    link: {
      required: true,
    },
    deepquery: {
      required: true,
    }
 })

 
const deepquerycalc = computed(() => {
        return props.link.deepquery.replace("$deepquery$",props.deepquery)
})

</script>

<template>
            <div class="linkdiv" v-if="link.link != ''">
                <div class="linktitle">{{link.title}}</div>
                <div>{{link.description}}</div>
                <a :href="link.link" v-if="!link.deepquery || deepquery == ''">{{link.link}}</a>
                <a :href="deepquerycalc" v-else>{{deepquerycalc}}</a>
            </div>
</template>

<style scoped>
.linkdiv {
 border: 0.10rem dashed var(--altgreen);
 border-radius:0.5rem;
 margin-bottom:0.5rem;
 padding:0.5rem;
 padding-left:0.5rem;
 max-width: var(--pagesize);
}
.linkdiv > a {
  font-size:0.8rem;

}
.linktitle {
  display:block;
  font-size:1.2rem;
  font-weight:600;
}
</style>
