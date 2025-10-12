export default function Header({ children }) {
  return (
    <header className="w-full max-w-3xl p-8 flex flex-col items-center gap-6 mx-auto">
      <h1 className="text-2xl font-semibold text-white">Boston Hacks</h1>
      {children}
    </header>
  )
}
