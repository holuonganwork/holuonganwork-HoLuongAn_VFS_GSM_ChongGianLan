import { nodes, edges, stages, CANVAS_WIDTH } from '../config/architecture.js';
import { icon, escape, openDialog } from '../lib/ui.js';

function edgePath([from, to, orientation]) {
  const a = nodes.find((node) => node.id === from);
  const b = nodes.find((node) => node.id === to);
  if (orientation === 'vertical') {
    return `M ${a.x + a.w / 2} ${a.y + a.h} V ${b.y - 8}`;
  }
  const x1 = a.x + a.w,
    y1 = a.y + a.h / 2,
    x2 = b.x - 8,
    y2 = b.y + b.h / 2;
  return `M ${x1} ${y1} C ${x1 + 28} ${y1}, ${x2 - 28} ${y2}, ${x2} ${y2}`;
}

export function mountArchitecture(target) {
  let zoom = 1;
  let planned = false;
  let selected;
  target.innerHTML = `<div class="panel-heading"><div class="panel-title">${icon('branch')}<div><h2>Bản đồ kiến trúc</h2><p>Luồng phát hiện và xử lý gian lận</p></div></div><label class="switch-label"><input id="show-roadmap" type="checkbox" role="switch"><span class="switch-track"></span>Hiện lộ trình mở rộng</label></div>
    <div class="map-viewport" role="region" aria-label="Sơ đồ kiến trúc, có thể cuộn ngang" tabindex="0"><div class="map-sizer"><div class="map-canvas">
    ${stages.map((stage) => `<div class="stage" style="left:${stage.x}px"><span>${stage.label}</span>${stage.title}</div>`).join('')}
    <svg class="map-edges" width="1140" height="680" aria-hidden="true"><defs><marker id="arrowhead" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L8 4L0 8" fill="#a0b5b1"/></marker></defs>${edges.map((edge) => `<path data-edge="${edge[0]} ${edge[1]}" d="${edgePath(edge)}" marker-end="url(#arrowhead)"/>`).join('')}</svg>
    ${nodes.map((node) => `<button class="map-node ${node.tone || ''} ${node.planned ? 'planned' : ''}" data-node="${node.id}" style="left:${node.x}px;top:${node.y}px;width:${node.w}px;height:${node.h}px" aria-label="${escape(node.title)} — ${node.planned ? 'Dự kiến mở rộng' : 'Đã triển khai'}"><span class="node-header"><span class="node-icon">${icon(node.icon)}</span><span class="node-indicator"></span></span><strong>${escape(node.title)}</strong><small>${escape(node.description)}</small>${node.tag ? `<span class="node-tag">${escape(node.tag)}</span>` : ''}</button>`).join('')}
    <div class="map-storage">${icon('database')}<strong>PostgreSQL</strong><span>Dữ liệu gốc · Cảnh báo · Hồ sơ · Bằng chứng · Audit</span></div>
    <div class="roadmap-label planned"><span>LỘ TRÌNH MỞ RỘNG</span><span>Các thành phần dự kiến, chưa triển khai</span></div>
    </div></div></div>
    <div class="map-footer"><div class="map-legend"><span><i class="legend-dot"></i>Đã triển khai</span><span><i class="legend-dot planned-dot"></i>Dự kiến</span><span class="map-tip">Bấm vào thành phần để xem chi tiết</span></div><div class="zoom-controls"><button class="icon-button" data-zoom="out" aria-label="Thu nhỏ">${icon('minus')}</button><output id="zoom-value">100%</output><button class="icon-button" data-zoom="in" aria-label="Phóng to">${icon('plus')}</button><span></span><button class="icon-button" data-zoom="fit" aria-label="Vừa khung">${icon('fit')}</button></div></div>`;
  const viewport = target.querySelector('.map-viewport');
  const canvas = target.querySelector('.map-canvas');
  const sizer = target.querySelector('.map-sizer');
  function resize() {
    const scale = Math.max(0.72, Math.min(1, (viewport.clientWidth - 32) / CANVAS_WIDTH)) * zoom;
    canvas.style.transform = `scale(${scale})`;
    sizer.style.width = `${CANVAS_WIDTH * scale}px`;
    sizer.style.height = `${(planned ? 680 : 525) * scale}px`;
    canvas.classList.toggle('show-planned', planned);
    target.querySelector('#zoom-value').textContent = `${Math.round(scale * 100)}%`;
  }
  target.querySelector('#show-roadmap').onchange = (event) => {
    planned = event.target.checked;
    resize();
  };
  target.querySelectorAll('[data-zoom]').forEach((button) => {
    button.onclick = () => {
      zoom =
        button.dataset.zoom === 'fit'
          ? 1
          : Math.min(1.6, Math.max(0.8, zoom + (button.dataset.zoom === 'in' ? 0.1 : -0.1)));
      resize();
      if (button.dataset.zoom === 'fit') viewport.scrollTo({ left: 0 });
    };
  });
  target.querySelectorAll('[data-node]').forEach((button) => {
    button.onclick = () => {
      selected?.classList.remove('selected');
      selected = button;
      button.classList.add('selected');
      const node = nodes.find((item) => item.id === button.dataset.node);
      target
        .querySelectorAll('[data-edge]')
        .forEach((edge) =>
          edge.classList.toggle('highlighted', edge.dataset.edge.split(' ').includes(node.id)),
        );
      openDialog(
        node.title,
        `<div class="detail-hero ${node.tone || ''}">${icon(node.icon)}<span class="badge ${node.planned ? 'amber' : 'green'}">${node.planned ? 'Dự kiến mở rộng' : 'Đã triển khai'}</span></div><p class="detail-description">${escape(node.detail)}</p><dl class="detail-list"><div><dt>Đầu vào</dt><dd>${escape(node.input)}</dd></div><div><dt>Đầu ra</dt><dd>${escape(node.output)}</dd></div>${node.module ? `<div><dt>Module backend</dt><dd><code>backend/${escape(node.module)}</code></dd></div>` : ''}</dl><div class="info-note">${icon('info')}<p>Trạng thái trên sơ đồ mô tả phạm vi triển khai. Kết nối thực tế được kiểm tra riêng qua API.</p></div>`,
        'THÀNH PHẦN HỆ THỐNG',
      );
    };
  });
  const observer = new ResizeObserver(resize);
  observer.observe(viewport);
  resize();
  return () => observer.disconnect();
}
