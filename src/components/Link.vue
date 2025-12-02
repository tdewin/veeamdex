<script setup>
 import { computed } from 'vue'
 const props = defineProps({
    link: {
      required: true,
    },
    deepquery: {
      required: true,
    },
    searchArr: {
      required: true,
    }
 })

 
const deepquerycalc = computed(() => {
        return props.link.deepquery.replace("$deepquery$",props.deepquery)
})

const addlinks = computed(() => {
        let sublinks = [];
        if (props.link.addlinks) {
          for (const al of props.link.addlinks) {
            let foundone = false;
            let searchArr= props.searchArr;
            let l = al.text.toLowerCase();
            for (let i =0;i < searchArr.length && !foundone;i++) { 
                  foundone = l.indexOf(searchArr[i]) != -1;
            }
            if (foundone) {
                  sublinks.push(al);
            } 
          }
        }
        return sublinks;
})

</script>

<template>
            <div class="linkdiv" v-if="link.link != ''">
                <div class="linktitle"> 
                        <div class="fasti" v-if="link.fasti">{{link.fasti}}</div>{{link.title}}
                </div>
                <div>{{link.description}}</div>
                <a :href="link.link" v-if="!link.deepquery || deepquery == ''">{{link.link}}</a>
                <a :href="deepquerycalc" v-else>{{deepquerycalc}}</a>
                <div v-if="addlinks.length > 0">
                <ul>        
                        <li v-for="al in addlinks"><a :href="al.href" >{{al.text}}</a></li>
                </ul>
                </div>
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
 position: relative;
}

.fasti {
display: inline-block;
min-width: 3rem;
height: 1.8rem;
font-size: 1.2rem;
border: 0.15rem solid var(--altgreen);
border-radius: 1rem;
margin-right: 0.5rem;
text-align: center;
}

@media screen and (max-width: 800px), screen and (max-height: 500px) {
 a,div {
  overflow-wrap: break-word;
 }
 .linkdiv {
   max-width: unset;
 }

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
