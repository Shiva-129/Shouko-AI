"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  LayoutGrid,
  Sparkles,
  BookOpen,
  FolderClosed,
  Settings,
  Building2,
  Clock,
  Paperclip,
  ArrowUp,
  FileText,
  MessageSquare,
  Loader2,
  Send,
  Network
} from "lucide-react";

// Paper Interface
interface Paper {
  id: string;
  title: string;
  subTagline: string;
  institution: string;
  difficulty: "EASY" | "MEDIUM" | "HARD";
  readingTime: string;
  relevance: string;
  isHot: boolean;
  category: "Agents" | "Multi-Agent" | "Safety" | "Reasoning";
  tags: string[];
  summary: string;
  body: string;
  citations: string[];
  notes: string[];
  initialAssistantMessage: string;
  mockQueries: string[];
  mockQAs: { question: string; answer: string }[];
  borderAccent?: string; // Optional border accent color
}

// Chat Message Interface
interface Message {
  role: "user" | "assistant";
  content: string;
}

// Draggable Mindmap Node Interface
interface NodePosition {
  id: string;
  label: string;
  desc: string;
  type: "root" | "branch" | "child";
  parentId?: string;
  x: number;
  y: number;
}

export default function PaperBrainDashboard() {
  // Navigation & Workspace states
  const [activeNav, setActiveNav] = useState<string>("digest");
  const [activeFilter, setActiveFilter] = useState<string>("All");
  const [selectedPaperId, setSelectedPaperId] = useState<string>("emergent-autonomous");
  const [activeRightTab, setActiveRightTab] = useState<"analysis" | "sources" | "chat">("analysis");
  const [inputMessage, setInputMessage] = useState<string>("");
  const [expandedMindmapPaperId, setExpandedMindmapPaperId] = useState<string | null>(null);
  const [activeMindmapNode, setActiveMindmapNode] = useState<string | null>(null);

  // Paper Catalog matching the screenshot
  const papers: Paper[] = [
    {
      id: "emergent-autonomous",
      title: "Emergent Autonomous Scientific Research Capabilities of Large Language Models",
      subTagline: "THE FRONTIER OF AUTONOMOUS DISCOVERY SYSTEMS",
      institution: "MIT",
      difficulty: "MEDIUM",
      readingTime: "12 min",
      relevance: "HOT",
      isHot: true,
      category: "Agents",
      tags: ["arXiv", "LLMs"],
      summary: "We explore the capability of large language models to autonomously design, plan, and execute scientific protocols.",
      body: "This work investigates the capability of modern large language models to autonomously plan, formulate hypotheses, and execute complex scientific research workflows. By placing agents inside virtualized sandboxes integrated with compilation environments, standard web search engines, and Python libraries, we observe the emergence of sophisticated troubleshooting and experiment design. While highly promising for accelerated research, our analysis underscores the critical need for robust safety sandboxing and alignment validation to prevent toxic compound synthesis or runaway network executions.",
      citations: [
        "Bran et al. (2023) — ChemCrow: Augmenting LLMs with Chemistry Tools",
        "Zelikman et al. (2022) — STaR: Bootstrapping Reasoning With Reasoning",
        "Amodei et al. (2016) — Concrete Problems in AI Safety"
      ],
      notes: [
        "LLM agents design, execute, and troubleshoot scientific code inside execution buffers.",
        "Demonstrates advanced reasoning and self-correction but poses safety risks under malicious goals.",
        "Proposes standard containment guidelines for multi-agent sandbox testing."
      ],
      initialAssistantMessage: "LLM Science Agent online. I am prepared to break down laboratory sandboxing protocols, emergent capabilities, or alignment metrics.",
      mockQueries: ["How were the agents containerized?", "What are the core safety risks?"],
      mockQAs: [
        {
          question: "how were the agents containerized?",
          answer: "Agents are confined to isolated Docker containers lacking raw socket access. Filesystem interactions are limited to temporary directories, and tool actions are monitored by a separate supervisor LLM that enforces strict policy restrictions."
        },
        {
          question: "what are the core safety risks?",
          answer: "The primary safety risks include accidental synthesis of toxic compounds, automated execution of malicious shell actions, and runaway API billing cycles if agents enter recursive tool-invocation feedback loops."
        }
      ]
    },
    {
      id: "self-reflective",
      title: "Self-Reflective Prompting: A Framework for Robust Multi-Agent Negotiation",
      subTagline: "ITERATIVE REFLECTION IN BAYESIAN MULTI-AGENT SYSTEMS",
      institution: "Stanford",
      difficulty: "HARD",
      readingTime: "8 min",
      relevance: "98% Match",
      isHot: false,
      category: "Multi-Agent",
      tags: ["NeurIPS", "Negotiation"],
      summary: "This paper introduces a novel architecture where agents iteratively evaluate their own generated proposals to find equilibria.",
      body: "Self-Reflective Prompting establishes a robust game-theoretic framework for multi-agent negotiations. Instead of using raw, uncorrected output sequences, each agent maintains a stateful reflection trace. During negotiation rounds, the agent critiques its own intermediate proposals against modeled opponent beliefs, minimizing Nash regret and converging to Pareto-optimal solutions in fewer communication turns.",
      citations: [
        "Rafailov et al. (2023) — Direct Preference Optimization",
        "Shoham et al. (2008) — Multiagent Systems: Algorithmic Foundations",
        "Shinn et al. (2023) — Reflexion: Language Agents with Verbal Feedback Loops"
      ],
      notes: [
        "Establishes a stateful reflection trace that models opposing player payoffs.",
        "Significantly decreases the number of communication rounds required to hit Nash equilibrium.",
        "Validated across classic economic benchmarks and multi-agent resource allocation games."
      ],
      initialAssistantMessage: "Negotiation critic initialized. Ask me how I calculate regret thresholds or manage stateful reflection traces.",
      mockQueries: ["Explain the Nash Regret calculation", "What negotiation benchmarks were used?"],
      mockQAs: [
        {
          question: "explain the nash regret calculation",
          answer: "Nash Regret is calculated by subtracting the expected payoff of the agent's current proposal from the maximum payoff available had the agent known the opponent's strategy. By holding internal critiques, the agent minimizes this value iteratively."
        },
        {
          question: "what negotiation benchmarks were used?",
          answer: "The framework was validated on two-player resource splitting games, complex supply chain contract disputes, and dynamic high-frequency asset swapping simulations."
        }
      ]
    },
    {
      id: "evaluating-safety",
      title: "Evaluating Safety Bounds in Autonomous Trading Swarms",
      subTagline: "STABILIZATION POLICIES FOR STOCHASTIC MARKET AGENTS",
      institution: "Oxford",
      difficulty: "HARD",
      readingTime: "15 min",
      relevance: "95% Match",
      isHot: false,
      category: "Safety",
      tags: ["Economics", "Safety"],
      summary: "", // Matches the screenshot: compact card with no visible body summary!
      body: "Autonomous trading swarms—composed of hundreds of deep reinforcement learning agents executing high-frequency trades—often exhibit chaotic emergent behaviors such as sudden flash crashes or joint market manipulation. This study models multi-agent stochastic policies and derives rigorous upper safety bounds. By applying control-theory principles to policy parameters, we demonstrate that system stability is mathematically preserved even when agents run adversarial or malicious trading configurations.",
      citations: [
        "Karpov (2021) — Algorithmic Collusion in Electronic Markets",
        "Sutton et al. (2018) — Reinforcement Learning: An Introduction",
        "Pfeifer et al. (2020) — Boundary Value Controls in Multi-Agent Physics"
      ],
      notes: [
        "Applies control-theory boundary constraints directly to reinforcement learning action spaces.",
        "Proves mathematical containment of flash-crash volatility under joint adversarial agent patterns.",
        "Demonstrates a 40% increase in logical trading consistency and risk mitigation."
      ],
      initialAssistantMessage: "Oxford Trading Safety Kernel online. Ask me about stochastic policy bounds, algorithmic collusion, or control-theory parameters.",
      mockQueries: ["How are the safety bounds formulated?", "Explain the flash-crash containment proof"],
      mockQAs: [
        {
          question: "how are the safety bounds formulated?",
          answer: "The safety bounds are formulated as Lipschitz continuity constraints on the policy network gradients, preventing sudden, unbounded shifts in trading volume during high-volatility market cycles."
        },
        {
          question: "explain the flash-crash containment proof",
          answer: "We employ Lyapunov stability functions to model the swarm's total kinetic market pressure, proving that under our boundary controls, market pressure remains bounded and converges back to equilibrium."
        }
      ],
      borderAccent: "border-t border-t-violet" // Matches the purple top outline of Card 3 in the screenshot!
    },
    {
      id: "llm-compiler",
      title: "LLM-Compiler: An Agentic Compiler for Parallel Execution",
      subTagline: "PARALLEL DIRECTED ACYCLIC GRAPH COMPILATION ON TOOLS",
      institution: "UC Berkeley",
      difficulty: "MEDIUM",
      readingTime: "14 min",
      relevance: "94% Match",
      isHot: false,
      category: "Multi-Agent",
      tags: ["Multi-Agent", "Reasoning"],
      summary: "LLM agents running complex workflows suffer from latency. LLM-Compiler compiles user queries into a parallel tool DAG.",
      body: "Sequential tool execution creates severe bottlenecks in multi-agent pipelines. LLM-Compiler resolves this by compiling user requirements into a parallel Directed Acyclic Graph (DAG). The planner traces data dependencies at runtime, executing independent steps concurrently and achieving massive latency gains without sacrificing precision.",
      citations: [
        "Kim et al. (2024) — LLM-Compiler: Parallel Function Call Compilation",
        "Chase et al. (2023) — LangChain: Building LLM Applications"
      ],
      notes: [
        "Splits architecture into Planner, Fetcher, and Execution Engine.",
        "Minimizes task execution latency up to 3.7x in standard benchmarks.",
        "Traces variables dynamically to resolve parallel tool dependency branches."
      ],
      initialAssistantMessage: "LLM-Compiler kernel operational. Ask me about compiler latency optimizations or tool-DAG dependencies.",
      mockQueries: ["What is the DAG Planner speedup?", "How does it handle runtime branches?"],
      mockQAs: [
        {
          question: "what is the dag planner speedup?",
          answer: "By executing independent tool loops concurrently, the LLM-Compiler reduces total pipeline latency by up to 3.7x compared to standard sequential ReAct execution."
        },
        {
          question: "how does it handle runtime branches?",
          answer: "If an intermediate tool returns a branch parameter, the fetcher halts pending dependent branches and updates the remaining DAG nodes dynamically based on the planner's revision rules."
        }
      ]
    },
    {
      id: "constitutional-ai",
      title: "Constitutional AI: Harmlessness from AI Feedback",
      subTagline: "SELF-ALIGNMENT VIA MACHINE FEEDBACK PRINCIPLES",
      institution: "Anthropic",
      difficulty: "HARD",
      readingTime: "18 min",
      relevance: "97% Match",
      isHot: true,
      category: "Safety",
      tags: ["Safety", "Agents", "HOT"],
      summary: "Trains models to be harmless without human feedback by using a written constitution to guide iterative self-critique and revision.",
      body: "Constitutional AI (CAI) automates the process of aligning artificial agents to human values. Instead of relying on manual human feedback for thousands of outputs, the system defines a set of principles (a 'constitution'). The AI critiques and revises its own responses based on these principles. This generates an synthetic dataset used to train a preference model for reinforcement learning (RLAIF). CAI results in highly helpful, honest, and harmless agents while maintaining complete transparency of the rules.",
      citations: [
        "Bai et al. (2022) — Constitutional AI: Harmlessness from AI Feedback",
        "Askell et al. (2021) — A Generalist Language Model for Alignment"
      ],
      notes: [
        "Replaces human evaluators in RLHF with an automated Constitutional critique-revision loop.",
        "First phase (Supervised CAI) rewrites intermediate answers to align with rules.",
        "Second phase (RL CAI) utilizes preference labeling by a high-grade language model to train a PPO policy."
      ],
      initialAssistantMessage: "Constitutional AI alignment agent online. I am equipped to explain self-critique parameters, safety constitutions, and RLAIF preference training.",
      mockQueries: ["How does critique-revision loop work?", "What is RLAIF?"],
      mockQAs: [
        {
          question: "how does critique-revision loop work?",
          answer: "In CAI, the model first generates an initial response to a prompt. It is then asked to critique its own response using a specific rule from the constitution (e.g. 'choose the response that is least harmful'). Finally, it revises the response to satisfy the critique, creating a safe and aligned training point."
        },
        {
          question: "what is rlaif?",
          answer: "RLAIF stands for Reinforcement Learning from AI Feedback. It replaces the expensive human annotator in RLHF by using a pre-defined constitution and a high-quality model to automatically evaluate and score agent outputs, training a robust preference model with zero human labels."
        }
      ]
    },
    {
      id: "quiet-star",
      title: "Quiet-STaR: Self-Taught Reasoner Thinking in the Background",
      subTagline: "BACKGROUND COGNITION FOR AUTONOMOUS LANGUAGE ENGINE",
      institution: "Stanford",
      difficulty: "HARD",
      readingTime: "22 min",
      relevance: "98% Match",
      isHot: true,
      category: "Reasoning",
      tags: ["Reasoning", "Agents", "HOT"],
      summary: "Enables language models to learn to think 'quietly' in the background before answering, predicting rationale tokens to improve reasoning capacity.",
      body: "Quiet-STaR expands background thinking to general text corpuses. Instead of generating thoughts only when prompted with explicit QA tasks, Quiet-STaR trains agents to generate internal rationale tokens ('thoughts') at *every single word* in a document. Using a REINFORCE-based policy gradient, the model optimizes its thoughts to make better next-word predictions, resulting in a model that self-learns background reasoning.",
      citations: [
        "Zelikman et al. (2024) — Quiet-STaR: Self-Taught Reasoner",
        "Zelikman et al. (2022) — STaR: Bootstrapping Reasoning With Reasoning"
      ],
      notes: [
        "Formulates reasoning as unobserved latent rationales optimized via predictions.",
        "Allows background rationales of arbitrary length to build multi-hop steps before a visible output.",
        "Yields massive accuracy leaps on mathematical reasoning and complex code synthesis."
      ],
      initialAssistantMessage: "Quiet-STaR background cognition kernel initialized. Ask me how I calculate latent thought distributions or optimize rationales using REINFORCE.",
      mockQueries: ["How does quiet thinking work?", "Explain the REINFORCE loss"],
      mockQAs: [
        {
          question: "how does quiet thinking work?",
          answer: "Quiet-STaR generates a variable length sequence of rationale ('thought') tokens *between* every standard token of text in a library document. These rationales are hidden from the final user output, but allow the model's inner weights to perform multi-step thinking before predicting the next visible word."
        },
        {
          question: "explain the reinforce loss",
          answer: "The model uses a policy gradient algorithm (REINFORCE) to optimize rationale generation. Rationales that help the model predict subsequent tokens more accurately receive a positive reward, while rationales that degrade prediction accuracy receive a negative reward, shifting attention weights accordingly."
        }
      ]
    }
  ];

  // Comprehensive 13-Node Mindmap dataset for all papers
  const initialMindmapNodes: Record<string, Omit<NodePosition, "x" | "y">[]> = {
    "emergent-autonomous": [
      { id: "root", label: "LLM Science Agent", desc: "Autonomous scientific hypothesis planner and code sandbox executer.", type: "root" },
      
      { id: "sandbox", label: "Execution Sandbox", desc: "Isolated virtualization runtime for executing compiled protocols safely.", type: "branch", parentId: "root" },
      { id: "docker", label: "Docker Containers", desc: "Confined virtual layers preventing untrusted socket and root filesystem access.", type: "child", parentId: "sandbox" },
      { id: "caps", label: "Resource Caps", desc: "Hard bounds limiting container memory and thread allocation pools.", type: "child", parentId: "sandbox" },
      
      { id: "core", label: "Scientific Core", desc: "Internal logic driving logical hypothesis drafting and trial runs.", type: "branch", parentId: "root" },
      { id: "planner", label: "Hypothesis Planner", desc: "Recursive deductive planner parsing existing research to compile schedules.", type: "child", parentId: "core" },
      { id: "runner", label: "Python Lab Runner", desc: "Isolated environment containing standard scientific compute libraries.", type: "child", parentId: "core" },
      
      { id: "alignment", label: "Safety Alignment", desc: "Continuous checking layers preventing adversarial breaches.", type: "branch", parentId: "root" },
      { id: "supervisor", label: "Supervisor Critic", desc: "Independent supervisor model intercepting and approving tools.", type: "child", parentId: "alignment" },
      { id: "toxicity", label: "Toxicity Monitor", desc: "Strict filter scanning outputs for malicious chemical plans.", type: "child", parentId: "alignment" },
      
      { id: "infra", label: "Infrastructure", desc: "Network layer configurations for container sandboxing.", type: "branch", parentId: "root" },
      { id: "api", label: "Isolated API Keys", desc: "Restricted rate-limited tokens holding no external billing links.", type: "child", parentId: "infra" },
      { id: "jail", label: "Network Jail", desc: "IPtables configurations preventing containers from making outgoing requests.", type: "child", parentId: "infra" }
    ],
    "self-reflective": [
      { id: "root", label: "Self-Reflection", desc: "Iterative negotiation prompting using game theory equilibria.", type: "root" },
      
      { id: "trace", label: "Reflection Trace", desc: "Internal logical states auditing generated offers.", type: "branch", parentId: "root" },
      { id: "critique", label: "Internal Critique", desc: "Deductive cycles scoring intermediate offers against opponent goals.", type: "child", parentId: "trace" },
      { id: "cycles", label: "Revision Cycles", desc: "Optimization passes re-drafting communication responses dynamically.", type: "child", parentId: "trace" },
      
      { id: "calculus", label: "Regret Calculus", desc: "Continuous payoff computations to minimize Nash regret margins.", type: "branch", parentId: "root" },
      { id: "nash", label: "Nash Regret Bounds", desc: "Mathematical ceiling values enforcing strategic fairness over rounds.", type: "child", parentId: "calculus" },
      { id: "matrix", label: "Payoff Matrix", desc: "Mathematical coordinate maps aligning strategies to expected margins.", type: "child", parentId: "calculus" },
      
      { id: "games", label: "Negotiation Games", desc: "Classic economic testbeds verifying convergence speed.", type: "branch", parentId: "root" },
      { id: "swap", label: "Asset Swap Game", desc: "Simulations involving concurrent high-frequency asset trading.", type: "child", parentId: "games" },
      { id: "splitting", label: "Resource Splitting", desc: "Divide-and-choose scenarios measuring fair utility distributions.", type: "child", parentId: "games" },
      
      { id: "theory", label: "Game Theory", desc: "Logical frameworks governing multi-agent coordination.", type: "branch", parentId: "root" },
      { id: "pareto", label: "Pareto Optimality", desc: "Equilibrium bounds where no agent can gain without degrading others.", type: "child", parentId: "theory" },
      { id: "bayesian", label: "Bayesian Beliefs", desc: "Stochastic modeling tracking expected strategies of opposing players.", type: "child", parentId: "theory" }
    ],
    "evaluating-safety": [
      { id: "root", label: "Safety Bounds", desc: "Stabilization parameters containerizing swarm behavior.", type: "root" },
      
      { id: "reward", label: "Reward Modeling", desc: "Preference evaluations scoring harmlessness outputs.", type: "branch", parentId: "root" },
      { id: "rlaif", label: "RLAIF Preferences", desc: "Automated machine preference labeled datasets replacing human benchmarks.", type: "child", parentId: "reward" },
      { id: "toxic", label: "Toxicity Scores", desc: "Continuous numeric models grading negative conversational indicators.", type: "child", parentId: "reward" },
      
      { id: "hitl", label: "Human-in-the-Loop", desc: "Continuous monitoring checkpoints during live agent executions.", type: "branch", parentId: "root" },
      { id: "manual", label: "Manual Intervention", desc: "Supervisor manual keys allowing live overrides during trading runs.", type: "child", parentId: "hitl" },
      { id: "approval", label: "Active Approval", desc: "Strict gating checks validating high-volatility financial movements.", type: "child", parentId: "hitl" },
      
      { id: "robustness", label: "Adversarial Robustness", desc: "Model protection against coordinate stress testing.", type: "branch", parentId: "root" },
      { id: "injection", label: "Prompt Injection", desc: "System firewalls shielding agents from host system prompt overrides.", type: "child", parentId: "robustness" },
      { id: "stress", label: "Stress Testing", desc: "Simulated coordinate stress vectors testing containment under stress.", type: "child", parentId: "robustness" },
      
      { id: "verification", label: "Verification", desc: "Mathematical bounds demonstrating convergent system security.", type: "branch", parentId: "root" },
      { id: "lyapunov", label: "Lyapunov Functions", desc: "Stability algorithms verifying convergence back to normal market equilibrium.", type: "child", parentId: "verification" },
      { id: "lipschitz", label: "Lipschitz Bounds", desc: "Gradient continuity multipliers preventing flash-crash volume triggers.", type: "child", parentId: "verification" }
    ],
    "llm-compiler": [
      { id: "root", label: "LLM Compiler", desc: "Concurrent Directed Acyclic Graph executor for multi-agent loops.", type: "root" },
      
      { id: "dag", label: "Compiler DAG", desc: "Instruction parsing engines generating concurrent dependency grids.", type: "branch", parentId: "root" },
      { id: "trace", label: "Dependency Trace", desc: "Variable tracking layers resolving parallel function pipelines.", type: "child", parentId: "dag" },
      { id: "planner", label: "Planner Engine", desc: "Core parser translating instruction strings into execute schedules.", type: "child", parentId: "dag" },
      
      { id: "concurrent", label: "Concurrent Exec", desc: "Engine orchestrating parallel tool requests.", type: "branch", parentId: "root" },
      { id: "fetcher", label: "Concurrent Fetcher", desc: "Asynchronous network layer sending independent query calls.", type: "child", parentId: "concurrent" },
      { id: "buffers", label: "Execution Buffers", desc: "Staging memory caches feeding output fields into downstream tasks.", type: "child", parentId: "concurrent" },
      
      { id: "optimization", label: "Optimization", desc: "Latency reductions increasing inference speed.", type: "branch", parentId: "root" },
      { id: "latency", label: "3.7x Latency Gains", desc: "Speed gains accomplished via concurrent ReAct function executions.", type: "child", parentId: "optimization" },
      { id: "token", label: "Token Reduction", desc: "Recursive prompt compression saving overhead token calls.", type: "child", parentId: "optimization" },
      
      { id: "scheduler", label: "Task Scheduler", desc: "Dynamic queuing algorithms managing tool streams.", type: "branch", parentId: "root" },
      { id: "queue", label: "Queue Management", desc: "Active queue sequencing calls based on dependency releases.", type: "child", parentId: "scheduler" },
      { id: "rewrite", label: "Dependency Rewrite", desc: "Real-time updates restructuring tool branches based on runtime flags.", type: "child", parentId: "scheduler" }
    ],
    "constitutional-ai": [
      { id: "root", label: "CAI Alignment", desc: "Self-alignment architecture building harmless AI assistants.", type: "root" },
      
      { id: "supervised", label: "Supervised CAI", desc: "Rewriting text sequences according to alignment instructions.", type: "branch", parentId: "root" },
      { id: "constitution", label: "Constitution Rules", desc: "The explicit principles containerizing acceptable system statements.", type: "child", parentId: "supervised" },
      { id: "critique", label: "Self-Critique Loops", desc: "Recursive review processes identifying safety issues in drafts.", type: "child", parentId: "supervised" },
      
      { id: "rl", label: "RL CAI Phase", desc: "Downstream training pipelines using machine preferences.", type: "branch", parentId: "root" },
      { id: "preferences", label: "Preference Modeling", desc: "AI-annotated preference scoring replacing manual RLAIF runs.", type: "child", parentId: "rl" },
      { id: "ppo", label: "PPO Policy Tuning", desc: "Reinforcement gradient optimizers adjusting final policy parameters.", type: "child", parentId: "rl" },
      
      { id: "principles", label: "Principles", desc: "The core values governing the model safety guidelines.", type: "branch", parentId: "root" },
      { id: "transparency", label: "Transparency Metrics", desc: "Full audit tracking showing which rules governed any response revision.", type: "child", parentId: "principles" },
      { id: "helpful", label: "Helpful vs Harmless", desc: "Balanced criteria enforcing guidelines without sacrificing utility.", type: "child", parentId: "principles" },
      
      { id: "synthetic", label: "Synthetic Data", desc: "AI-generated training sets bootstrapping preference weights.", type: "branch", parentId: "root" },
      { id: "feedback", label: "AI Feedback Loops", desc: "Internal evaluation iterations generating aligned targets.", type: "child", parentId: "synthetic" },
      { id: "labeling", label: "Preference Labeling", desc: "High-grade models scoring response preference pairs autonomously.", type: "child", parentId: "synthetic" }
    ],
    "quiet-star": [
      { id: "root", label: "Quiet-STaR", desc: "Background rationale token generations enhancing predictive reasoning.", type: "root" },
      
      { id: "background", label: "Background Thought", desc: "Invisible text rationale streams generated before next-word copy.", type: "branch", parentId: "root" },
      { id: "tokens", label: "Latent Thought Tokens", desc: "Unseen reasoning markers expanding contextual memory layers.", type: "child", parentId: "background" },
      { id: "rationale", label: "Rationale Generation", desc: "Recursive explanation sequences justifying logical reasoning leaps.", type: "child", parentId: "background" },
      
      { id: "policy", label: "Thought Policy", desc: "Policy gradients rewarding rationales that increase copy accuracy.", type: "branch", parentId: "root" },
      { id: "reinforce", label: "REINFORCE Algorithm", desc: "Gradients weighting thought patterns leading to predictable sentences.", type: "child", parentId: "policy" },
      { id: "reward", label: "Thought Rewards", desc: "Efficiency metrics scoring rationales against target prediction deltas.", type: "child", parentId: "policy" },
      
      { id: "metrics", label: "Metrics", desc: "Substantial precision gains verified on computational benchmarks.", type: "branch", parentId: "root" },
      { id: "math", label: "Math Corpus Leap", desc: "Observed efficiency gains on mathematical problem solving datasets.", type: "child", parentId: "metrics" },
      { id: "synthesis", label: "Code Synthesis Gains", desc: "Enhanced structural syntax matches in complex code generation.", type: "child", parentId: "metrics" },
      
      { id: "inference", label: "Inference Loop", desc: "The dynamic background execution flow parsing library items.", type: "branch", parentId: "root" },
      { id: "insertion", label: "Token Insertion", desc: "Inserting hidden thought tokens during active prediction stages.", type: "child", parentId: "inference" },
      { id: "prediction", label: "Next-Word Predictions", desc: "Training weights minimizing surprise indexes for visible text copy.", type: "child", parentId: "inference" }
    ]
  };

  // Draggable Node Positions State
  const [mindmapPositions, setMindmapPositions] = useState<Record<string, NodePosition[]>>({});
  
  // Drag-and-drop state
  const [draggingNode, setDraggingNode] = useState<{
    paperId: string;
    nodeId: string;
    startX: number;
    startY: number;
    nodeStartX: number;
    nodeStartY: number;
  } | null>(null);

  // Initialize all positions symmetrically
  useEffect(() => {
    const initialized: Record<string, NodePosition[]> = {};
    Object.keys(initialMindmapNodes).forEach((paperId) => {
      const nodeList = initialMindmapNodes[paperId];
      initialized[paperId] = nodeList.map((node) => {
        let initialX = 205;
        let initialY = 210;

        if (node.id === "root") {
          initialX = 205; // Center of 540 container width
          initialY = 210; // Center of 460 container height
        } else if (node.id === "sandbox" || node.id === "trace" || node.id === "reward" || node.id === "dag" || node.id === "supervised" || node.id === "background") {
          // Branch 1 (Top Left)
          initialX = 75;
          initialY = 110;
        } else if (node.id === "docker" || node.id === "critique" || node.id === "rlaif" || node.id === "trace" || node.id === "constitution" || node.id === "tokens") {
          // Child 1.1 (Far Top Left)
          initialX = 15;
          initialY = 30;
        } else if (node.id === "caps" || node.id === "cycles" || node.id === "toxic" || node.id === "planner" || node.id === "critique" || node.id === "rationale") {
          // Child 1.2 (Mid Top Left)
          initialX = 140;
          initialY = 30;
        } else if (node.id === "core" || node.id === "calculus" || node.id === "hitl" || node.id === "concurrent" || node.id === "rl" || node.id === "policy") {
          // Branch 2 (Top Right)
          initialX = 335;
          initialY = 110;
        } else if (node.id === "planner" || node.id === "nash" || node.id === "manual" || node.id === "fetcher" || node.id === "preferences" || node.id === "reinforce") {
          // Child 2.1 (Mid Top Right)
          initialX = 270;
          initialY = 30;
        } else if (node.id === "runner" || node.id === "matrix" || node.id === "approval" || node.id === "buffers" || node.id === "ppo" || node.id === "reward") {
          // Child 2.2 (Far Top Right)
          initialX = 395;
          initialY = 30;
        } else if (node.id === "alignment" || node.id === "games" || node.id === "robustness" || node.id === "optimization" || node.id === "principles" || node.id === "metrics") {
          // Branch 3 (Bottom Left)
          initialX = 75;
          initialY = 310;
        } else if (node.id === "supervisor" || node.id === "swap" || node.id === "injection" || node.id === "latency" || node.id === "transparency" || node.id === "math") {
          // Child 3.1 (Far Bottom Left)
          initialX = 15;
          initialY = 390;
        } else if (node.id === "toxicity" || node.id === "splitting" || node.id === "stress" || node.id === "token" || node.id === "helpful" || node.id === "synthesis") {
          // Child 3.2 (Mid Bottom Left)
          initialX = 140;
          initialY = 390;
        } else if (node.id === "infra" || node.id === "theory" || node.id === "verification" || node.id === "scheduler" || node.id === "synthetic" || node.id === "inference") {
          // Branch 4 (Bottom Right)
          initialX = 335;
          initialY = 310;
        } else if (node.id === "api" || node.id === "pareto" || node.id === "lyapunov" || node.id === "queue" || node.id === "feedback" || node.id === "insertion") {
          // Child 4.1 (Mid Bottom Right)
          initialX = 270;
          initialY = 390;
        } else if (node.id === "jail" || node.id === "bayesian" || node.id === "lipschitz" || node.id === "rewrite" || node.id === "labeling" || node.id === "prediction") {
          // Child 4.2 (Far Bottom Right)
          initialX = 395;
          initialY = 390;
        }

        return {
          ...node,
          x: initialX,
          y: initialY
        };
      });
    });
    setMindmapPositions(initialized);
  }, []);

  // Drag handlers
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!draggingNode) return;
    const dx = e.clientX - draggingNode.startX;
    const dy = e.clientY - draggingNode.startY;

    const container = e.currentTarget.getBoundingClientRect();
    let newX = draggingNode.nodeStartX + dx;
    let newY = draggingNode.nodeStartY + dy;

    // Boundary constraints based on node sizes
    const nodeWidth = draggingNode.nodeId === "root" ? 130 : 125;
    const nodeHeight = draggingNode.nodeId === "root" ? 40 : 32;

    newX = Math.max(10, Math.min(container.width - nodeWidth - 10, newX));
    newY = Math.max(10, Math.min(container.height - nodeHeight - 10, newY));

    setMindmapPositions((prev) => {
      const currentList = prev[draggingNode.paperId] || [];
      const updated = currentList.map((n) =>
        n.id === draggingNode.nodeId ? { ...n, x: newX, y: newY } : n
      );
      return {
        ...prev,
        [draggingNode.paperId]: updated
      };
    });
  };

  const handleMouseUp = () => {
    setDraggingNode(null);
  };

  // Map of Paper ID -> Chat Messages
  const [chatHistories, setChatHistories] = useState<Record<string, Message[]>>({
    "emergent-autonomous": [{ role: "assistant", content: papers[0].initialAssistantMessage }],
    "self-reflective": [{ role: "assistant", content: papers[1].initialAssistantMessage }],
    "evaluating-safety": [{ role: "assistant", content: papers[2].initialAssistantMessage }],
    "llm-compiler": [{ role: "assistant", content: papers[3].initialAssistantMessage }],
    "constitutional-ai": [{ role: "assistant", content: papers[4].initialAssistantMessage }],
    "quiet-star": [{ role: "assistant", content: papers[5].initialAssistantMessage }]
  });

  // Dynamic Streaming & Reasoning State
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [activeCheckpoint, setActiveCheckpoint] = useState<string | null>(null);

  const activePaper = papers.find(p => p.id === selectedPaperId) || papers[0];
  const activeChat = chatHistories[selectedPaperId] || [{ role: "assistant", content: activePaper.initialAssistantMessage }];

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeChat, isStreaming, activeCheckpoint, activeRightTab]);

  // "Load memory" handler (logs removed from state completely)
  const handleLoadMemory = () => {
    // Simply placeholder logic or memory initialization
  };

  // Dynamic Multi-Agent reasoning & streaming response generator
  const triggerStreamingResponse = async (userText: string) => {
    if (isStreaming) return;
    setIsStreaming(true);

    const paperId = selectedPaperId;
    const currentPaper = papers.find(p => p.id === paperId) || papers[0];

    // Force Right Tab to Chat
    setActiveRightTab("chat");

    // 1. Append User Message
    setChatHistories(prev => ({
      ...prev,
      [paperId]: [...(prev[paperId] || []), { role: "user", content: userText }]
    }));

    // 2. Play reasoning checkpoints sequence
    const checkpoints = [
      "COGNITION: Analyzing semantic parameters...",
      "RETRIEVAL: Ingesting local citation vectors...",
      "ALIGNMENT: Validating model constraints...",
      "SYNTHESIS: Assembling response schemas..."
    ];

    for (let i = 0; i < checkpoints.length; i++) {
      setActiveCheckpoint(checkpoints[i]);
      await new Promise(res => setTimeout(res, 550));
    }

    setActiveCheckpoint("STREAMING: Transmitting response tokens...");
    await new Promise(res => setTimeout(res, 200));
    setActiveCheckpoint(null);

    // 3. Find answer or generate smart response
    let finalAnswer = "";
    const lowerQuery = userText.toLowerCase().trim();
    const matchedQA = currentPaper.mockQAs.find(qa => 
      lowerQuery.includes(qa.question.toLowerCase()) || qa.question.toLowerCase().includes(lowerQuery)
    );

    if (matchedQA) {
      finalAnswer = matchedQA.answer;
    } else {
      finalAnswer = `Ingesting query regarding **"${currentPaper.title}"**...\n\nYour question ("${userText}") concerns key architectural paradigms within the ${currentPaper.category} space. \n\nOur parsed intelligence indexes the following:\n* **Context Alignment**: Eliminating extraction boundaries.\n* **Metric Checkpoint**: ${currentPaper.notes[0] || 'Optimizing weights'}\n* **Structural Validation**: ${currentPaper.notes[1] || 'Satisfying bounds'}\n\nLet me know if you would like me to retrieve specific formulas in ${currentPaper.institution}'s publication!`;
    }

    // 4. Initialize empty Assistant response
    setChatHistories(prev => ({
      ...prev,
      [paperId]: [...(prev[paperId] || []), { role: "assistant", content: "" }]
    }));

    // 5. Stream response word-by-word
    const words = finalAnswer.split(" ");
    let currentResponse = "";

    for (let i = 0; i < words.length; i++) {
      currentResponse += words[i] + " ";
      setChatHistories(prev => {
        const history = [...(prev[paperId] || [])];
        const lastMsg = history[history.length - 1];
        if (lastMsg && lastMsg.role === "assistant") {
          history[history.length - 1] = { ...lastMsg, content: currentResponse };
        }
        return { ...prev, [paperId]: history };
      });
      await new Promise(res => setTimeout(res, 35));
    }

    setIsStreaming(false);
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isStreaming) return;
    const query = inputMessage;
    setInputMessage("");
    triggerStreamingResponse(query);
  };

  const selectPaperAndScroll = (id: string) => {
    setSelectedPaperId(id);
  };

  // Filter logic
  const filteredPapers = activeFilter === "All" 
    ? papers 
    : papers.filter(p => p.category === activeFilter || p.tags.includes(activeFilter));

  const filterOptions = ["All", "Agents", "Multi-Agent", "Safety"];

  // 2-Column Split to match the masonry layout of Card 1 (Left Col) and Cards 2 & 3 (Right Col)
  const col1Papers = filteredPapers.filter((_, idx) => idx % 2 === 0);
  const col2Papers = filteredPapers.filter((_, idx) => idx % 2 !== 0);

  // Render a specific concept mindmap tree for a card matching the user's uploaded diagram perfectly
  const renderCardMindmap = (paperId: string) => {
    const mmList = mindmapPositions[paperId] || [];
    if (mmList.length === 0) return null;

    const getNodeCenter = (node: NodePosition) => {
      if (node.type === "root") {
        return { x: node.x + 65, y: node.y + 20 };
      }
      return { x: node.x + 62, y: node.y + 16 };
    };

    return (
      <div 
        onClick={(e) => e.stopPropagation()}
        className="mt-5 pt-5 border-t border-border/40 flex flex-col gap-4 animate-fadeIn select-none"
      >
        <div className="flex items-center justify-between">
          <span className="font-mono text-[9px] text-lime tracking-widest uppercase font-extrabold animate-pulse">
            INTERACTIVE KNOWLEDGE CANVAS
          </span>
          <span className="font-mono text-[8px] text-secondaryText">
            drag nodes to reposition • click to explore
          </span>
        </div>

        {/* Drag-and-Drop Mindmap Canvas container */}
        <div 
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          className="bg-[#0D0D0D] border border-[#2A2A2A] rounded-[12px] h-[460px] relative overflow-hidden select-none cursor-grab active:cursor-grabbing"
        >
          {/* SVG arrows overlay */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
            <defs>
              <marker 
                id="arrow" 
                viewBox="0 0 10 10" 
                refX="8" 
                refY="5" 
                markerWidth="6" 
                markerHeight="6" 
                orient="auto-start-reverse"
              >
                <path 
                  d="M 1 1 L 9 5 L 1 9" 
                  fill="none" 
                  stroke="#C8F04A" 
                  strokeWidth="1.5" 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                />
              </marker>
            </defs>
            
            {/* Dynamically drawn connector lines */}
            {mmList.map((node) => {
              if (!node.parentId) return null;
              const parent = mmList.find(n => n.id === node.parentId);
              if (!parent) return null;
              const pCenter = getNodeCenter(parent);
              const cCenter = getNodeCenter(node);
              
              return (
                <line
                  key={`line-${node.id}`}
                  x1={pCenter.x}
                  y1={pCenter.y}
                  x2={cCenter.x}
                  y2={cCenter.y}
                  stroke="#2A2A2A"
                  strokeWidth="1.5"
                  markerEnd="url(#arrow)"
                />
              );
            })}
          </svg>

          {/* Render draggable Nodes */}
          {mmList.map((node) => {
            const isSelected = activeMindmapNode === node.label;
            const isRoot = node.type === "root";
            const isBranch = node.type === "branch";
            
            const style: React.CSSProperties = {
              left: `${node.x}px`,
              top: `${node.y}px`
            };

            let nodeClass = "";
            if (isRoot) {
              nodeClass = "w-[130px] h-[40px] bg-[#E8E6DF] text-[#0D0D0D] font-syne font-extrabold text-[11px] rounded-[12px] border border-[#E8E6DF] shadow-md shadow-white/5 whitespace-nowrap";
            } else if (isBranch) {
              nodeClass = `w-[125px] h-[32px] text-[8.5px] font-mono font-bold tracking-wider uppercase border rounded-[10px] leading-tight ${
                isSelected
                  ? "bg-lime text-black border-lime font-extrabold shadow-sm shadow-lime/10"
                  : "bg-[#1E1E1E] text-secondaryText border-[#2A2A2A] hover:bg-[#202020] hover:text-white"
              }`;
            } else {
              nodeClass = `w-[125px] h-[32px] text-[8.5px] font-mono border rounded-[10px] leading-tight ${
                isSelected
                  ? "bg-lime text-black border-lime font-extrabold shadow-sm shadow-lime/10"
                  : "bg-[#0D0D0D] text-secondaryText border-[#2A2A2A] hover:bg-[#1A1A1A] hover:text-[#E8E6DF]"
              }`;
            }

            return (
              <button
                key={node.id}
                type="button"
                style={style}
                onMouseDown={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setDraggingNode({
                    paperId,
                    nodeId: node.id,
                    startX: e.clientX,
                    startY: e.clientY,
                    nodeStartX: node.x,
                    nodeStartY: node.y
                  });
                  setActiveMindmapNode(node.label);
                }}
                className={`absolute z-10 flex items-center justify-center text-center px-1.5 transition-all select-none duration-75 active:scale-[0.98] ${nodeClass}`}
              >
                <span className="truncate w-full block">{node.label}</span>
              </button>
            );
          })}

        </div>

        {/* Selected Node Details block */}
        {activeMindmapNode && mmList.some(n => n.label === activeMindmapNode) && (
          <div className="bg-[#141414] border border-[#2A2A2A] p-3.5 rounded-[6px] flex flex-col gap-1.5 animate-fadeIn">
            <div className="flex items-center justify-between border-b border-border/40 pb-1">
              <span className="font-mono text-[8.5px] text-lime uppercase tracking-wider font-bold">
                {activeMindmapNode}
              </span>
              <button
                onClick={() => setActiveMindmapNode(null)}
                className="text-[8px] font-mono text-secondaryText hover:text-white"
              >
                clear
              </button>
            </div>
            
            <p className="text-[11px] leading-relaxed text-secondaryText font-sans select-text">
              {mmList.find(n => n.label === activeMindmapNode)?.desc}
            </p>

            <button
              onClick={() => {
                setInputMessage(`Tell me more about ${activeMindmapNode} inside ${activePaper.title}.`);
                setActiveRightTab("chat");
              }}
              className="self-start text-[9.5px] font-bold text-lime hover:underline flex items-center gap-1 font-mono mt-1"
            >
              Ask Agent about this concept ➔
            </button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-canvas overflow-hidden font-sans text-primaryText select-none">
      
      {/* ======================================================== */}
      {/* 1. LEFT SIDEBAR (240px)                                  */}
      {/* ======================================================== */}
      <aside className="w-[240px] shrink-0 bg-[#0D0D0D] flex flex-col justify-between select-none p-5 border-r border-[#1E1E1E]">
        <div className="flex flex-col gap-6">
          {/* Brand Wordmark - RESEARCH RUN. */}
          <div className="font-syne font-extrabold text-[22px] tracking-tight text-white select-none leading-none pt-2 flex items-center">
            RESEARCH RUN<span className="text-lime">.</span>
          </div>

          {/* Load Memory Module */}
          <div className="w-full">
            <button
              onClick={handleLoadMemory}
              className="w-full bg-[#1E1E1E]/40 hover:bg-[#1E1E1E] text-[#E8E6DF] border border-border py-2 px-3 rounded-[6px] font-sans text-xs text-left transition-colors flex items-center gap-2 group active:scale-[0.98]"
            >
              <span className="relative flex h-2 w-2 shrink-0">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-lime opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-lime"></span>
              </span>
              <span className="group-hover:text-lime transition-colors">Load memory</span>
            </button>
          </div>

          {/* Navigation Bar */}
          <div className="flex flex-col gap-1.5 pt-2">
            {[
              { id: "dashboard", label: "Dashboard", icon: LayoutGrid },
              { id: "digest", label: "Today's Digest", icon: Sparkles },
              { id: "library", label: "My Library", icon: BookOpen },
              { id: "collections", label: "Collections", icon: FolderClosed }
            ].map((item) => {
              const isActive = activeNav === item.id;
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveNav(item.id)}
                  className={`w-full py-2 px-3 rounded-[6px] font-sans text-xs text-left flex items-center gap-3 transition-colors ${
                    isActive
                      ? "text-lime bg-[#1E1E1E]/40 font-semibold"
                      : "text-secondaryText hover:text-primaryText hover:bg-[#1E1E1E]/20"
                  }`}
                >
                  <Icon className={`h-4 w-4 shrink-0 ${isActive ? "text-lime" : "text-secondaryText"}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Minimal Footer Settings Link */}
        <div className="flex flex-col gap-4">
          <button className="w-full py-2 px-3 rounded-[6px] text-secondaryText hover:text-white transition-all flex items-center gap-3 text-xs text-left">
            <Settings className="h-4 w-4 shrink-0 text-secondaryText" />
            <span>Settings</span>
          </button>
        </div>
      </aside>

      {/* ======================================================== */}
      {/* 2. MAIN RESEARCH FEED (Flexible Middle)                   */}
      {/* ======================================================== */}
      <main className="flex-1 bg-workspace border-r border-[#1E1E1E] flex flex-col min-w-0 p-8 select-none">
        
        {/* Main Feed Header */}
        <header className="flex flex-col shrink-0 mb-6">
          <h1 className="font-syne font-extrabold text-[32px] text-primaryText tracking-tight select-none">
            Today's Digest
          </h1>
          
          {/* Filter Bar */}
          <div className="flex items-center mt-4 border-b border-[#1E1E1E] pb-4">
            <div className="flex gap-2">
              {filterOptions.map((filter) => {
                const isActive = activeFilter === filter;
                return (
                  <button
                    key={filter}
                    onClick={() => setActiveFilter(filter)}
                    className={`px-3.5 py-1 rounded-full font-sans text-xs tracking-wider transition-all border ${
                      isActive
                        ? "bg-lime text-[#0D0D0D] border-lime font-medium"
                        : "bg-transparent text-[#E8E6DF] border-border hover:text-primaryText hover:border-secondaryText"
                    }`}
                  >
                    {filter}
                  </button>
                );
              })}
            </div>
          </div>
        </header>

        {/* Research Paper Grid - Masonry Columns */}
        <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar select-none">
          <div className="grid grid-cols-2 gap-6 pb-6 items-start">
            
            {/* Column 1 (Left Col) */}
            <div className="flex flex-col gap-6">
              {col1Papers.map((paper) => {
                const isSelected = selectedPaperId === paper.id;
                const isMindmapExpanded = expandedMindmapPaperId === paper.id;
                return (
                  <div
                    key={paper.id}
                    onClick={() => {
                      selectPaperAndScroll(paper.id);
                      if (expandedMindmapPaperId !== paper.id) {
                        setExpandedMindmapPaperId(null);
                        setActiveMindmapNode(null);
                      }
                    }}
                    className={`bg-card border p-6 rounded-[12px] transition-all flex flex-col justify-between cursor-pointer group hover:border-[#444440] select-none ${
                      isSelected ? "border-lime bg-[#202020]/30" : "border-border"
                    } ${paper.borderAccent || ""}`}
                  >
                    <div>
                      {/* Card Top Row - Badge only */}
                      <div className="flex justify-end items-start mb-3">
                        {paper.isHot ? (
                          <span className="bg-coral text-canvas font-mono text-[8px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider flex items-center gap-1">
                            <span className="w-1 h-1 bg-canvas rounded-full animate-pulse"></span>
                            HOT
                          </span>
                        ) : (
                          <span className="bg-[#1A2400] text-lime font-mono text-[8px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider border border-lime/20">
                            {paper.relevance}
                          </span>
                        )}
                      </div>

                      {/* Paper Title */}
                      <h2 className="font-syne font-bold text-[15px] text-primaryText tracking-tight mb-2 group-hover:text-lime transition-colors leading-tight">
                        {paper.title}
                      </h2>

                      {/* Tag Pills directly under title */}
                      <div className="flex flex-wrap gap-1.5 mb-4">
                        {paper.tags.map((tag) => {
                          let colorClass = "text-secondaryText bg-[#141414] border-border";
                          if (tag === "arXiv" || tag === "LLMs") colorClass = "text-blue bg-[#0D1525] border-blue/20";
                          if (tag === "NeurIPS" || tag === "Negotiation") colorClass = "text-violet bg-[#1A142D] border-violet/20";
                          if (tag === "Economics" || tag === "Safety") colorClass = "text-coral bg-[#2D0D0D] border-coral/20";

                          return (
                            <span
                              key={tag}
                              className={`font-mono text-[8px] font-semibold px-2 py-0.5 rounded-md border uppercase tracking-wider ${colorClass}`}
                            >
                              {tag}
                            </span>
                          );
                        })}
                      </div>

                      {/* Summary (Only rendered if summary is present) */}
                      {paper.summary && (
                        <p className="text-[12.5px] text-secondaryText leading-relaxed mb-6 font-sans">
                          {paper.summary}
                        </p>
                      )}
                    </div>

                    {/* Card Bottom Row: Institution & Reading Time next to icons */}
                    <div className="flex items-center justify-between pt-4 border-t border-border/40 font-mono text-[10px] text-secondaryText tracking-wide">
                      <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1.5">
                          <Building2 className="h-3.5 w-3.5 text-secondaryText/80" />
                          <span>{paper.institution}</span>
                        </span>
                        <span className="flex items-center gap-1.5">
                          <Clock className="h-3.5 w-3.5 text-secondaryText/80" />
                          <span>{paper.readingTime}</span>
                        </span>
                      </div>
                      
                      {/* Mindmap and Ask Agent bottom actions */}
                      <div className="flex items-center gap-2 select-none">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            selectPaperAndScroll(paper.id);
                            if (isMindmapExpanded) {
                              setExpandedMindmapPaperId(null);
                              setActiveMindmapNode(null);
                            } else {
                              setExpandedMindmapPaperId(paper.id);
                              setActiveMindmapNode(null);
                            }
                          }}
                          className={`font-mono text-[10px] transition-colors ${
                            isMindmapExpanded ? "text-lime font-bold" : "text-secondaryText hover:text-white"
                          }`}
                        >
                          {isMindmapExpanded ? "Hide Mindmap" : "Mindmap ➔"}
                        </button>
                        <span className="text-[#2A2A2A]">/</span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            selectPaperAndScroll(paper.id);
                            setActiveRightTab("chat");
                          }}
                          className="font-mono text-[10px] text-lime font-bold hover:underline"
                        >
                          Ask Agent ➔
                        </button>
                      </div>
                    </div>

                    {/* Expandable Mindmap Graph Section inside the card */}
                    {isMindmapExpanded && renderCardMindmap(paper.id)}
                  </div>
                );
              })}
            </div>

            {/* Column 2 (Right Col) */}
            <div className="flex flex-col gap-6">
              {col2Papers.map((paper) => {
                const isSelected = selectedPaperId === paper.id;
                const isMindmapExpanded = expandedMindmapPaperId === paper.id;
                return (
                  <div
                    key={paper.id}
                    onClick={() => {
                      selectPaperAndScroll(paper.id);
                      if (expandedMindmapPaperId !== paper.id) {
                        setExpandedMindmapPaperId(null);
                        setActiveMindmapNode(null);
                      }
                    }}
                    className={`bg-card border p-6 rounded-[12px] transition-all flex flex-col justify-between cursor-pointer group hover:border-[#444440] select-none ${
                      isSelected ? "border-lime bg-[#202020]/30" : "border-border"
                    } ${paper.borderAccent || ""}`}
                  >
                    <div>
                      {/* Card Top Row - Badge only */}
                      <div className="flex justify-end items-start mb-3">
                        {paper.isHot ? (
                          <span className="bg-coral text-canvas font-mono text-[8px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider flex items-center gap-1">
                            <span className="w-1 h-1 bg-canvas rounded-full animate-pulse"></span>
                            HOT
                          </span>
                        ) : (
                          <span className="bg-[#1A2400] text-lime font-mono text-[8px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider border border-lime/20">
                            {paper.relevance}
                          </span>
                        )}
                      </div>

                      {/* Paper Title */}
                      <h2 className="font-syne font-bold text-[15px] text-primaryText tracking-tight mb-2 group-hover:text-lime transition-colors leading-tight">
                        {paper.title}
                      </h2>

                      {/* Tag Pills directly under title */}
                      <div className="flex flex-wrap gap-1.5 mb-4">
                        {paper.tags.map((tag) => {
                          let colorClass = "text-secondaryText bg-[#141414] border-border";
                          if (tag === "arXiv" || tag === "LLMs") colorClass = "text-blue bg-[#0D1525] border-blue/20";
                          if (tag === "NeurIPS" || tag === "Negotiation") colorClass = "text-violet bg-[#1A142D] border-violet/20";
                          if (tag === "Economics" || tag === "Safety") colorClass = "text-coral bg-[#2D0D0D] border-coral/20";

                          return (
                            <span
                              key={tag}
                              className={`font-mono text-[8px] font-semibold px-2 py-0.5 rounded-md border uppercase tracking-wider ${colorClass}`}
                            >
                              {tag}
                            </span>
                          );
                        })}
                      </div>

                      {/* Summary (Only rendered if summary is present) */}
                      {paper.summary && (
                        <p className="text-[12.5px] text-secondaryText leading-relaxed mb-6 font-sans">
                          {paper.summary}
                        </p>
                      )}
                    </div>

                    {/* Card Bottom Row: Institution & Reading Time next to icons */}
                    <div className="flex items-center justify-between pt-4 border-t border-border/40 font-mono text-[10px] text-secondaryText tracking-wide">
                      <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1.5">
                          <Building2 className="h-3.5 w-3.5 text-secondaryText/80" />
                          <span>{paper.institution}</span>
                        </span>
                        {paper.readingTime && (
                          <span className="flex items-center gap-1.5">
                            <Clock className="h-3.5 w-3.5 text-secondaryText/80" />
                            <span>{paper.readingTime}</span>
                          </span>
                        )}
                      </div>
                      
                      {/* Mindmap and Ask Agent bottom actions */}
                      <div className="flex items-center gap-2 select-none">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            selectPaperAndScroll(paper.id);
                            if (isMindmapExpanded) {
                              setExpandedMindmapPaperId(null);
                              setActiveMindmapNode(null);
                            } else {
                              setExpandedMindmapPaperId(paper.id);
                              setActiveMindmapNode(null);
                            }
                          }}
                          className={`font-mono text-[10px] transition-colors ${
                            isMindmapExpanded ? "text-lime font-bold" : "text-secondaryText hover:text-white"
                          }`}
                        >
                          {isMindmapExpanded ? "Hide Mindmap" : "Mindmap ➔"}
                        </button>
                        <span className="text-[#2A2A2A]">/</span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            selectPaperAndScroll(paper.id);
                            setActiveRightTab("chat");
                          }}
                          className="font-mono text-[10px] text-lime font-bold hover:underline"
                        >
                          Ask Agent ➔
                        </button>
                      </div>
                    </div>

                    {/* Expandable Mindmap Graph Section inside the card */}
                    {isMindmapExpanded && renderCardMindmap(paper.id)}
                  </div>
                );
              })}
            </div>

          </div>
        </div>
      </main>

      {/* ======================================================== */}
      {/* 3. RIGHT RESEARCH BRIEF PANEL (360px)                      */}
      {/* ======================================================== */}
      <aside className="w-[360px] shrink-0 bg-lightBg text-[#444440] flex flex-col z-10 overflow-hidden relative select-none border-l border-[#E2E2DF]">
        
        {/* Editorial Paper Brief Container */}
        <div className="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-light flex flex-col gap-5">
          
          {/* Header Section matching 'Research Brief' */}
          <div className="border-b border-[#E2E2DF] pb-4">
            <h1 className="font-syne font-extrabold text-[28px] text-black leading-none tracking-tight mb-1 select-none">
              Research Brief
            </h1>
            <span className="font-mono text-[9px] text-[#888882] uppercase tracking-[0.2em] font-semibold block mb-4">
              AI Synthesis
            </span>

            {/* Horizontal Tabs: Analysis, Sources, Chat with outline icons */}
            <div className="flex border-b border-[#E2E2DF] gap-4">
              {[
                { id: "analysis", label: "Analysis", icon: FileText },
                { id: "sources", label: "Sources", icon: BookOpen },
                { id: "chat", label: "Chat", icon: MessageSquare }
              ].map((tab) => {
                const isActive = activeRightTab === tab.id;
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveRightTab(tab.id as any)}
                    className={`pb-2.5 font-sans text-xs font-semibold flex items-center gap-1.5 border-b-2 transition-all -mb-px outline-none ${
                      isActive
                        ? "border-black text-black"
                        : "border-transparent text-[#888882] hover:text-black"
                    }`}
                  >
                    <Icon className={`h-4 w-4 ${isActive ? "text-black" : "text-[#888882]"}`} />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* DYNAMIC TAB CONTENT VIEW */}
          <div className="flex-1 flex flex-col gap-5 select-text">
            
            {/* VIEW A: ANALYSIS TAB */}
            {activeRightTab === "analysis" && (
              <div className="flex flex-col gap-4 animate-fadeIn">
                <h2 className="font-syne font-bold text-[20px] text-black leading-tight tracking-tight select-none">
                  The Multi-Agent Frontier
                </h2>
                
                {/* Synthesis from sources note in dark-green */}
                <div className="font-mono text-[10px] text-[#2E6C2F] font-bold select-none leading-none">
                  &gt; Synthesis generated from 14 sources
                </div>

                <div className="font-sans text-[13.5px] leading-relaxed text-[#444440] space-y-4">
                  <p>
                    The transition from single-model inference to multi-agent ecosystems marks a pivotal shift in AI capabilities. Recent literature highlights three critical architectural paradigms.
                  </p>
                  <p>
                    First, <strong className="text-black">Hierarchical Task Delegation</strong> allows a 'manager' agent to decompose complex objectives into atomic tasks, assigned to specialized sub-agents. This dramatically reduces hallucination rates in specialized domains.
                  </p>
                  <p>
                    Second, the emergence of <strong className="text-black">Adversarial Verification</strong> networks where agents debate outcomes prior to output. The Stanford paper (2023) demonstrated a 40% increase in logical consistency using this method.
                  </p>
                </div>
              </div>
            )}

            {/* VIEW B: SOURCES TAB */}
            {activeRightTab === "sources" && (
              <div className="flex flex-col gap-4 animate-fadeIn">
                <span className="font-mono text-[9px] text-[#888882] tracking-widest uppercase block mb-1 font-semibold">
                  INGESTED SOURCE CITATIONS
                </span>
                <div className="flex flex-col gap-2">
                  {activePaper.citations.map((citation, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-2.5 bg-[#F1F1EE] border border-[#E2E2DF] p-3 font-mono text-[10px] text-[#444440]"
                    >
                      <FileText className="h-3.5 w-3.5 text-blue shrink-0 mt-0.5" />
                      <span className="leading-relaxed select-text">{citation}</span>
                    </div>
                  ))}
                </div>

                {/* AI generated notes in sources */}
                <div className="bg-[#FAF6E8] border border-[#EBE4C7] p-4 text-[11.5px] font-mono text-[#5C543A] mt-2">
                  <div className="flex items-center gap-2 mb-2.5 font-bold text-[#453E26] tracking-wider uppercase border-b border-[#EBE4C7]/60 pb-1">
                    <Sparkles className="h-4 w-4 text-[#8C7621]" />
                    <span>COGNITIVE NOTES</span>
                  </div>
                  <ul className="list-disc pl-4 space-y-1.5">
                    {activePaper.notes.map((note, idx) => (
                      <li key={idx} className="leading-relaxed">{note}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* VIEW C: CHAT TAB */}
            {activeRightTab === "chat" && (
              <div className="flex flex-col gap-4 animate-fadeIn">
                <div className="flex items-center justify-between border-b border-[#E2E2DF] pb-2 mb-1 select-none">
                  <span className="font-mono text-[9px] text-black font-extrabold uppercase tracking-widest">
                    AGENT DISCOVERY CHANNEL
                  </span>
                  <span className="text-[9px] bg-[#141414] text-lime font-mono px-2 py-0.5 font-semibold leading-none">
                    PIPELINE ACTIVE
                  </span>
                </div>

                {/* Reasoning Checkpoint Status Widget */}
                {activeCheckpoint && (
                  <div className="bg-[#141414] text-[#E8E6DF] p-3 font-mono text-[9px] border border-[#2A2A2A] animate-pulse select-none">
                    <div className="flex items-start gap-2 text-lime">
                      <span className="font-bold text-lime mt-0.5">●</span>
                      <span className="leading-tight">{activeCheckpoint}</span>
                    </div>
                  </div>
                )}

                {/* Conversation thread */}
                <div className="flex flex-col gap-3 min-h-[140px]">
                  {activeChat.map((msg, index) => {
                    const isUser = msg.role === "user";
                    return (
                      <div
                        key={index}
                        className={`flex flex-col gap-1 ${isUser ? "items-end" : "items-start"}`}
                      >
                        <span className="font-mono text-[8px] text-[#888882] px-1 uppercase tracking-wider leading-none">
                          {isUser ? "USER RESEARCHER" : `AGENT [${activePaper.id.split("-")[0].toUpperCase()}]`}
                        </span>

                        <div
                          className={`max-w-[100%] py-2.5 px-3.5 border font-mono text-[11px] leading-relaxed ${
                            isUser
                              ? "bg-[#141414] text-[#E8E6DF] border-[#2A2A2A]"
                              : "bg-[#F1F1EE] text-[#2E2E2C] border-[#E2E2DF] font-sans text-[12px]"
                          }`}
                        >
                          <div className="whitespace-pre-line leading-relaxed">
                            {msg.content}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                  
                  {isStreaming && !activeCheckpoint && (
                    <div className="flex items-center gap-2 text-[9px] font-mono text-[#888882] animate-pulse py-1 select-none">
                      <Loader2 className="h-3 w-3 animate-spin text-lime" />
                      <span>STREAMING ACTIVE INTELLIGENCE TOKENS...</span>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>

                {/* Suggested Inquiries inside Chat */}
                <div className="bg-[#F1F1EE] border border-[#E2E2DF] p-3 mt-1 select-none">
                  <span className="font-mono text-[9px] text-[#888882] tracking-wider uppercase block mb-2 font-bold leading-none">
                    SUGGESTED DISCOVERY QUERIES
                  </span>
                  <div className="flex flex-col gap-1.5">
                    {activePaper.mockQueries.map((query) => (
                      <button
                        key={query}
                        onClick={() => {
                          if (isStreaming) return;
                          setInputMessage(query);
                        }}
                        className="w-full text-left font-mono text-[10px] text-[#5B21B6] hover:bg-[#E2E2DF] py-1 px-1.5 border border-transparent hover:border-[#DDD6FE] transition-all truncate block"
                      >
                        → {query}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

          </div>

          {/* ======================================================== */}
          {/* HIGH-CONTRAST DARK QUERY INPUT AREA                       */}
          {/* ======================================================== */}
          <form onSubmit={handleFormSubmit} className="mt-auto pt-4 border-t border-[#E2E2DF] bg-[#FAFAF7]">
            <div className="bg-[#141414] border border-[#2A2A2A] rounded-[6px] p-3 flex flex-col gap-3">
              
              {/* Text Input */}
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask follow-up questions to refine this brief..."
                disabled={isStreaming}
                rows={2}
                className="w-full bg-transparent text-[#E8E6DF] font-mono text-[11px] leading-relaxed placeholder-[#888882] focus:outline-none resize-none border-none p-0 focus:ring-0"
              />

              {/* Bottom Row - Attachment & Send */}
              <div className="flex items-center justify-between border-t border-[#2A2A2A] pt-2.5">
                
                {/* Paperclip upload icon on left */}
                <button
                  type="button"
                  className="text-secondaryText hover:text-white transition-colors"
                >
                  <Paperclip className="h-4 w-4" />
                </button>

                {/* Send action text with up-arrow on right */}
                <button
                  type="submit"
                  disabled={isStreaming || !inputMessage.trim()}
                  className="font-mono text-[10px] font-bold text-lime hover:text-white tracking-widest flex items-center gap-1.5 transition-colors disabled:opacity-40 disabled:cursor-not-allowed select-none bg-transparent border-none p-0"
                >
                  <span>SEND TO AGENT</span>
                  <ArrowUp className="h-3.5 w-3.5 shrink-0" />
                </button>

              </div>

            </div>
          </form>

        </div>

      </aside>

    </div>
  );
}
