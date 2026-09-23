import { NavLink } from 'react-router-dom'

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? 'text-slate-900 font-medium' : 'hover:text-slate-900'

export function Header() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <span className="text-lg font-semibold tracking-tight">QuoteBind</span>
        <nav className="flex gap-6 text-sm text-slate-600">
          <NavLink to="/products" className={navLinkClass}>
            Products
          </NavLink>
          <NavLink to="/question-set" className={navLinkClass}>
            Question Set
          </NavLink>
          <NavLink to="/quotes" className={navLinkClass}>
            Quotes
          </NavLink>
        </nav>
      </div>
    </header>
  )
}
