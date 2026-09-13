import { endpoints, request } from '../lib/api.js';
import { icon, escape, number, date, labels, badge, risk, empty } from '../lib/ui.js';
import { showRecord } from '../components/record-detail.js';

const PAGE_SIZE = 20;
const options = (values) =>
  values.map((value) => `<option value="${value}">${labels[value] || value}</option>`).join('');

export function mountRecords(target, type) {
  let controller;
  let offset = 0;
  let disposed = false;
  target.innerHTML = `<section class="panel records-panel"><form class="records-filters" id="record-filters"><div class="filter-title">${icon(type === 'drivers' ? 'users' : 'folder')}<strong>${type === 'queue' ? 'Sắp xếp theo rủi ro giảm dần' : 'Danh sách bản ghi'}</strong></div><div class="filter-controls">${['alerts', 'cases'].includes(type) ? '<label>Mã ID tài xế<input name="driver_id" type="number" min="1" step="1" placeholder="Ví dụ: 1"></label>' : ''}${type === 'cases' ? `<label>Trạng thái<select name="status"><option value="">Tất cả trạng thái</option>${options(['detected', 'under_review', 'confirmed_fraud', 'dismissed', 'awaiting_driver_explanation', 'driver_responded'])}</select></label><label>Loại dấu hiệu<select name="fraud_type"><option value="">Tất cả dấu hiệu</option>${options(['gps_spoofing', 'repeated_trips', 'shared_device', 'promotion_abuse'])}</select></label>` : ''}${type === 'alerts' ? `<label>Phân luồng<select name="outcome"><option value="">Tất cả kết quả</option>${options(['auto_clear', 'auto_fraud', 'human_review'])}</select></label>` : ''}${['alerts', 'cases'].includes(type) ? '<button class="button primary" type="submit">Áp dụng</button><button class="button" type="button" data-reset>Đặt lại</button>' : ''}</div></form><div id="records-content" aria-live="polite"></div><div class="pagination"><span id="page-label"></span><div><button class="button" id="previous" aria-label="Trang trước">${icon('chevron', 'rotate')}Trước</button><button class="button" id="next" aria-label="Trang sau">Sau${icon('chevron')}</button></div></div></section>`;
  const form = target.querySelector('#record-filters');
  const previous = target.querySelector('#previous');
  const next = target.querySelector('#next');
  const content = target.querySelector('#records-content');
  async function load() {
    controller?.abort();
    controller = new AbortController();
    const active = controller;
    previous.disabled = true;
    next.disabled = true;
    content.innerHTML = empty('Đang tải dữ liệu…', 'Đang truy xuất bản ghi từ hệ thống.');
    target.querySelector('#page-label').textContent = `Trang ${offset / PAGE_SIZE + 1}`;
    const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(offset) });
    for (const [name, value] of new FormData(form)) if (value) params.set(name, value);
    try {
      const rows = await request(`${endpoints[type]}?${params}`, { signal: active.signal });
      if (disposed || active.signal.aborted) return;
      if (!Array.isArray(rows)) throw new Error('Phản hồi danh sách không hợp lệ.');
      content.innerHTML = rows.length
        ? table(rows, type)
        : empty(
            offset ? 'Đã đến cuối danh sách' : 'Không có bản ghi phù hợp',
            offset
              ? 'Quay lại trang trước để xem các bản ghi đã tải.'
              : 'Thử thay đổi bộ lọc hoặc chạy pipeline phát hiện nếu chưa có dữ liệu.',
          );
      target.querySelector('#page-label').textContent = rows.length
        ? `Bản ghi ${number(offset + 1)}–${number(offset + rows.length)} · Trang ${offset / PAGE_SIZE + 1}`
        : `Trang ${offset / PAGE_SIZE + 1}`;
      previous.disabled = offset === 0;
      next.disabled = rows.length < PAGE_SIZE;
      content.querySelectorAll('[data-record]').forEach((button) => {
        button.onclick = () => showRecord(type, Number(button.dataset.record));
      });
    } catch (error) {
      if (disposed || active.signal.aborted) return;
      content.innerHTML = `${empty('Chưa tải được danh sách', error.message)}<div class="retry-wrap"><button class="button" id="retry">${icon('refresh')}Thử lại</button></div>`;
      content.querySelector('#retry').onclick = load;
      previous.disabled = offset === 0;
    }
  }
  form.onsubmit = (event) => {
    event.preventDefault();
    offset = 0;
    load();
  };
  target.querySelector('[data-reset]')?.addEventListener('click', () => {
    form.reset();
    offset = 0;
    load();
  });
  previous.onclick = () => {
    offset = Math.max(0, offset - PAGE_SIZE);
    load();
  };
  next.onclick = () => {
    offset += PAGE_SIZE;
    load();
  };
  load();
  return () => {
    disposed = true;
    controller?.abort();
  };
}

function table(rows, type) {
  const driver = type === 'drivers';
  const alert = type === 'alerts';
  return `<div class="table-scroll"><table><thead><tr>${(driver ? ['Mã tài xế', 'Họ tên', 'Trạng thái', 'Ngày tạo', ''] : [alert ? 'Cảnh báo' : 'Hồ sơ', 'Tài xế', 'Dấu hiệu', 'Rủi ro', alert ? 'Phân luồng' : 'Trạng thái', 'Ngày tạo', '']).map((header) => `<th>${header}</th>`).join('')}</tr></thead><tbody>${rows.map((row) => `<tr>${driver ? `<td><strong>${escape(row.external_driver_id)}</strong><small>ID: ${row.id}</small></td><td>${escape(row.name)}</td><td>${badge(row.status)}</td><td class="date-cell">${date(row.created_at)}</td>` : `<td><strong>${alert ? 'CB' : 'HS'}-${row.id}</strong></td><td>#${row.driver_id}</td><td>${row.fraud_types.map((value) => `<span class="fraud-type">${escape(labels[value] || value)}</span>`).join('')}</td><td>${risk(row.risk_score)}</td><td>${badge(alert ? row.decision_result.outcome : row.status)}</td><td class="date-cell">${date(row.created_at)}</td>`}<td><button class="icon-button" data-record="${row.id}" aria-label="Xem ${driver ? 'tài xế' : alert ? 'cảnh báo' : 'hồ sơ'} ${row.id}">${icon('arrow')}</button></td></tr>`).join('')}</tbody></table></div>`;
}
