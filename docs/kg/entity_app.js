var COLORS={星:"#FFD700",官:"#7DC2B2",曜:"#F49B8A",象:"#FF6B6B",神:"#C9A96E",州:"#7EB8DA",岁:"#6B8DB5",器:"#D4A574",历:"#B39DDB"};
function esc(s){var d=document.createElement("div");d.textContent=s;return d.innerHTML;}
function highlightName(text,name){return text.split(name).join('<mark style="background:rgba(201,169,110,0.25);color:#c9a96e;padding:0 2px;border-radius:2px">'+esc(name)+'</mark>');}
(function(){
var m=window.location.search.match(/[?&]name=([^&]+)/);
if(!m){document.getElementById("content").innerHTML='<p class="notfound">缺少名称参数</p>';return;}
var name=decodeURIComponent(m[1]),ent=null;
var all=window.ENTITIES||[];
for(var i=0;i<all.length;i++){if(all[i].name===name){ent=all[i];break;}}
if(!ent){document.getElementById("content").innerHTML='<p class="notfound">未找到：'+esc(name)+'</p>';return;}

var URLS=window.BOOK_URLS||{};
var srcBook=null;
var rm=window.location.search.match(/[?&]ref=([^&]+)/);
if(rm){
  var refFile=decodeURIComponent(rm[1]);
  for(var bk in URLS){
    if(URLS[bk].indexOf(refFile)!==-1){srcBook=bk;break;}
  }
}

// Header
var h='<h1>'+esc(ent.name)+'</h1>';
h+='<div class="meta"><span class="badge badge-'+ent.type+'" style="font-size:0.8rem">'+ent.type_cn+'</span>';
h+='共出现 <strong>'+ent.total+'</strong> 次，分布在 <strong>'+ent.book_count+'</strong> 部古籍中</div>';

// Book distribution
h+='<div class="section"><h2>跨书分布</h2><div class="book-list">';
var books=Object.keys(ent.books).sort(function(a,b){return ent.books[b]-ent.books[a];});
books.forEach(function(b){
  var u=URLS[b]||"#";
  var cls=(b===srcBook)?'book-item current':'book-item';
  h+='<a href="'+u+'" class="'+cls+'" target="_blank">'+esc(b)+' <span class="book-count">'+ent.books[b]+'</span></a>';
});
h+='</div></div>';

// Contexts section: 1 from current book + 4 from others = 5 max
if(ent.contexts&&ent.contexts.length>0){
  var ctxs=ent.contexts;
  var curCtxs=[], otherCtxs=[];
  ctxs.forEach(function(c){
    if(c.book===srcBook) curCtxs.push(c);
    else otherCtxs.push(c);
  });

  h+='<div class="section"><h2>原文语境 <span style="font-size:0.75rem;color:var(--text-muted);font-weight:normal">（共'+ctxs.length+'条，点击跳转到出处）</span></h2>';

  // 1 from current book
  if(srcBook&&curCtxs.length>0){
    h+='<div class="ctx-label" style="color:var(--accent-gold);font-size:0.8rem;margin-bottom:4px;font-weight:600">▸ '+esc(srcBook)+'（当前书籍）</div>';
    var c=curCtxs[0];
    var chUrl=(URLS[c.book]||"") + (c.para_id ? '#'+c.para_id : '');
    h+='<div class="ctx-item current-book" onclick="window.open(\''+chUrl+'\')" style="cursor:pointer" title="点击跳转到原文"><span class="ctx-seq">#'+c.seq+'</span>'+highlightName(esc(c.text),name)+'</div>';
  }

  // Up to 4 from other books
  var shownOthers=otherCtxs.slice(0,4);
  if(shownOthers.length>0){
    if(srcBook&&curCtxs.length>0){
      h+='<div class="ctx-label" style="color:var(--text-muted);font-size:0.8rem;margin:12px 0 4px;font-weight:600">▸ 其他书籍</div>';
    }
    shownOthers.forEach(function(c){
      var chUrl=(URLS[c.book]||"") + (c.para_id ? '#'+c.para_id : '');
      h+='<div class="ctx-item" onclick="window.open(\''+chUrl+'\')" style="cursor:pointer" title="点击跳转到原文"><span class="ctx-seq">#'+c.seq+'</span>'+highlightName(esc(c.text),name)+' <small>('+esc(c.book)+')</small></div>';
    });
    if(otherCtxs.length>4){
      h+='<div class="ctx-more" style="text-align:center;color:var(--text-muted);font-size:0.78rem;padding:8px">… 还有 '+(otherCtxs.length-4)+' 条来自其他书籍的上下文</div>';
    }
  }
  h+='</div>';
}

document.getElementById("content").innerHTML=h;

// Back link
if(rm){
  var ref=decodeURIComponent(rm[1]),bk=document.getElementById("back-link");
  if(bk){
    bk.href="../chapters/"+ref;
    bk.textContent="\u2190 返回原文";
  }
}
})();
