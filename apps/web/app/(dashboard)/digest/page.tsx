"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function DigestRedirect() {
  const router = useRouter();

  useEffect(() => {
    const today = new Date().toISOString().split("T")[0];
    router.replace(`/digest/${today}`);
  }, [router]);

  return null;
}
