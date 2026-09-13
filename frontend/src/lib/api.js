export class ApiError extends Error {
  constructor(message, status = 0) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export async function request(path, { signal, timeoutMs = 12000 } = {}) {
  const controller = new AbortController();
  const abort = () => controller.abort();
  signal?.addEventListener('abort', abort, { once: true });
  if (signal?.aborted) abort();
  const timer = setTimeout(abort, timeoutMs);
  try {
    const response = await fetch(`/api${path}`, {
      signal: controller.signal,
      cache: 'no-store',
      headers: { Accept: 'application/json' },
    });
    if (!response.ok) {
      throw new ApiError(
        response.status === 404
          ? 'Không tìm thấy bản ghi.'
          : 'Không tải được dữ liệu. Kiểm tra backend, PostgreSQL và migration rồi thử lại.',
        response.status,
      );
    }
    return await response.json();
  } catch (error) {
    if (signal?.aborted) throw new DOMException('Đã hủy yêu cầu', 'AbortError');
    if (error instanceof ApiError) throw error;
    throw new ApiError(
      controller.signal.aborted
        ? 'Máy chủ phản hồi quá lâu. Vui lòng thử lại.'
        : 'Chưa kết nối được backend. Kiểm tra máy chủ rồi thử lại.',
    );
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', abort);
  }
}

// The API has no aggregate endpoint. Bound requests and expose truncation in the UI.
export async function loadCollection(path, { signal, pageSize = 200, maxPages = 10 } = {}) {
  const items = [];
  for (let page = 0; page < maxPages; page++) {
    const separator = path.includes('?') ? '&' : '?';
    const batch = await request(`${path}${separator}limit=${pageSize}&offset=${page * pageSize}`, {
      signal,
    });
    if (!Array.isArray(batch)) throw new ApiError('Phản hồi danh sách không hợp lệ.');
    items.push(...batch);
    if (batch.length < pageSize) return { items, truncated: false };
  }
  return { items, truncated: true };
}

export const endpoints = {
  drivers: '/drivers',
  alerts: '/fraud-alerts',
  cases: '/fraud-cases',
  queue: '/review-queue',
};
