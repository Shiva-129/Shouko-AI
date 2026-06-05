import { create } from "zustand";

interface UpgradeModalStore {
  isOpen: boolean;
  title: string;
  description: string;
  open: (title?: string, description?: string) => void;
  close: () => void;
}

export const useUpgradeModal = create<UpgradeModalStore>((set) => ({
  isOpen: false,
  title: "Usage Limit Reached",
  description: "You have hit the monthly usage threshold for your Free account.",
  open: (title, description) =>
    set({
      isOpen: true,
      title: title || "Usage Limit Reached",
      description: description || "You have hit the monthly usage threshold for your Free account.",
    }),
  close: () => set({ isOpen: false }),
}));
