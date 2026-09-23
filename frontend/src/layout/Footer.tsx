export function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="border-t border-slate-800 bg-slate-950 py-10 text-center">
      <p className="font-mono text-sm text-[#8b93c9]">
        © {year} Swati Pote. All rights reserved.
      </p>
    </footer>
  )
}
