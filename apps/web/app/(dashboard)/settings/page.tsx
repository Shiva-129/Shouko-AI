"use client";

import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useUser } from "@/lib/hooks/useUser";
import { Loader2 } from "lucide-react";

export default function SettingsPage() {
  const router = useRouter();
  const { data: user, isLoading: isUserLoading } = useUser();

  if (isUserLoading) {
    return (
      <div className="flex-1 bg-workspace flex flex-col justify-center items-center min-w-0 p-8 h-96 select-none">
        <Loader2 className="h-8 w-8 text-lime animate-spin mb-2" />
        <p className="text-secondaryText text-sm font-mono">Loading settings...</p>
      </div>
    );
  }

  return (
    <div className="flex-1 bg-workspace flex flex-col min-w-0 p-8 select-none">
      <h1 className="font-syne font-extrabold text-[32px] text-primaryText tracking-tight mb-6">
        Settings
      </h1>

      <div className="grid gap-6">
        {/* Profile Card */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-lg text-primaryText">Profile</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-secondaryText text-sm mb-3">
              Logged in as <span className="font-mono text-primaryText">{user?.email}</span>
            </p>
            <Button variant="outline" size="sm" disabled>
              Edit Profile
            </Button>
          </CardContent>
        </Card>

        {/* Interest Profile Card */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-lg text-primaryText">Interest Profile</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-secondaryText text-sm mb-3">
              Set your research interests to personalize your daily digest.
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push("/settings/interests")}
            >
              Manage Interests
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
