"use client";

import Link from "next/link";
import { Sparkles, Brain, ArrowRight, BookOpen, MessageSquare, Library } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white relative overflow-hidden flex flex-col justify-between">
      {/* Background gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[600px] bg-gradient-to-b from-lime/10 via-transparent to-transparent blur-3xl pointer-events-none" />
      <div className="absolute top-1/4 right-10 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 left-10 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <header className="max-w-7xl mx-auto w-full px-6 py-6 flex items-center justify-between z-10">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-lime/20 flex items-center justify-center border border-lime/30">
            <Brain className="h-4.5 w-4.5 text-lime" />
          </div>
          <span className="font-syne font-extrabold text-lg tracking-tight">
            Shouko <span className="text-lime">AI</span>
          </span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/login">
            <Button variant="ghost" className="text-xs font-mono hover:text-white hover:bg-slate-900">
              Sign In
            </Button>
          </Link>
          <Link href="/signup">
            <Button size="sm" className="bg-lime text-slate-950 hover:bg-lime/90 font-bold text-xs">
              Get Started
            </Button>
          </Link>
        </div>
      </header>

      {/* Hero section */}
      <main className="max-w-4xl mx-auto px-6 py-20 text-center flex-1 flex flex-col items-center justify-center z-10">
        <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-lime/20 bg-lime/5 text-lime text-[10px] font-mono uppercase tracking-wider mb-6 animate-pulse">
          <Sparkles className="h-3 w-3" />
          Next-Gen Academic Intelligence
        </div>

        <h1 className="font-syne font-extrabold text-4xl md:text-6xl tracking-tight leading-tight max-w-3xl mb-6 bg-gradient-to-b from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
          Transform Academic Literature Into Living Knowledge
        </h1>

        <p className="text-sm md:text-base text-slate-400 font-mono max-w-xl mb-10 leading-relaxed">
          Shouko-AI automatically discovers recent papers, ingests and chunks PDFs, extracts structured insights, and lets you chat with your entire library via context-aware RAG agents.
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-4 mb-20">
          <Link href="/signup">
            <Button size="lg" className="bg-lime text-slate-950 hover:bg-lime/90 font-bold text-sm px-8 py-6 rounded-xl shadow-lg shadow-lime/10">
              Start Researching Free
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </Link>
          <Link href="/login">
            <Button size="lg" variant="outline" className="border-slate-800 bg-slate-900/50 text-white hover:bg-slate-900 hover:text-white font-mono text-xs px-8 py-6 rounded-xl">
              Access Workspace
            </Button>
          </Link>
        </div>

        {/* Feature Highlights Grid */}
        <div className="grid md:grid-cols-3 gap-6 w-full text-left">
          <div className="bg-slate-900/40 border border-slate-800/80 p-6 rounded-2xl backdrop-blur-sm">
            <div className="h-8 w-8 rounded-lg bg-lime/10 flex items-center justify-center mb-4">
              <BookOpen className="h-4 w-4 text-lime" />
            </div>
            <h3 className="font-syne font-bold text-sm text-white mb-2">Daily Discovery Digests</h3>
            <p className="text-xs text-slate-400 font-mono leading-relaxed">
              Curated daily academic recommendations customized against your scientific interest profile.
            </p>
          </div>

          <div className="bg-slate-900/40 border border-slate-800/80 p-6 rounded-2xl backdrop-blur-sm">
            <div className="h-8 w-8 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4">
              <Library className="h-4 w-4 text-blue-400" />
            </div>
            <h3 className="font-syne font-bold text-sm text-white mb-2">Interactive Wikified Artifacts</h3>
            <p className="text-xs text-slate-400 font-mono leading-relaxed">
              PDF text is mapped to structured dashboards of key insights, QA pairs, and suggested experiments.
            </p>
          </div>

          <div className="bg-slate-900/40 border border-slate-800/80 p-6 rounded-2xl backdrop-blur-sm">
            <div className="h-8 w-8 rounded-lg bg-purple-500/10 flex items-center justify-center mb-4">
              <MessageSquare className="h-4 w-4 text-purple-400" />
            </div>
            <h3 className="font-syne font-bold text-sm text-white mb-2">Context-Aware RAG Chat</h3>
            <p className="text-xs text-slate-400 font-mono leading-relaxed">
              Query specific publications with citation-aware responses backed by pgvector similarity search.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900/80 py-8 text-center text-[10px] font-mono text-slate-600 z-10">
        © 2026 Shouko-AI. Crafted for advanced academic exploration.
      </footer>
    </div>
  );
}
