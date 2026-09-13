import { loadCollection, endpoints } from '../lib/api.js';
import { icon, number, escape, badge, risk, empty, labels } from '../lib/ui.js';
import { mountArchitecture } from '../components/architecture-map.js';
import { showRecord } from '../components/record-detail.js';

const metrics = [
  {
    key: 'drivers',
    title: 'Tài xế trong hệ thống',
    icon: 'users',
    tone: 'blue',
    caption: 'Nguồn dữ liệu đầu vào',
  },
  {
    key: 'alerts',
    title: 'Cảnh báo đã ghi nhận',
    icon: 'alert',
    tone: 'teal',
    caption: 'Sau khi tổng hợp tín hiệu',
  },
  {
    key: 'queue',
    title: 'Hồ sơ cần review',
    icon: 'clock',
    tone: 'amber',
    caption: 'Ngoại lệ chờ đội kiểm soát',
  },
  {
    key: 'cases',
    title: 'Tổng hồ sơ điều tra',
    icon: 'folder',
    tone: 'purple',
    caption: 'Bao gồm hồ sơ đã xử lý',
  },
];

export function mountDashboard(target) {
  const controller = new AbortController();
  target.innerHTML = `<div class="dashboard-notice" role="status" hidden></div>
    <div class="metrics">${metrics.map((metric) => `<article class="metric-card"><div class="metric-heading"><span>${metric.title}</span><span class="metric-icon ${metric.tone}">${icon(metric.icon)}</span></div><strong data-metric="${metric.key}" class="metric-value" aria-label="Đang tải">—</strong><span class="metric-caption" data-caption="${metric.key}">${metric.caption}</span></article>`).join('')}</div>
    <section class="panel architecture-panel" id="architecture"></section>
    <div class="pipeline-note">${icon('info')}<p><strong>Giai đoạn hiện tại: phát hiện bằng quy tắc.</strong> Probability và confidence chưa được ước lượng; kết quả hiện được chuyển đến Human Review.</p><span class="version-pill">Modular monolith</span></div>
    <div class="dashboard-bottom"><section class="panel queue-panel"><div class="panel-heading"><div class="panel-title">${icon('clock')}<div><h2>Ưu tiên review</h2><p>Các hồ sơ có điểm rủi ro cao nhất trong hàng chờ</p></div></div><a href="#queue" class="text-link">Xem tất cả ${icon('arrow')}</a></div><div id="queue-preview">${empty('Đang tải hàng chờ…', 'Kết nối đến dữ liệu của hệ thống.')}</div></section>
    <section class="panel outcome-panel"><div class="panel-heading"><div class="panel-title">${icon('branch')}<div><h2>Phân luồng quyết định</h2><p>Kết quả chính sách trên các cảnh báo</p></div></div></div><div id="outcomes">${empty('Đang tải…', 'Auto Clear · Auto Fraud · Human Review')}</div></section></div>
    <section class="rules-strip"><div><span class="eyebrow">LỚP PHÁT HIỆN</span><h3>4 nhóm quy tắc hiện có</h3></div>${[
      ['route', 'gps_spoofing'],
      ['activity', 'repeated_trips'],
      ['device', 'shared_device'],
      ['spark', 'promotion_abuse'],
    ]
      .map(([symbol, type]) => `<span>${icon(symbol)}${labels[type]}</span>`)
      .join('')}</section>
    <div class="data-timestamp" id="data-timestamp">Đang tải dữ liệu từ API…</div>`;
  const cleanupMap = mountArchitecture(target.querySelector('#architecture'));
  let errors = 0;
  const tasks = metrics.map(async (metric) => {
    try {
      const collection = await loadCollection(endpoints[metric.key], { signal: controller.signal });
      if (controller.signal.aborted) return;
      const value = target.querySelector(`[data-metric="${metric.key}"]`);
      value.textContent = `${collection.truncated ? '≥ ' : ''}${number(collection.items.length)}`;
      value.removeAttribute('aria-label');
      if (collection.truncated)
        target.querySelector(`[data-caption="${metric.key}"]`).textContent =
          'Đã tải tối đa 2.000 bản ghi';
      if (metric.key === 'queue') {
        const rows = collection.items.slice(0, 5);
        target.querySelector('#queue-preview').innerHTML = rows.length
          ? `<div class="table-scroll"><table><thead><tr><th>Hồ sơ / Tài xế</th><th>Dấu hiệu</th><th>Rủi ro</th><th></th></tr></thead><tbody>${rows.map((item) => `<tr><td><strong>HS-${item.id}</strong><small>Tài xế #${item.driver_id}</small></td><td>${escape(labels[item.fraud_type] || item.fraud_type)}</td><td>${risk(item.risk_score)}</td><td><button class="icon-button" data-case="${item.id}" aria-label="Xem hồ sơ ${item.id}">${icon('arrow')}</button></td></tr>`).join('')}</tbody></table></div>`
          : empty('Hàng chờ trống', 'Hiện không có hồ sơ cần review.');
        target.querySelectorAll('[data-case]').forEach((button) => {
          button.onclick = () => showRecord('cases', Number(button.dataset.case));
        });
      }
      if (metric.key === 'alerts') renderOutcomes(target.querySelector('#outcomes'), collection);
    } catch (error) {
      if (controller.signal.aborted) return;
      errors++;
      target.querySelector(`[data-metric="${metric.key}"]`).removeAttribute('aria-label');
      target.querySelector(`[data-caption="${metric.key}"]`).textContent = 'Chưa tải được dữ liệu';
      if (metric.key === 'queue')
        target.querySelector('#queue-preview').innerHTML = empty(
          'Chưa tải được hàng chờ',
          error.message,
        );
      if (metric.key === 'alerts')
        target.querySelector('#outcomes').innerHTML = empty(
          'Chưa có dữ liệu quyết định',
          'Kết nối backend để xem kết quả thực tế.',
        );
      const notice = target.querySelector('.dashboard-notice');
      notice.hidden = false;
      notice.innerHTML = `${icon('info')}<p><strong>Một số dữ liệu chưa tải được.</strong> Kiểm tra backend và bấm “Làm mới dữ liệu”. Bạn vẫn có thể khám phá sơ đồ kiến trúc.</p>`;
    }
  });
  Promise.allSettled(tasks).then(() => {
    if (!controller.signal.aborted)
      target.querySelector('#data-timestamp').textContent =
        `${errors ? 'Tải dữ liệu chưa đầy đủ' : 'Dữ liệu từ API'} · Kiểm tra lúc ${new Date().toLocaleTimeString('vi-VN')} · Làm mới thủ công`;
  });
  return () => {
    controller.abort();
    cleanupMap();
  };
}

function renderOutcomes(target, { items, truncated }) {
  if (!items.length) {
    target.innerHTML = empty(
      'Chưa có quyết định',
      'Kết quả sẽ xuất hiện sau khi chạy phát hiện gian lận.',
    );
    return;
  }
  const counts = { auto_clear: 0, auto_fraud: 0, human_review: 0 };
  items.forEach((item) => {
    if (item.decision_result?.outcome in counts) counts[item.decision_result.outcome]++;
  });
  target.innerHTML = `<div class="outcome-total"><strong>${number(items.length)}</strong><span>cảnh báo ${truncated ? 'đã tải (tối đa 2.000)' : 'được phân luồng'}</span></div><div class="outcome-bar" aria-hidden="true">${Object.entries(
    counts,
  )
    .map(
      ([key, value]) =>
        `<span class="${key}" style="width:${(value / items.length) * 100}%"></span>`,
    )
    .join('')}</div><div class="outcome-rows">${Object.entries(counts)
    .map(
      ([key, value]) =>
        `<div>${badge(key)}<span><strong>${number(value)}</strong><small>${Math.round((value / items.length) * 100)}%</small></span></div>`,
    )
    .join(
      '',
    )}</div><p class="outcome-footnote">${truncated ? 'Tỷ lệ chỉ tính trên các cảnh báo đã tải.' : 'Điểm rủi ro độc lập với xác suất gian lận.'}</p>`;
}
