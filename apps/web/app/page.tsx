"use client";

import Link from "next/link";
import { Sparkles, Brain, ArrowRight, BookOpen, MessageSquare, Library, Check, Zap, Cpu, Database } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-canvas text-primaryText relative overflow-hidden flex flex-col font-sans">
      {/* Background gradients aligned with design system */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-[600px] bg-gradient-to-b from-lime/10 via-transparent to-transparent blur-3xl pointer-events-none" />
      <div className="absolute top-1/4 right-10 w-96 h-96 bg-violet/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 left-10 w-96 h-96 bg-blue/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <header className="max-w-7xl mx-auto w-full px-6 py-6 flex items-center justify-between z-10">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-lime/10 flex items-center justify-center border border-lime/20">
            <Brain className="h-4.5 w-4.5 text-lime" />
          </div>
          <span className="font-syne font-extrabold text-xl tracking-tight">
            PaperBrain <span className="text-lime">AI</span>
          </span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/login">
            <Button variant="ghost" className="text-xs font-mono text-secondaryText hover:text-primaryText hover:bg-workspace">
              Sign In
            </Button>
          </Link>
          <Link href="/signup">
            <Button size="sm" className="bg-lime text-workspace hover:bg-lime/90 font-bold text-xs shadow-[0_0_15px_rgba(200,240,74,0.3)] transition-all">
              Get Started
            </Button>
          </Link>
        </div>
      </header>

      {/* Hero section */}
      <section className="max-w-5xl mx-auto px-6 py-24 text-center flex flex-col items-center z-10">
        <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-lime/20 bg-lime/5 text-lime text-[10px] font-mono uppercase tracking-wider mb-8 animate-pulse shadow-[0_0_10px_rgba(200,240,74,0.1)]">
          <Sparkles className="h-3 w-3" />
          Multi-Agent Academic Intelligence
        </div>

        <h1 className="font-syne font-extrabold text-5xl md:text-7xl tracking-tight leading-[1.1] max-w-4xl mb-8 text-primaryText">
          Turn Static Papers Into <br className="hidden md:block"/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-lime to-violet">Interactive Knowledge</span>
        </h1>

        <p className="text-sm md:text-lg text-secondaryText font-sans max-w-2xl mb-12 leading-relaxed">
          Ingest dense PDFs, extract structured insights via Kimi K2.6, and chat with your entire library using pgvector-powered RAG. Your personalized AI research assistant.
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-5">
          <Link href="/signup">
            <Button size="lg" className="bg-lime text-workspace hover:bg-lime/90 font-bold text-sm px-8 py-6 rounded-xl shadow-[0_0_20px_rgba(200,240,74,0.2)] hover:shadow-[0_0_30px_rgba(200,240,74,0.4)] transition-all">
              Start Researching Free
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </Link>
          <Link href="/login">
            <Button size="lg" variant="outline" className="border-border bg-workspace text-primaryText hover:bg-card hover:text-primaryText font-mono text-xs px-8 py-6 rounded-xl transition-all">
              Access Workspace
            </Button>
          </Link>
        </div>
      </section>

      {/* Features Grid */}
      <section className="max-w-7xl mx-auto px-6 py-20 w-full z-10">
        <div className="text-center mb-16">
          <h2 className="font-syne font-bold text-3xl md:text-4xl text-primaryText mb-4">Powered by Advanced AI Agents</h2>
          <p className="text-secondaryText font-mono text-xs uppercase tracking-widest">Built on OpenRouter & Groq Infrastructure</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 w-full">
          <div className="bg-workspace border border-border p-8 rounded-2xl hover:border-lime/30 transition-colors group">
            <div className="h-12 w-12 rounded-xl bg-card flex items-center justify-center mb-6 group-hover:scale-110 transition-transform border border-border">
              <Database className="h-5 w-5 text-lime" />
            </div>
            <h3 className="font-syne font-bold text-xl text-primaryText mb-3">Vector-Powered RAG</h3>
            <p className="text-sm text-secondaryText font-sans leading-relaxed">
              Every ingested paper is chunked and embedded using Nemotron-Embed 2048d into our pgvector database for highly accurate semantic retrieval.
            </p>
          </div>

          <div className="bg-workspace border border-border p-8 rounded-2xl hover:border-violet/30 transition-colors group">
            <div className="h-12 w-12 rounded-xl bg-card flex items-center justify-center mb-6 group-hover:scale-110 transition-transform border border-border">
              <Cpu className="h-5 w-5 text-violet" />
            </div>
            <h3 className="font-syne font-bold text-xl text-primaryText mb-3">Structured Artifacts</h3>
            <p className="text-sm text-secondaryText font-sans leading-relaxed">
              Our ArtifactAgent distills complex PDFs into executive summaries, key insights with importance scores, auto-generated Q&A, and suggested experiments.
            </p>
          </div>

          <div className="bg-workspace border border-border p-8 rounded-2xl hover:border-blue/30 transition-colors group">
            <div className="h-12 w-12 rounded-xl bg-card flex items-center justify-center mb-6 group-hover:scale-110 transition-transform border border-border">
              <Zap className="h-5 w-5 text-blue" />
            </div>
            <h3 className="font-syne font-bold text-xl text-primaryText mb-3">Daily Discovery Digests</h3>
            <p className="text-sm text-secondaryText font-sans leading-relaxed">
              Automated Celery tasks scan ArXiv daily, score papers against your interests using Groq&apos;s Llama-3, and deliver personalized email digests via Resend.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="max-w-5xl mx-auto px-6 py-24 w-full z-10 border-t border-border mt-10">
        <div className="text-center mb-16">
          <h2 className="font-syne font-bold text-3xl md:text-5xl text-primaryText mb-4">Simple, Transparent Pricing</h2>
          <p className="text-secondaryText font-sans max-w-xl mx-auto">Start exploring for free, upgrade when your research demands it.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Free Tier */}
          <div className="bg-workspace border border-border p-10 rounded-3xl flex flex-col">
            <h3 className="font-syne font-bold text-2xl text-primaryText mb-2">Researcher Basic</h3>
            <div className="flex items-baseline gap-2 mb-6">
              <span className="text-4xl font-extrabold text-primaryText">$0</span>
              <span className="text-secondaryText font-mono text-sm">/ forever</span>
            </div>
            <p className="text-sm text-secondaryText mb-8 flex-1">Perfect for students and casual researchers exploring the platform.</p>

            <ul className="space-y-4 mb-8 font-sans text-sm text-primaryText">
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-lime shrink-0" />
                <span>Up to 10 Paper Ingestions / month</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-lime shrink-0" />
                <span>Basic Artifact Generation</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-lime shrink-0" />
                <span>Standard RAG Chat (50 messages/mo)</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-lime shrink-0" />
                <span>Weekly Discovery Digest</span>
              </li>
            </ul>

            <Link href="/signup" className="w-full mt-auto">
              <Button variant="outline" className="w-full border-border bg-card text-primaryText hover:bg-border font-bold">
                Get Started Free
              </Button>
            </Link>
          </div>

          {/* Pro Tier */}
          <div className="bg-card border-2 border-lime/50 p-10 rounded-3xl relative flex flex-col shadow-[0_0_40px_rgba(200,240,74,0.05)]">
            <div className="absolute top-0 right-10 -translate-y-1/2 bg-lime text-workspace px-3 py-1 rounded-full text-xs font-bold font-mono uppercase tracking-wider">
              Most Popular
            </div>
            <h3 className="font-syne font-bold text-2xl text-primaryText mb-2">PaperBrain Pro</h3>
            <div className="flex items-baseline gap-2 mb-6">
              <span className="text-4xl font-extrabold text-primaryText">$15</span>
              <span className="text-secondaryText font-mono text-sm">/ month</span>
            </div>
            <p className="text-sm text-secondaryText mb-8 flex-1">Uncapped intelligence for serious academics and R&D professionals.</p>

            <ul className="space-y-4 mb-8 font-sans text-sm text-primaryText">
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-lime shrink-0" />
                <span><strong>Unlimited</strong> Paper Ingestions</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-lime shrink-0" />
                <span>Deep Artifact Generation (Kimi K2.6)</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-lime shrink-0" />
                <span><strong>Unlimited</strong> Context-Aware RAG Chat</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="h-5 w-5 text-lime shrink-0" />
                <span><strong>Daily</strong> Personalized Discovery Digests</span>
              </li>
            </ul>

            <Link href="/signup" className="w-full mt-auto">
              <Button className="w-full bg-lime text-workspace hover:bg-lime/90 font-bold shadow-[0_0_15px_rgba(200,240,74,0.2)]">
                Upgrade to Pro
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border mt-auto py-10 z-10 bg-workspace">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2 opacity-50">
            <Brain className="h-4 w-4 text-primaryText" />
            <span className="font-syne font-bold text-sm tracking-tight text-primaryText">
              PaperBrain AI
            </span>
          </div>
          <p className="text-[11px] font-mono text-tertiaryText">
            © 2026 PaperBrain. Empowering academic exploration with multi-agent infrastructure.
          </p>
        </div>
      </footer>
    </div>
  );
}
