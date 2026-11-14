import Link from "next/link";

export function AppHeader() {
  return (
    <header className="border-b border-border/40 px-6 py-4">
      <Link href="/home" className="text-lg font-semibold tracking-tight">Tu App</Link>
    </header>
  );
}
