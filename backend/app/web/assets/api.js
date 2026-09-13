export class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status; }
}
export async function request(path, {method = 'GET', body, signal} = {}) {
  const timeout = new AbortController();
  const timer = setTimeout(() => timeout.abort(), 12000);
  const abort = () => timeout.abort();
  signal?.addEventListener('abort', abort, {once:true});
  if (signal?.aborted) abort();
  try {
    const response = await fetch(path, {
      method, signal: timeout.signal, cache:'no-store',
      headers: {Accept:'application/json', ...(body ? {'Content-Type':'application/json'} : {})},
      ...(body ? {body:JSON.stringify(body)} : {}),
    });
    if (!response.ok) {
      const message = response.status === 409 ? 'Hồ sơ đã thay đổi trạng thái. Vui lòng đóng và mở lại để cập nhật.'
        : response.status === 404 ? 'Không tìm thấy bản ghi này.'
        : response.status === 422 ? 'Thông tin chưa hợp lệ. Vui lòng kiểm tra lại.'
        : 'Không thể tải dữ liệu. Kiểm tra backend, PostgreSQL và migration rồi thử lại.';
      throw new ApiError(message, response.status);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(error.name === 'AbortError' ? 'Yêu cầu đã dừng hoặc quá thời gian chờ. Vui lòng thử lại.' : 'Không kết nối được với máy chủ. Vui lòng thử lại.', 0);
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', abort);
  }
}

