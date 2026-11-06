/* 校团委活动场地：新增/编辑流程中的链接改写
 * URL 带 ?type=tuanwei 时，表单模板步骤指向 57，审批流程步骤指向 62；
 * 带 &mode=edit 时，步骤间链接指向编辑页。
 * 页面也可调用 TuanweiFlow.apply(true/false) 动态切换（如基础信息切换场地类型）。 */
(function(){
  var params=new URLSearchParams(location.search);
  var editMode=params.get('mode')==='edit'||/^1[0-4]-venue-edit/.test(location.pathname.split('/').pop());
  var FORM='57-venue-add-form-tuanwei.html',APPROVAL='62-venue-add-approval-tuanwei.html';
  var ADD_MAP={'07-venue-add-form.html':FORM,'08-venue-add-approval.html':APPROVAL,'35-venue-add-approval-branch.html':APPROVAL};
  var EDIT_MAP={
    '05-venue-add-basic.html':'10-venue-edit-basic.html',
    '06-venue-add-timeslot.html':'11-venue-edit-timeslot.html',
    '07-venue-add-form.html':FORM,'12-venue-edit-form.html':FORM,
    '08-venue-add-approval.html':APPROVAL,'13-venue-edit-approval.html':APPROVAL,
    '09-venue-add-permission.html':'14-venue-edit-permission.html'
  };
  var FLOW=/^(0[5-9]|1[0-4]|3[1-9]|4[01]|57|58|60|62)-[\w-]+\.html$/;

  function links(){
    return Array.prototype.filter.call(document.querySelectorAll('a[href]'),function(a){
      if(a.closest('.sidebar')||a.closest('.breadcrumb')||a.closest('.tpl-select')){return false;}
      var h=a.dataset.origHref||a.getAttribute('href');
      return FLOW.test(h.split('?')[0]);
    });
  }
  function banner(on){
    var el=document.getElementById('tuanweiBanner');
    if(!on){if(el){el.remove();}return;}
    if(el){return;}
    var tabs=document.querySelector('.tabs');
    if(!tabs){return;}
    el=document.createElement('div');
    el.id='tuanweiBanner';
    el.style.cssText='margin:-8px 0 20px;padding:10px 14px;border-radius:8px;background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;font-size:12.5px;line-height:1.6';
    el.innerHTML='<b>场地类型：校团委活动场地</b>　时段配置与通用场地一致，可自由修改；表单模板与审批流程已自动套用团委预置配置。';
    tabs.parentNode.insertBefore(el,tabs.nextSibling);
  }
  function apply(on){
    links().forEach(function(a){
      if(!a.dataset.origHref){a.dataset.origHref=a.getAttribute('href');}
      var orig=a.dataset.origHref;
      if(!on){a.setAttribute('href',orig);return;}
      var base=orig.split('?')[0];
      base=(editMode?EDIT_MAP[base]:ADD_MAP[base])||base;
      a.setAttribute('href',base+'?type=tuanwei'+(editMode?'&mode=edit':''));
    });
    banner(on);
    if(on&&editMode){
      Array.prototype.forEach.call(document.querySelectorAll('.tabs .tab.disabled'),function(tab){tab.classList.remove('disabled');});
      var bc=document.querySelector('.breadcrumb');
      if(bc&&/新增场地/.test(bc.innerHTML)){bc.innerHTML=bc.innerHTML.replace('新增场地','编辑场地 · 毓秀楼和声堂');}
    }
  }
  var page=location.pathname.split('/').pop();
  window.TuanweiFlow={on:params.get('type')==='tuanwei'||page===FORM||page===APPROVAL,editMode:editMode,apply:apply};
  function init(){if(window.TuanweiFlow.on){apply(true);}}
  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',init);}else{init();}
})();
