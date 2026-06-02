"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function CollectionsPage() {
  return (
    <div className="p-8">
      <h1 className="font-syne font-extrabold text-[32px] text-primaryText tracking-tight mb-6">
        Collections
      </h1>
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-lg text-primaryText">Your Collections</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-secondaryText text-sm">
            Organize your artifacts into themed collections.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
