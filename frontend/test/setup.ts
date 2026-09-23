import { TextDecoder, TextEncoder } from 'node:util'

import '@testing-library/jest-dom'

// jest-environment-jsdom doesn't expose TextEncoder/TextDecoder as globals
// (a long-standing Jest+jsdom gap); @mui/x-data-grid's internals need them.
if (!('TextEncoder' in global)) {
  global.TextEncoder = TextEncoder as unknown as typeof global.TextEncoder
}
if (!('TextDecoder' in global)) {
  global.TextDecoder = TextDecoder as unknown as typeof global.TextDecoder
}

// MUI's DataGrid measures its container via ResizeObserver, which jsdom
// doesn't implement. A no-op stub is enough for it to render in tests.
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}

if (!('ResizeObserver' in window)) {
  window.ResizeObserver = ResizeObserverStub as unknown as typeof ResizeObserver
}

if (!('matchMedia' in window)) {
  window.matchMedia = (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  })
}
