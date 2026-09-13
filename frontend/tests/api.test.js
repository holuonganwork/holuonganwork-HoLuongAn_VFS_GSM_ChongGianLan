import { afterEach, test, mock } from 'node:test';
import assert from 'node:assert/strict';
import { loadCollection, request, ApiError } from '../src/lib/api.js';

afterEach(() => mock.restoreAll());

test('aggregates pages and preserves endpoint filters', async () => {
  const paths = [];
  mock.method(globalThis, 'fetch', async (path) => {
    paths.push(path);
    return Response.json(paths.length === 1 ? [{ id: 1 }, { id: 2 }] : [{ id: 3 }]);
  });
  assert.deepEqual(await loadCollection('/fraud-alerts?outcome=human_review', { pageSize: 2 }), {
    items: [{ id: 1 }, { id: 2 }, { id: 3 }],
    truncated: false,
  });
  assert.deepEqual(paths, [
    '/api/fraud-alerts?outcome=human_review&limit=2&offset=0',
    '/api/fraud-alerts?outcome=human_review&limit=2&offset=2',
  ]);
});

test('exposes a bounded count instead of presenting a partial total as complete', async () => {
  const fetch = mock.method(globalThis, 'fetch', async () => Response.json([{ id: 1 }]));
  const result = await loadCollection('/drivers', { pageSize: 1, maxPages: 2 });
  assert.equal(result.truncated, true);
  assert.equal(fetch.mock.callCount(), 2);
});

test('a later page failure rejects the entire count', async () => {
  let page = 0;
  mock.method(globalThis, 'fetch', async () =>
    ++page === 1 ? Response.json([{ id: 1 }]) : new Response('', { status: 503 }),
  );
  await assert.rejects(
    loadCollection('/drivers', { pageSize: 1 }),
    (error) => error instanceof ApiError && error.status === 503,
  );
});

test('a caller cancellation is distinct from a timeout', async () => {
  mock.method(globalThis, 'fetch', async (_, { signal }) => {
    if (signal.aborted) throw new DOMException('Aborted', 'AbortError');
    return new Promise((resolve, reject) =>
      signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')), {
        once: true,
      }),
    );
  });
  const controller = new AbortController();
  controller.abort();
  await assert.rejects(request('/health', { signal: controller.signal }), { name: 'AbortError' });
  await assert.rejects(
    request('/health', { timeoutMs: 5 }),
    (error) => error instanceof ApiError && error.message.includes('quá lâu'),
  );
});

test('an empty list is a valid zero; malformed lists are rejected', async () => {
  mock.method(globalThis, 'fetch', async () => Response.json([]));
  assert.deepEqual(await loadCollection('/drivers'), { items: [], truncated: false });
  mock.method(globalThis, 'fetch', async () => Response.json({ count: 12 }));
  await assert.rejects(loadCollection('/drivers'), ApiError);
});
