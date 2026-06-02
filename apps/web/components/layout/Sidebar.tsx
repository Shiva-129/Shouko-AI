"use client";

import { usePathname, useRouter } from "next/navigation";
import {
  LayoutGrid,
  Sparkles,
  BookOpen,
  FolderClosed,
  Settings,
  LogOut,
} from "lucide-react";
import { createClient } from "@/lib/supabase";

const navItems = [
  { id: "dashboard", label: "Dashboard", icon: LayoutGrid, href: "/dashboard" },
  { id: "digest", label: "Today's Digest", icon: Sparkles, href: "/digest" },
  { id: "library", label: "My Library", icon: BookOpen, href: "/library" },
  { id: "collections", label: "Collections", icon: FolderClosed, href: "/collections" },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  const handleSignOut = async () => {
    const supabase = createClient();
    if (supabase) {
      await supabase.auth.signOut();
    }
    router.push("/login");
  };

  return (
    <aside className="w-[240px] shrink-0 bg-[#0D0D0D] flex flex-col justify-between p-5 border-r border-[#1E1E1E] min-h-screen">
      <div className="flex flex-col gap-6">
        <button
          onClick={() => router.push("/dashboard")}
          className="font-syne font-extrabold text-[22px] tracking-tight text-white text-left leading-none pt-2 flex items-center"
        >
          RESEARCH RUN<span className="text-lime">.</span>
        </button>

        <div className="flex flex-col gap-1.5 pt-2">
          {navItems.map((item) => {
            const isActive = pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => router.push(item.href)}
                className={`w-full py-2 px-3 rounded-[6px] font-sans text-xs text-left flex items-center gap-3 transition-colors ${
                  isActive
                    ? "text-lime bg-[#1E1E1E]/40 font-semibold"
                    : "text-secondaryText hover:text-primaryText hover:bg-[#1E1E1E]/20"
                }`}
              >
                <Icon className={`h-4 w-4 shrink-0 ${isActive ? "text-lime" : "text-secondaryText"}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex flex-col gap-4">
        <button
          onClick={() => router.push("/settings")}
          className="w-full py-2 px-3 rounded-[6px] text-secondaryText hover:text-white transition-all flex items-center gap-3 text-xs text-left"
        >
          <Settings className="h-4 w-4 shrink-0 text-secondaryText" />
          <span>Settings</span>
        </button>
        <button
          onClick={handleSignOut}
          className="w-full py-2 px-3 rounded-[6px] text-secondaryText hover:text-red-400 transition-all flex items-center gap-3 text-xs text-left"
        >
          <LogOut className="h-4 w-4 shrink-0" />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  );
}
