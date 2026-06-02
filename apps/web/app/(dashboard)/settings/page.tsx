"use client";

import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function SettingsPage() {
  const router = useRouter();

  return (
    <div className="p-8">
      <h1 className="font-syne font-extrabold text-[32px] text-primaryText tracking-tight mb-6">
        Settings
      </h1>
      <div className="grid gap-4">
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-lg text-primaryText">Profile</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-secondaryText text-sm mb-3">
              Manage your name, email, and avatar.
            </p>
            <Button variant="outline" size="sm" disabled>
              Edit Profile
            </Button>
          </CardContent>
        </Card>
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
