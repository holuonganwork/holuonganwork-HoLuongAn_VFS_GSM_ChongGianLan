import { request } from '../lib/api.js';
import { openDialog, escape, labels, badge, risk, date, empty, icon } from '../lib/ui.js';

let pending;
const field = (name, value) =>
  `<div><dt>${name}</dt><dd>${escape(value ?? 'Chưa xác định')}</dd></div>`;
const jsonDetails = (label, data) =>
  `<details class="json-detail"><summary>${escape(label)}</summary><pre>${escape(JSON.stringify(data, null, 2))}</pre></details>`;
const probability = (value) => (value == null ? 'Chưa ước lượng' : `${(value * 100).toFixed(1)}%`);

export async function showRecord(type, id) {
  pending?.abort();
  const controller = new AbortController();
  pending = controller;
  const path =
    type === 'drivers' ? '/drivers' : type === 'alerts' ? '/fraud-alerts' : '/fraud-cases';
  const title =
    type === 'drivers'
      ? `Tài xế #${id}`
      : type === 'alerts'
        ? `Cảnh báo CB-${id}`
        : `Hồ sơ HS-${id}`;
  const dialog = openDialog(
    title,
    empty('Đang tải chi tiết…', 'Đang truy xuất bản ghi từ hệ thống.'),
    'CHI TIẾT BẢN GHI',
  );
  const close = () => controller.abort();
  dialog.addEventListener('close', close, { once: true });
  try {
    const record = await request(`${path}/${id}`, { signal: controller.signal });
    if (controller.signal.aborted || !dialog.open) return;
    let content;
    if (type === 'drivers') {
      content = `<div class="record-summary">${badge(record.status)}<h3>${escape(record.name)}</h3></div><dl class="detail-list">${field('Mã tài xế', record.external_driver_id)}${field('ID dữ liệu', record.id)}${field('Ngày tạo', date(record.created_at))}${field('Cập nhật', date(record.updated_at))}</dl><a class="button" href="#cases">${icon('folder')}Tra cứu hồ sơ điều tra</a>`;
    } else if (type === 'alerts') {
      content = `<div class="record-summary">${badge(record.decision_result.outcome)}${risk(record.risk_score)}</div><dl class="detail-list">${field('Tài xế', `#${record.driver_id}`)}${field('Nhóm dấu hiệu', record.fraud_types.map((value) => labels[value] || value).join(', '))}${field('Probability', probability(record.fraud_probability))}${field('Confidence', probability(record.confidence))}${field('Mức tác động', labels[record.impact] || record.impact)}${field('Phiên bản mô hình', record.model_version)}${field('Chính sách', record.decision_result.policy_version)}${field('Thời điểm', date(record.created_at))}</dl><h3>Lý do phân luồng</h3><p class="detail-description">${escape(record.decision_result.reason)}</p>${jsonDetails('Tín hiệu và nguồn bằng chứng', record.signals)}${jsonDetails('Cấu hình quy tắc tại thời điểm phát hiện', record.rule_config)}${jsonDetails('Cấu hình chính sách tại thời điểm quyết định', record.decision_result.policy_config)}`;
    } else {
      content = `<div class="record-summary">${badge(record.status)}${risk(record.risk_score)}</div><dl class="detail-list">${field('Tài xế', `#${record.driver_id}`)}${field('Nhóm dấu hiệu', record.fraud_types.map((value) => labels[value] || value).join(', '))}${field('Ngày tạo', date(record.created_at))}${field('Cảnh báo liên kết', record.alert_id ? `CB-${record.alert_id}` : 'Hồ sơ lịch sử chưa liên kết')}</dl>
      <h3>Bằng chứng <span class="count-pill">${record.evidence.length}</span></h3>${record.evidence.map((evidence) => `<article class="evidence-card"><div>${badge(evidence.severity)}<span>#${evidence.id}</span></div><h4>${escape(labels[evidence.fraud_type] || evidence.fraud_type)}</h4><p>${escape(evidence.description)}</p>${jsonDetails('Dữ liệu bằng chứng', evidence.evidence_data)}<button class="text-link" data-source="${evidence.id}">Xem bản ghi nguồn ${icon('external')}</button><div class="source-records" data-source-content="${evidence.id}"></div></article>`).join('') || '<p>Chưa có bằng chứng.</p>'}
      <h3>Lịch sử xử lý</h3><div class="timeline">${record.status_events.map((event) => `<article><span class="timeline-dot"></span><strong>${escape(labels[event.to_status] || event.to_status)}</strong><small>${escape(date(event.created_at))} · ${escape(event.actor)}</small><p>${escape(event.reason)}</p></article>`).join('') || '<p class="muted">Chưa có thao tác review.</p>'}</div>${record.decisions.map((decision) => `<div class="decision-note">${badge(decision.decision)}<p>${escape(decision.reason)}</p><small>${escape(decision.reviewer)} · ${decision.actor_type === 'system' ? 'Hệ thống' : 'Người review'} · ${escape(date(decision.created_at))}</small></div>`).join('')}`;
    }
    dialog.querySelector('.drawer-body').innerHTML = content;
    dialog.querySelectorAll('[data-source]').forEach((button) => {
      button.onclick = async () => {
        button.disabled = true;
        const sourceTarget = dialog.querySelector(
          `[data-source-content="${button.dataset.source}"]`,
        );
        sourceTarget.textContent = 'Đang tải bản ghi nguồn…';
        try {
          const sources = await request(
            `/fraud-cases/${id}/evidence/${button.dataset.source}/sources`,
            { signal: controller.signal },
          );
          if (controller.signal.aborted) return;
          sourceTarget.innerHTML =
            sources
              .map((source) =>
                jsonDetails(`${source.source_type} #${source.source_id}`, source.data),
              )
              .join('') || '<p>Chưa có bản ghi nguồn.</p>';
        } catch (error) {
          if (!controller.signal.aborted) sourceTarget.textContent = error.message;
        } finally {
          button.disabled = false;
        }
      };
    });
  } catch (error) {
    if (!controller.signal.aborted && dialog.open)
      dialog.querySelector('.drawer-body').innerHTML = empty(
        'Chưa tải được bản ghi',
        error.message,
      );
  }
}
