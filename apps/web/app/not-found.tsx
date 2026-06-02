import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-canvas gap-4">
      <h1 className="font-syne font-extrabold text-6xl text-primaryText">404</h1>
      <p className="text-secondaryText text-lg">Page not found</p>
      <Link
        href="/dashboard"
        className="text-lime hover:underline text-sm font-mono"
      >
        Return to dashboard
      </Link>
    </div>
  );
}
