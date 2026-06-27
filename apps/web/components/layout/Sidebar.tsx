"use client";

import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import {
  LayoutGrid,
  Sparkles,
  BookOpen,
  FolderClosed,
  Settings,
  Menu,
} from "lucide-react";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";

const navItems = [
  { id: "dashboard", label: "Dashboard", icon: LayoutGrid, href: "/dashboard" },
  { id: "digest", label: "Today's Digest", icon: Sparkles, href: "/digest" },
  { id: "library", label: "My Library", icon: BookOpen, href: "/library" },
  { id: "collections", label: "Collections", icon: FolderClosed, href: "/collections" },
];

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  const router = useRouter();

  const handleNavigation = (href: string) => {
    router.push(href);
    onNavigate?.();
  };

  return (
    <div className="flex flex-col justify-between h-full bg-[#0D0D0D] p-5 min-h-screen">
      <div className="flex flex-col gap-6">
        <button
          onClick={() => handleNavigation("/dashboard")}
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
                onClick={() => handleNavigation(item.href)}
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
          onClick={() => handleNavigation("/settings")}
          className="w-full py-2 px-3 rounded-[6px] text-secondaryText hover:text-white transition-all flex items-center gap-3 text-xs text-left"
        >
          <Settings className="h-4 w-4 shrink-0 text-secondaryText" />
          <span>Settings</span>
        </button>

      </div>
    </div>
  );
}

export function Sidebar() {
  return (
    <aside className="hidden md:flex w-[240px] shrink-0 bg-[#0D0D0D] border-r border-[#1E1E1E] min-h-screen">
      <div className="w-full h-full">
        <SidebarContent />
      </div>
    </aside>
  );
}

export function MobileHeader() {
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();

  return (
    <header className="md:hidden h-14 border-b border-[#1E1E1E] bg-[#0D0D0D] flex items-center justify-between px-4 w-full shrink-0 z-40">
      <button
        onClick={() => router.push("/dashboard")}
        className="font-syne font-extrabold text-[18px] tracking-tight text-white"
      >
        RESEARCH RUN<span className="text-lime">.</span>
      </button>

      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetTrigger asChild>
          <button className="h-8 w-8 flex items-center justify-center text-primaryText hover:text-lime outline-none">
            <Menu className="h-5 w-5 text-white" />
          </button>
        </SheetTrigger>
        <SheetContent side="left" className="p-0 w-[240px] bg-[#0D0D0D] border-r border-[#1E1E1E]">
          <SidebarContent onNavigate={() => setIsOpen(false)} />
        </SheetContent>
      </Sheet>
    </header>
  );
}
