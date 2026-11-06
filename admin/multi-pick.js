/* 人员多选：<div class="mp" data-selected="孙瀚（综合办）,李明（民族办）"></div>
 * 初始化后 el.getValue() 返回已选数组，el.setValue(arr) 可改写。变更时冒泡 mp-change。 */
(function(){
  var PEOPLE=['孙瀚（综合办）','李明（民族办）','张华（思政办）','王芳（就业指导中心）','赵丽（心理中心）','陈伟（学生事务办）','刘洋（武装部）','王强（校团委）','聂天成（校团委）','胡新亮（校团委）','刘诚（保卫部）'];
  var css='.mp{position:relative}.mp-box{min-height:36px;padding:4px 26px 4px 8px;border:1px solid #e2e8f0;border-radius:8px;background:#fff;display:flex;flex-wrap:wrap;gap:4px;align-items:center;cursor:pointer}.mp-ph{color:#94a3b8;font-size:13px}.mp-chip{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:6px;background:#eef2ff;color:#4338ca;font-size:12.5px}.mp-chip b{cursor:pointer;color:#94a3b8;font-weight:400}.mp-panel{display:none;position:absolute;left:0;right:0;top:calc(100% + 4px);background:#fff;border:1px solid #e2e8f0;border-radius:8px;box-shadow:0 8px 24px rgba(15,23,42,.08);max-height:220px;overflow:auto;z-index:40;padding:6px}.mp.open .mp-panel{display:block}.mp-panel label{display:flex;align-items:center;gap:8px;padding:6px 8px;font-size:13px;border-radius:6px;cursor:pointer;font-weight:400}.mp-panel label:hover{background:#f8fafc}.mp-panel input{width:15px;height:15px;accent-color:#4f46e5;flex-shrink:0}.mp-arrow{position:absolute;right:10px;top:11px;color:#94a3b8;font-size:11px;pointer-events:none}';
  var st=document.createElement('style');st.textContent=css;document.head.appendChild(st);
  function init(el){
    if(el.dataset.ready){return;}
    el.dataset.ready='1';
    var selected=(el.getAttribute('data-selected')||'').split(',').map(function(s){return s.trim();}).filter(Boolean);
    el.innerHTML='<div class="mp-box"><span class="mp-chips"></span><span class="mp-ph">请选择，可多选</span></div><span class="mp-arrow">▾</span><div class="mp-panel">'+
      PEOPLE.map(function(p){return '<label><input type="checkbox" value="'+p+'">'+p+'</label>';}).join('')+'</div>';
    var panel=el.querySelector('.mp-panel');
    function render(){
      el.querySelector('.mp-chips').innerHTML=selected.map(function(p){return '<span class="mp-chip">'+p+'<b>×</b></span>';}).join('');
      el.querySelector('.mp-ph').style.display=selected.length?'none':'';
      Array.prototype.forEach.call(panel.querySelectorAll('input'),function(i){i.checked=selected.indexOf(i.value)>-1;});
      el.dispatchEvent(new CustomEvent('mp-change',{bubbles:true}));
    }
    el.querySelector('.mp-box').addEventListener('click',function(e){
      var chip=e.target.closest?e.target.closest('.mp-chip'):null;
      if(chip){selected=selected.filter(function(v){return v!==chip.textContent.replace('×','').trim();});render();return;}
      el.classList.toggle('open');
    });
    panel.addEventListener('click',function(e){e.stopPropagation();});
    panel.addEventListener('change',function(e){
      if(e.target.type!=='checkbox'){return;}
      var v=e.target.value;
      if(e.target.checked){if(selected.indexOf(v)<0){selected.push(v);}}
      else{selected=selected.filter(function(x){return x!==v;});}
      render();
    });
    document.addEventListener('click',function(e){if(!el.contains(e.target)){el.classList.remove('open');}});
    el.getValue=function(){return selected.slice();};
    el.setValue=function(arr){selected=arr.slice();render();};
    render();
  }
  function boot(){Array.prototype.forEach.call(document.querySelectorAll('.mp'),init);}
  boot();
  document.addEventListener('DOMContentLoaded',boot);
})();
