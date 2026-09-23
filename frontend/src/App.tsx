function App() {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <span className="text-lg font-semibold tracking-tight">QuoteBind</span>
          <nav className="flex gap-6 text-sm text-slate-600">
            <a className="hover:text-slate-900" href="#">
              Products
            </a>
            <a className="hover:text-slate-900" href="#">
              Quotes
            </a>
          </nav>
        </div>
      </header>

      <main className="mx-auto flex max-w-5xl flex-1 flex-col items-center justify-center gap-4 px-6 py-24 text-center">
        <h1 className="text-4xl font-semibold tracking-tight text-slate-900">
          QuoteBind
        </h1>
        <p className="max-w-md text-slate-600">
          Frontend scaffold — React + TypeScript + Tailwind CSS, wired up to talk
          to the QuoteBind API.
        </p>
      </main>

      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-400">
        QuoteBind
      </footer>
    </div>
  )
}

export default App
