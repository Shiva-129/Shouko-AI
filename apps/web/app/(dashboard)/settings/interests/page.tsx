"use client";

import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useUser } from "@/lib/hooks/useUser";
import { apiClient } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const ARXIV_CATEGORIES = [
  "cs.AI", "cs.CL", "cs.CV", "cs.LG", "cs.IR",
  "cs.NE", "cs.RO", "cs.MA", "cs.SI", "cs.SE",
  "stat.ML", "math.OC", "q-bio.QM", "q-fin.ST",
];

export default function InterestsPage() {
  const { data: user, isLoading } = useUser();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [topics, setTopics] = useState<string[]>(
    (user?.interest_profile?.topics as string[]) || []
  );
  const [keywords, setKeywords] = useState<string[]>(
    (user?.interest_profile?.keywords as string[]) || []
  );
  const [authors, setAuthors] = useState<string[]>(
    (user?.interest_profile?.authors as string[]) || []
  );
  const [selectedCategories, setSelectedCategories] = useState<string[]>(
    (user?.interest_profile?.categories as string[]) || []
  );
  const [topicInput, setTopicInput] = useState("");
  const [keywordInput, setKeywordInput] = useState("");
  const [authorInput, setAuthorInput] = useState("");
  const [saving, setSaving] = useState(false);

  const addItem = (
    list: string[],
    setter: (v: string[]) => void,
    value: string
  ) => {
    const trimmed = value.trim();
    if (trimmed && !list.includes(trimmed)) {
      setter([...list, trimmed]);
    }
  };

  const removeItem = (
    list: string[],
    setter: (v: string[]) => void,
    item: string
  ) => {
    setter(list.filter((i) => i !== item));
  };

  const toggleCategory = (cat: string) => {
    if (selectedCategories.includes(cat)) {
      setSelectedCategories(selectedCategories.filter((c) => c !== cat));
    } else {
      setSelectedCategories([...selectedCategories, cat]);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await apiClient.patch("/users/me", {
        interest_profile: {
          topics,
          keywords,
          authors,
          categories: selectedCategories,
        },
      });
      queryClient.invalidateQueries({ queryKey: ["user"] });
      toast({
        title: "Interests saved",
        description: "Your daily digest will be personalized based on these interests.",
      });
    } catch {
      toast({
        title: "Failed to save",
        description: "Check your connection and try again.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="p-8 space-y-4">
        <Skeleton className="h-8 w-48 bg-card" />
        <Skeleton className="h-48 bg-card" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-2xl">
      <h1 className="font-syne font-extrabold text-[32px] text-primaryText tracking-tight mb-1">
        Interest Profile
      </h1>
      <p className="text-sm text-secondaryText mb-6">
        Set your research interests to personalize your daily digest and
        recommendations.
      </p>

      <div className="grid gap-6">
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-sm text-primaryText font-semibold">
              Topics
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex gap-2">
              <Input
                placeholder="e.g. Transformers, Reinforcement Learning"
                value={topicInput}
                onChange={(e) => setTopicInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    addItem(topics, setTopics, topicInput);
                    setTopicInput("");
                  }
                }}
                className="bg-canvas border-border text-sm"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  addItem(topics, setTopics, topicInput);
                  setTopicInput("");
                }}
              >
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {topics.map((t) => (
                <Badge
                  key={t}
                  variant="secondary"
                  className="cursor-pointer hover:bg-red-500/20 hover:text-red-400 transition-colors"
                  onClick={() => removeItem(topics, setTopics, t)}
                >
                  {t} &times;
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-sm text-primaryText font-semibold">
              Keywords
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex gap-2">
              <Input
                placeholder="e.g. Attention, Rotary, KV Cache"
                value={keywordInput}
                onChange={(e) => setKeywordInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    addItem(keywords, setKeywords, keywordInput);
                    setKeywordInput("");
                  }
                }}
                className="bg-canvas border-border text-sm"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  addItem(keywords, setKeywords, keywordInput);
                  setKeywordInput("");
                }}
              >
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {keywords.map((k) => (
                <Badge
                  key={k}
                  variant="secondary"
                  className="cursor-pointer hover:bg-red-500/20 hover:text-red-400 transition-colors"
                  onClick={() => removeItem(keywords, setKeywords, k)}
                >
                  {k} &times;
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-sm text-primaryText font-semibold">
              Favorite Authors
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex gap-2">
              <Input
                placeholder="e.g. Ashish Vaswani, Yann LeCun"
                value={authorInput}
                onChange={(e) => setAuthorInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    addItem(authors, setAuthors, authorInput);
                    setAuthorInput("");
                  }
                }}
                className="bg-canvas border-border text-sm"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  addItem(authors, setAuthors, authorInput);
                  setAuthorInput("");
                }}
              >
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {authors.map((a) => (
                <Badge
                  key={a}
                  variant="secondary"
                  className="cursor-pointer hover:bg-red-500/20 hover:text-red-400 transition-colors"
                  onClick={() => removeItem(authors, setAuthors, a)}
                >
                  {a} &times;
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="text-sm text-primaryText font-semibold">
              ArXiv Categories
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-secondaryText mb-3">
              Select categories that match your research areas.
            </p>
            <div className="flex flex-wrap gap-2">
              {ARXIV_CATEGORIES.map((cat) => {
                const active = selectedCategories.includes(cat);
                return (
                  <Badge
                    key={cat}
                    variant={active ? "default" : "outline"}
                    className={`cursor-pointer transition-colors ${
                      active
                        ? "bg-lime/20 text-lime border-lime/30 hover:bg-lime/30"
                        : "border-border text-secondaryText hover:text-primaryText hover:border-lime/30"
                    }`}
                    onClick={() => toggleCategory(cat)}
                  >
                    {cat}
                  </Badge>
                );
              })}
            </div>
          </CardContent>
        </Card>

        <Button
          onClick={handleSave}
          disabled={saving}
          className="bg-lime text-black hover:bg-lime/90 font-semibold"
        >
          {saving ? "Saving..." : "Save Interests"}
        </Button>
      </div>
    </div>
  );
}
