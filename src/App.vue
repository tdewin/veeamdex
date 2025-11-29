<script setup>
import Search from './components/Search.vue'
import Link from './components/Link.vue'
import LinkBar from './components/LinkBar.vue'
import jsonLinkData from './data/links.json'
import jsonBlogs from './data/blogs.json'
import jsonCommunity from './data/community.json'
import jsonHelpcenter from './data/helpcenter.json'
import jsonForums from './data/forums.json'
import jsonKB from './data/kb.json'
import jsonVeeamhub from './data/veeamhub.json'
import jsonBP from './data/bp.json'

import { ref } from 'vue'
import { computed } from 'vue'

const search = ref("");
const deepquery = ref("");
const searchArr = ref([]);

let linkDataSource = [...jsonBP,...jsonLinkData,...jsonBlogs,...jsonVeeamhub,...jsonCommunity,...jsonKB,...jsonForums,...jsonHelpcenter];

console.time('buildindex')
for (const cat of linkDataSource) {
  for (const l of cat.catlinks) {
    let tags = cat.cattags || [];
    let addlinks = (l.addlinks || []).map((m)=> m.text);
    l.index = [...tags,cat.catname,l.title,l.description,l.link,...addlinks].join(" ").split(" ").filter((word) => word.length > 1).join(" ").toLowerCase();
  }
}
console.timeEnd('buildindex')

const linkData = computed(() => {
        if (searchArr.value.length > 0 || deepquery.value != "") {
                var filtered = []
                for (const cat of linkDataSource) {
                       var links = []
                       for (const l of cat.catlinks) {
                          let allfound = true;
                          for (let i =0;i < searchArr.value.length && allfound;i++) { 
                                allfound = l.index.indexOf(searchArr.value[i]) != -1;
                          }
                          if (allfound && (deepquery.value == "" || l.deepquery)) {
                                links.push(l);
                          }  
                       }
                       const recat = {"catname":cat.catname,"catlinks":links}
                       if (links.length > 0 ) {
                         filtered.push(recat);
                       }

                }
                return filtered;
        } else {
                return linkDataSource
        }
});

function searchChange(q) {
  let deepsearch = q.split("q=");
  search.value = q;
  let splitq = deepsearch[0].split(" ").filter((word) => word.length > 1).map((x) => x.toLowerCase());

  if (deepsearch.length > 1)
  {
        deepquery.value = encodeURI(deepsearch[1].trim());
  }
  searchArr.value = splitq
}

</script>

<script>
</script>

<template>
  <div class="centerpage">
      <div class="side-panel"></div>
      <div class="pagesizer" id="logo"> 
        <div id="header-logo"></div>
        <p style="align-self:center;margin:0px;padding:0px;">Jump to search field with "/", append q= to pass parameter to the next site. eg."kb q=tape" or "deepq q=tape"<br/>
        <span style="display:none;font-size:0.6rem;" id="smallgithub"><a href="https://github.com/tdewin/veeamdex">github.com/tdewin/veeamdex</a></span></p>
      </div>
      <div class="side-panel"></div>
  </div>
  <header>
      <div class="side-panel"></div>
      <div class="pagesizer" id="topnav">
        <Search :search="search" @changed="searchChange" />

        <LinkBar :linkData="linkData" />
      </div>
      <div class="side-panel"></div>
  </header>
  <main>
      <div class="side-panel"></div>
      <div class="pagesizer stack">
        <div v-for="cat in linkData">
          <div class="ref" :id="'cat-'+cat.catname.replace(' ','_')" ></div>
          <div >
            <div><h1>{{cat.catname}}</h1></div>
            <template v-for="link in cat.catlinks">
                <Link :link="link" :deepquery="deepquery" :searchArr="searchArr"/>
            </template>
          </div>
        </div>
        <div id="bottom-spacer" class="spacer"></div>
      </div>
      <div class="side-panel"></div>
  </main>
  <footer>
      <div class="side-panel"></div>
      <div class="pagesizer footer-content">
<div>
<a href="https://github.com/tdewin/veeamdex"><span id="github-logo"></span><span id="github-text">https://github.com/tdewin/veeamdex</span></a></div>
</div>
      <div class="side-panel"></div>
  </footer>
</template>

<style scoped>
.side-panel {
  flex-grow:1;
  min-width:1rem;
}
.pagesizer {
  display:flex;
  max-width: var(--pagesize);
  flex-grow:50;
  flex-direction: column;
}

#header-logo {
  display:block;
  margin-right:0.5rem;
  height: 20rem;
  width: 20rem;
  background-image:url("@/assets/veeamdex_plain.svg");
  background-size:contain;
  background-repeat:no-repeat;
  align-self: center;
}
#github-text {
  position: relative;
  bottom: 0.1rem;
}
#github-logo {
  display:inline-block;
  height: 0.5rem;
  width: 0.5rem;
  background-image:url("@/assets/github.svg");
  background-size:contain;
  background-repeat:no-repeat;
  align-self: center;
  margin-right: 0.5rem;
  margin-left: 0.5rem;
  background-color:var(--white);
  border: 0.01rem solid var(--white);
  border-radius: 0.3rem;

}
#logo  span {
  font-size:3rem;
}
@media screen and (max-width: 800px), screen and (max-height: 700px) {
        #logo {
                flex-direction: row;
        }
        #logo p {
          display: inline-block;
          min-width: 10rem;
          flex-grow:10;
        }
        #logo #header-logo {
          display: inline-block;
          flex-grow:1;
          min-width:8rem;
          max-width:12rem;
          height:unset;
          aspect-ratio: 1 / 1; 
          background-position: center;
        }
        .pagesizer {
          max-width: 95vw;
        }
        .side-panel {
          min-width: unset;
        }
        header {
          position:fixed !important;
          bottom: 0rem;
          top: unset !important;
          padding: 0.1rem !important;
        }
        footer {
          display:none !important;
        }
        #smallgithub {
          display:block !important;
        }
        #bottom-spacer {
          height:11rem;
        }
}
.spacer {
  display: block;
  min-height: 3rem;
}
.centerpage {
  display:flex;
  width: 100%;
}
header {
  display:flex;
  width: 100%;
  position: sticky;
  z-index: 999;
  top: 0rem;
  background-color: var(--color-background);
}
main {
  display:flex;
  width: 100%;
}
footer {
  display:flex;
  align-items: flex-end;
  position: fixed;
  z-index: 999;
  bottom: 0rem;
  left: 0rem;
  width: 100%;
  background-color: var(--color-background);
  flex-direction: row;
  justify-content: center;

}
.footer-content {
  vertical-align: top;
  padding-top:0.2rem;
  padding-bottom: -0.2rem;
  background-color: var(--color-background);
  color: var(--color-text);
  flex-direction:row;
  border-top: 0.1rem solid #88888822;
  font-size:xx-small;
}
.footer-content a {
  background-color: var(--color-background);
  color: var(--color-text);
  text-decoration: none;
}
.stack {
  display:flex;
  flex-direction: column;
}
</style>
