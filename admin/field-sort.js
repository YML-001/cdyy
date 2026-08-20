/* 表单字段列表的拖拽排序：作用于所有 .field-list 中的 .field-row（表头 .header 除外） */
(function () {
  var STYLE = [
    '.field-row .drag{cursor:grab;user-select:none}',
    '.field-row .drag:active{cursor:grabbing}',
    '.field-row:hover .drag{color:#4f46e5}',
    '.field-row .drag:focus{outline:2px solid #c7d2fe;outline-offset:1px;border-radius:4px}',
    '.field-row.dragging{opacity:.45;background:#eef2ff}',
    '.field-row.drop-before{box-shadow:inset 0 3px 0 0 #4f46e5;background:#f8faff}',
    '.field-row.drop-after{box-shadow:inset 0 -3px 0 0 #4f46e5;background:#f8faff}',
    '.field-row.just-moved{animation:fieldMoved .9s ease-out}',
    '@keyframes fieldMoved{from{background:#eef2ff}to{background:transparent}}',
    '.sort-toast{position:fixed;left:50%;bottom:32px;transform:translateX(-50%);background:#0f172a;color:#fff;',
    'font-size:13px;padding:9px 18px;border-radius:8px;z-index:999;opacity:0;transition:opacity .2s;pointer-events:none}',
    '.sort-toast.show{opacity:.92}'
  ].join('');

  var toastEl, toastTimer;

  function injectStyle() {
    var s = document.createElement('style');
    s.textContent = STYLE;
    document.head.appendChild(s);
  }

  function toast(msg) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.className = 'sort-toast';
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('show'); }, 1800);
  }

  function sortableRows(list) {
    return Array.prototype.filter.call(list.children, function (el) {
      return el.classList.contains('field-row') && !el.classList.contains('header');
    });
  }

  function nameOf(row) {
    var n = row.querySelector('.fname');
    return n ? n.textContent.trim() : '字段';
  }

  function announce(list, row) {
    var rows = sortableRows(list);
    row.classList.remove('just-moved');
    void row.offsetWidth; // 重新触发高亮动画
    row.classList.add('just-moved');
    toast('「' + nameOf(row) + '」已移到第 ' + (rows.indexOf(row) + 1) + ' 位，保存后生效');
  }

  function clearMarks(list) {
    sortableRows(list).forEach(function (r) {
      r.classList.remove('drop-before', 'drop-after');
    });
  }

  function setupList(list) {
    if (list.dataset.sortable === '1') { return; }
    list.dataset.sortable = '1';

    var dragging = null;

    function bindRow(row) {
      if (row.dataset.sortBound === '1') { return; }
      row.dataset.sortBound = '1';

      var handle = row.querySelector('.drag');
      // 仅从拖拽手柄发起拖动，避免选中文字时误触
      row.draggable = false;
      if (handle) {
        handle.setAttribute('tabindex', '0');
        handle.setAttribute('title', '拖动调整顺序（也可用 ↑ ↓ 键移动）');
        handle.addEventListener('mousedown', function () { row.draggable = true; });
        handle.addEventListener('keydown', function (e) {
          if (e.key !== 'ArrowUp' && e.key !== 'ArrowDown') { return; }
          e.preventDefault();
          var sib = e.key === 'ArrowUp' ? row.previousElementSibling : row.nextElementSibling;
          if (!sib || sib.classList.contains('header') || !sib.classList.contains('field-row')) { return; }
          if (e.key === 'ArrowUp') { list.insertBefore(row, sib); }
          else { list.insertBefore(sib, row); }
          handle.focus();
          announce(list, row);
        });
      }

      row.addEventListener('dragstart', function (e) {
        dragging = row;
        row.classList.add('dragging');
        if (e.dataTransfer) {
          e.dataTransfer.effectAllowed = 'move';
          e.dataTransfer.setData('text/plain', nameOf(row));
        }
      });

      row.addEventListener('dragend', function () {
        row.classList.remove('dragging');
        row.draggable = false;
        clearMarks(list);
        if (dragging) { announce(list, dragging); }
        dragging = null;
      });

      function markTarget(e) {
        if (!dragging || dragging === row) { return; }
        e.preventDefault();
        if (e.dataTransfer) { e.dataTransfer.dropEffect = 'move'; }
        var rect = row.getBoundingClientRect();
        var before = e.clientY < rect.top + rect.height / 2;
        clearMarks(list);
        row.classList.add(before ? 'drop-before' : 'drop-after');
      }

      // dragenter 与 dragover 都要标记：鼠标停住不动时浏览器可能不再派发 dragover
      row.addEventListener('dragenter', markTarget);
      row.addEventListener('dragover', markTarget);

      row.addEventListener('dragleave', function (e) {
        // 在同一行的子元素之间移动也会冒泡出 dragleave，需排除，否则指示线会闪断
        if (e.relatedTarget && row.contains(e.relatedTarget)) { return; }
        row.classList.remove('drop-before', 'drop-after');
      });

      row.addEventListener('drop', function (e) {
        if (!dragging || dragging === row) { return; }
        e.preventDefault();
        e.stopPropagation();
        var rect = row.getBoundingClientRect();
        if (e.clientY < rect.top + rect.height / 2) { list.insertBefore(dragging, row); }
        else { list.insertBefore(dragging, row.nextSibling); }
        clearMarks(list);
      });
    }

    sortableRows(list).forEach(bindRow);

    // 新增字段后自动接管新行
    new MutationObserver(function () {
      sortableRows(list).forEach(bindRow);
    }).observe(list, { childList: true });
  }

  function init() {
    injectStyle();
    Array.prototype.forEach.call(document.querySelectorAll('.field-list'), setupList);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
