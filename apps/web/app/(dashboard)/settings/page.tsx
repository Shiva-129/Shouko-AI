"use client";

import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useUser } from "@/lib/hooks/useUser";
import { apiClient } from "@/lib/api";
import { CreditCard, Zap, CheckCircle, Sparkles, Loader2 } from "lucide-react";
import { useState } from "react";
import { Progress } from "@/components/ui/progress";

export default function SettingsPage() {
  const router = useRouter();
  const { data: user, isLoading: isUserLoading, refetch } = useUser();
  const [isBillingLoading, setIsBillingLoading] = useState(false);
  const [billingError, setBillingError] = useState<string | null>(null);

  const handleBillingAction = async () => {
    if (!user) return;
    setIsBillingLoading(true);
    setBillingError(null);
    try {
      if (user.plan === "pro") {
        // Redirect to Stripe Portal
        const res = await apiClient.post<{ url: string }>("/billing/portal");
        if (res.url) {
          window.location.href = res.url;
        } else {
          throw new Error("No portal URL returned.");
        }
      } else {
        // Redirect to Stripe Checkout
        const res = await apiClient.post<{ url: string }>("/billing/checkout");
        if (res.url) {
          window.location.href = res.url;
        } else {
          throw new Error("No checkout URL returned.");
        }
      }
    } catch (err: any) {
      console.error("Billing action failed:", err);
      setBillingError(err.message || "Something went wrong. Please try again.");
    } finally {
      setIsBillingLoading(false);
    }
  };

  if (isUserLoading) {
    return (
      <div className="p-8 max-w-5xl flex flex-col justify-center items-center h-96">
        <Loader2 className="h-8 w-8 text-lime animate-spin mb-2" />
        <p className="text-secondaryText text-sm font-mono">Loading settings...</p>
      </div>
    );
  }

  const usage = user?.usage;
  const isPro = user?.plan === "pro";

  return (
    <div className="p-8 max-w-5xl">
      <h1 className="font-syne font-extrabold text-[32px] text-primaryText tracking-tight mb-6">
        Settings
      </h1>

      <div className="grid gap-6">
        {/* Billing & Subscription */}
        <Card className="bg-card border-border overflow-hidden relative">
          <div className="absolute top-0 right-0 w-64 h-64 bg-lime/5 rounded-full blur-3xl pointer-events-none" />
          <CardHeader className="pb-4">
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-lg text-primaryText font-syne font-bold flex items-center gap-2">
                  <CreditCard className="h-5 w-5 text-lime" />
                  Subscription Plan
                </CardTitle>
                <CardDescription className="text-xs text-secondaryText font-mono mt-1">
                  Manage your subscription and usage limits.
                </CardDescription>
              </div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-mono uppercase tracking-wider font-semibold ${
                isPro 
                  ? "bg-lime/20 text-lime border border-lime/30" 
                  : "bg-slate-800 text-secondaryText border border-border"
              }`}>
                {user?.plan || "free"} Plan
              </span>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Upgrade CTA or active subscription info */}
            <div className="p-4 rounded-xl border border-border bg-slate-800/40 backdrop-blur-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                {isPro ? (
                  <>
                    <h3 className="font-bold text-sm text-primaryText flex items-center gap-1.5">
                      <Sparkles className="h-4 w-4 text-lime animate-pulse" />
                      PaperBrain Pro Active
                    </h3>
                    <p className="text-xs text-secondaryText mt-1">
                      You have unlimited access to AI summaries, ingestion, and chat.
                    </p>
                  </>
                ) : (
                  <>
                    <h3 className="font-bold text-sm text-primaryText flex items-center gap-1.5">
                      <Zap className="h-4 w-4 text-amber-500 animate-pulse" />
                      Upgrade to Pro
                    </h3>
                    <p className="text-xs text-secondaryText mt-1">
                      Unlock unlimited ingestion, automated paper artifacts, and unlimited RAG chat.
                    </p>
                  </>
                )}
              </div>
              <div>
                <Button 
                  onClick={handleBillingAction} 
                  disabled={isBillingLoading}
                  className={`w-full sm:w-auto font-bold text-xs ${
                    isPro 
                      ? "bg-slate-700 hover:bg-slate-600 text-primaryText" 
                      : "bg-lime text-[#0D0D0D] hover:bg-lime/90"
                  }`}
                >
                  {isBillingLoading && <Loader2 className="h-3 w-3 mr-2 animate-spin" />}
                  {isPro ? "Manage Subscription" : "Upgrade to Pro for $15/mo"}
                </Button>
              </div>
            </div>

            {billingError && (
              <p className="text-xs text-red-400 font-mono mt-2">{billingError}</p>
            )}

            {/* Usage Enforcements */}
            <div className="space-y-4">
              <h4 className="text-xs font-mono uppercase tracking-wider text-secondaryText font-semibold">
                Usage Statistics
              </h4>
              
              <div className="grid md:grid-cols-3 gap-4">
                {/* Artifact generation limit */}
                <Card className="bg-slate-900/50 border-border p-4">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-mono text-secondaryText">Artifacts (Monthly)</span>
                    <span className="text-xs font-mono font-bold text-primaryText">
                      {usage?.artifact_created_monthly || 0} / {isPro ? "∞" : (usage?.artifact_created_limit || 5)}
                    </span>
                  </div>
                  <Progress 
                    value={isPro ? 100 : Math.min(100, ((usage?.artifact_created_monthly || 0) / (usage?.artifact_created_limit || 5)) * 100)} 
                    className="h-1.5 bg-slate-800"
                  />
                </Card>

                {/* Paper Ingestion Limit */}
                <Card className="bg-slate-900/50 border-border p-4">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-mono text-secondaryText">Ingestions (Monthly)</span>
                    <span className="text-xs font-mono font-bold text-primaryText">
                      {usage?.paper_ingested_monthly || 0} / {isPro ? "∞" : (usage?.paper_ingested_limit || 10)}
                    </span>
                  </div>
                  <Progress 
                    value={isPro ? 100 : Math.min(100, ((usage?.paper_ingested_monthly || 0) / (usage?.paper_ingested_limit || 10)) * 100)} 
                    className="h-1.5 bg-slate-800"
                  />
                </Card>

                {/* Chat Questions Limit */}
                <Card className="bg-slate-900/50 border-border p-4">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-mono text-secondaryText">AI Chat Questions (Daily)</span>
                    <span className="text-xs font-mono font-bold text-primaryText">
                      {usage?.question_asked_daily || 0} / {isPro ? "∞" : (usage?.question_asked_limit || 20)}
                    </span>
                  </div>
                  <Progress 
                    value={isPro ? 100 : Math.min(100, ((usage?.question_asked_daily || 0) / (usage?.question_asked_limit || 20)) * 100)} 
                    className="h-1.5 bg-slate-800"
                  />
                </Card>
              </div>
            </div>
          </CardContent>
        </Card>

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
