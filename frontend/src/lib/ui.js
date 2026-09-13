const paths = {
  shield: '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z"/><path d="m8 12 3 3 5-6"/>',
  dashboard:
    '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
  alert:
    '<path d="m10.3 4-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3l-8-14a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4m0 4h.01"/>',
  folder:
    '<path d="M3 7V5a2 2 0 0 1 2-2h5l2 3h7a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/><path d="M3 9h18"/>',
  users:
    '<circle cx="9" cy="8" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3m1-16a3 3 0 0 1 0 6m2 4a5 5 0 0 1 3 4v2"/>',
  settings:
    '<path d="M4 7h16M4 17h16"/><circle cx="8" cy="7" r="3"/><circle cx="16" cy="17" r="3"/>',
  arrow: '<path d="M5 12h14m-5-5 5 5-5 5"/>',
  chevron: '<path d="m9 5 7 7-7 7"/>',
  external:
    '<path d="M14 3h7v7m0-7L10 14M10 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-5"/>',
  refresh: '<path d="M20 7v5h-5M4 17v-5h5"/><path d="M6 6a8 8 0 0 1 13 2M5 16a8 8 0 0 0 13 2"/>',
  edit: '<path d="m16 3 5 5-13 13H3v-5Zm-2 2 5 5"/>',
  download: '<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
  database:
    '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 4 18 4 18 0V5M3 12c0 4 18 4 18 0"/>',
  route:
    '<circle cx="5" cy="5" r="2"/><circle cx="19" cy="19" r="2"/><path d="M7 5h9a4 4 0 0 1 0 8H8a3 3 0 0 0 0 6h9"/>',
  device: '<rect x="6" y="2" width="12" height="20" rx="3"/><path d="M10 18h4"/>',
  process:
    '<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="8" cy="6" r="2"/><circle cx="16" cy="12" r="2"/><circle cx="10" cy="18" r="2"/>',
  cpu: '<rect x="5" y="5" width="14" height="14" rx="3"/><rect x="9" y="9" width="6" height="6" rx="1"/><path d="M9 2v3m6-3v3M9 19v3m6-3v3M2 9h3m-3 6h3m14-6h3m-3 6h3"/>',
  layers: '<path d="m12 3 10 6-10 6L2 9Zm-10 12 10 6 10-6M2 12l10 6 10-6"/>',
  activity: '<path d="M2 12h5l3-8 4 16 3-8h5"/>',
  branch:
    '<circle cx="6" cy="4" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="6" cy="20" r="2"/><path d="M6 6v12m0-6h6a6 6 0 0 0 6-4"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  x: '<path d="m6 6 12 12M6 18 18 6"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  book: '<path d="M12 5C8 2 4 3 2 4v16c3-2 7-2 10 0 3-2 7-2 10 0V4c-3-2-7-2-10 1Zm0 0v15"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  minus: '<path d="M5 12h14"/>',
  fit: '<path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5"/>',
  search: '<circle cx="10" cy="10" r="7"/><path d="m15 15 6 6"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10h.01"/>',
  code: '<path d="m7 6-6 6 6 6m10-12 6 6-6 6M14 3l-4 18"/>',
  spark: '<path d="m12 3 3 6 6 3-6 3-3 6-3-6-6-3 6-3Z"/>',
};
export function icon(name, className = '') {
  return `<svg class="icon ${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name] || paths.layers}</svg>`;
}
export function escape(value) {
  return String(value ?? '').replace(
    /[&<>"']/g,
    (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char],
  );
}
export const number = (value) =>
  value == null ? '—' : new Intl.NumberFormat('vi-VN').format(value);
export const date = (value) =>
  value && !Number.isNaN(new Date(value).getTime())
    ? new Intl.DateTimeFormat('vi-VN', { dateStyle: 'short', timeStyle: 'short' }).format(
        new Date(value),
      )
    : 'Chưa có dữ liệu';
export const labels = {
  gps_spoofing: 'Giả mạo GPS',
  repeated_trips: 'Cuốc xe lặp lại',
  shared_device: 'Dùng chung thiết bị',
  promotion_abuse: 'Lạm dụng khuyến mãi',
  detected: 'Chờ review',
  under_review: 'Đang review',
  confirmed_fraud: 'Xác nhận gian lận',
  dismissed: 'Đã loại trừ',
  awaiting_driver_explanation: 'Chờ review (cũ)',
  driver_responded: 'Chờ review (cũ)',
  auto_clear: 'Auto Clear',
  auto_fraud: 'Auto Fraud',
  human_review: 'Human Review',
  active: 'Hoạt động',
  medium: 'Trung bình',
  high: 'Cao',
  low: 'Thấp',
  critical: 'Nghiêm trọng',
  unknown: 'Chưa xác định',
};
export function badge(value) {
  const tone = ['auto_clear', 'dismissed', 'active'].includes(value)
    ? 'green'
    : ['auto_fraud', 'confirmed_fraud', 'high', 'critical'].includes(value)
      ? 'red'
      : 'amber';
  return `<span class="badge ${tone}"><span class="dot"></span>${escape(labels[value] || value)}</span>`;
}
export function risk(value) {
  const score = Number.isFinite(value) ? Math.min(100, Math.max(0, value)) : 0;
  return `<span class="risk"><span class="risk-track"><span style="width:${score}%"></span></span><b>${number(value)}</b><span>/100</span></span>`;
}
let toastTimer;
export function toast(message) {
  const el = document.querySelector('#toast');
  el.textContent = message;
  el.classList.add('visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('visible'), 3600);
}
export function readLocal(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key)) ?? fallback;
  } catch {
    return fallback;
  }
}
export function writeLocal(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch {
    toast('Trình duyệt không cho phép lưu cài đặt.');
    return false;
  }
}
export function openDialog(title, content, subtitle = '') {
  const dialog = document.querySelector('#detail-dialog');
  dialog.innerHTML = `<header class="drawer-header"><div><span class="eyebrow">${escape(subtitle)}</span><h2 id="dialog-title">${escape(title)}</h2></div><button class="icon-button" data-close aria-label="Đóng">${icon('x')}</button></header><div class="drawer-body">${content}</div>`;
  if (!dialog.open) dialog.showModal();
  dialog.querySelector('[data-close]').onclick = () => dialog.close();
  return dialog;
}
export function empty(
  message = 'Chưa có dữ liệu',
  detail = 'Dữ liệu sẽ xuất hiện sau khi hệ thống ghi nhận kết quả.',
) {
  return `<div class="empty">${icon('layers')}<h3>${escape(message)}</h3><p>${escape(detail)}</p></div>`;
}
