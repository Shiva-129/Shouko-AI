"use client";

import { useParams } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";

export default function ArtifactPage() {
  const params = useParams();
  const id = params.id as string;

  return (
    <div className="p-8">
      <h1 className="font-syne font-extrabold text-[32px] text-primaryText tracking-tight mb-6">
        Artifact
      </h1>
      <Card className="bg-card border-border">
        <CardContent className="pt-6">
          <p className="text-secondaryText text-sm">
            Artifact {id} will be rendered here with summary, insights, Q&A, and chat.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
