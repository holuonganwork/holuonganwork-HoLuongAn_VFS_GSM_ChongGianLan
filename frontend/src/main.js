import './styles.css';
import './styles-responsive.css';
import { icon, escape } from './lib/ui.js';
import { request } from './lib/api.js';
import { mountDashboard } from './pages/dashboard.js';
import { mountRecords } from './pages/records.js';

const routes = {
  dashboard: { title: 'Tổng quan hệ thống', label: 'Dashboard', icon: 'dashboard' },
  alerts: { title: 'Cảnh báo gian lận', label: 'Cảnh báo', icon: 'alert' },
  queue: { title: 'Hàng chờ review', label: 'Hàng chờ review', icon: 'clock' },
  cases: { title: 'Hồ sơ điều tra', label: 'Hồ sơ điều tra', icon: 'folder' },
  drivers: { title: 'Dữ liệu tài xế', label: 'Tài xế', icon: 'users' },
};

document.querySelector('#app').innerHTML = `
  <aside class="sidebar" aria-label="Thanh điều hướng">
    <a class="brand" href="#dashboard"><span class="brand-mark">${icon('shield')}</span><span>FraudLens<small>DRIVER INTELLIGENCE</small></span></a>
    <div class="workspace"><span class="workspace-avatar">FL</span><div>Fraud Investigation<small>Không gian làm việc nội bộ</small></div><span class="workspace-dot"></span></div>
    <span class="nav-caption">KHÔNG GIAN LÀM VIỆC</span>
    <nav>${Object.entries(routes)
      .map(
        ([id, route]) =>
          `<a href="#${id}" data-route="${id}">${icon(route.icon)}<span>${route.label}</span>${id === 'dashboard' ? '<span class="nav-active-dot"></span>' : ''}</a>`,
      )
      .join('')}</nav>
    <div class="sidebar-bottom"><div class="scope-card">${icon('layers')}<strong>Hiểu rõ từng quyết định.</strong><p>Từ tín hiệu ban đầu đến bằng chứng và kết quả xử lý.</p><a href="#dashboard">Khám phá kiến trúc ${icon('arrow')}</a></div>
    <div class="environment"><span class="dot"></span><span>Môi trường local</span><code>v0.1</code></div></div>
  </aside>
  <div class="main-shell">
    <header class="topbar"><div class="breadcrumb">${icon('shield')}<span>Fraud Investigation</span>${icon('chevron')}<strong id="breadcrumb-page"></strong></div><div class="topbar-right"><span id="connection" class="connection" role="status"><span class="dot"></span>Đang kiểm tra API</span><span class="topbar-divider"></span><span class="avatar" aria-label="Không gian kiểm soát nội bộ">KS</span></div></header>
    <main id="main" tabindex="-1"></main>
    <footer class="app-footer"><span>FraudLens <span class="footer-dot">·</span> Driver Fraud Investigation System</span><span>Signals → Decisions → Evidence</span></footer>
  </div>`;

let cleanup;
let healthController;
async function render() {
  cleanup?.();
  healthController?.abort();
  healthController = new AbortController();
  const controller = healthController;
  const route = Object.hasOwn(routes, location.hash.slice(1))
    ? location.hash.slice(1)
    : 'dashboard';
  const meta = routes[route];
  document.title = `FraudLens · ${meta.title}`;
  document.querySelector('#breadcrumb-page').textContent = meta.label;
  document.querySelectorAll('[data-route]').forEach((link) => {
    if (link.dataset.route === route) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
  const target = document.querySelector('#main');
  target.innerHTML = `<section class="page-heading"><div><span class="eyebrow">TRUNG TÂM KIỂM SOÁT GIAN LẬN</span><h1>${escape(meta.title)}</h1><p>${route === 'dashboard' ? 'Một góc nhìn xuyên suốt. Từ dữ liệu đến quyết định.' : 'Tra cứu dữ liệu và bằng chứng được ghi nhận bởi hệ thống.'}</p></div><button class="button" id="refresh">${icon('refresh')}Làm mới dữ liệu</button></section><div id="page-content"></div>`;
  document.querySelector('#refresh').onclick = render;
  cleanup =
    route === 'dashboard'
      ? mountDashboard(document.querySelector('#page-content'))
      : mountRecords(document.querySelector('#page-content'), route);
  const status = document.querySelector('#connection');
  status.className = 'connection';
  status.innerHTML = '<span class="dot"></span>Đang kiểm tra API';
  try {
    const health = await request('/health', { signal: controller.signal });
    if (health.status !== 'ok') throw new Error('Unhealthy');
    status.className = 'connection online';
    status.innerHTML = '<span class="dot"></span>API & database kết nối';
  } catch {
    if (controller.signal.aborted) return;
    status.className = 'connection offline';
    status.innerHTML = '<span class="dot"></span>Chưa kết nối API';
  }
}

window.addEventListener('hashchange', () => {
  document.querySelector('#detail-dialog').close();
  render();
});
document.querySelector('.skip-link').addEventListener('click', (event) => {
  event.preventDefault();
  document.querySelector('#main').focus();
  document.querySelector('#main').scrollIntoView();
});
document.querySelector('#detail-dialog').addEventListener('click', (event) => {
  if (event.target === event.currentTarget) {
    const bounds = event.currentTarget.getBoundingClientRect();
    if (
      event.clientX < bounds.left ||
      event.clientX > bounds.right ||
      event.clientY < bounds.top ||
      event.clientY > bounds.bottom
    )
      event.currentTarget.close();
  }
});
render();
