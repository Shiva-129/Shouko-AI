# Shouko-AI — Marketing & Go-To-Market Strategy

> Focused on AI/ML engineers and researchers. Distribution before product perfection.

---

## Target Customer (ICP)

**Primary: AI/ML Engineer at a startup (25–35 years old)**
- Reads 5–10 ArXiv papers per week
- Follows @karpathy, @ylecun, @sama on X
- Has a Notion workspace full of half-finished paper notes
- Expenses SaaS tools under $50/month without approval
- Finds tools via X, Hacker News, and GitHub
- Converted by: seeing the tool work live (demo > description)

**Secondary: PhD researcher in CS/AI**
- Reads 20–30 papers per week
- Frustrated by how quickly paper knowledge fades
- Tight budget (but university may have team licenses)
- Converted by: peer recommendation + academic credibility

---

## Pre-Launch (Weeks 1–6 while building)

### Build in Public on X/Twitter

Post weekly. Show real progress. This is your #1 acquisition channel.

**Post types that work:**
```
Type 1: Progress update
"Week 2 of building Shouko-AI. The ArXiv discovery agent now
scans 200 papers/day and ranks them in under 10 seconds using
Claude Haiku. Here's how the scoring works..."
[attach screenshot of agent output]

Type 2: Problem framing
"I've read 300 papers in the last year. I remember maybe 15 of them.
The problem isn't reading — it's retention. That's what I'm building Shouko-AI to fix."

Type 3: Technical insight
"Chunking strategy matters a lot for RAG on research papers.
Splitting at section boundaries (not just token count) improves
retrieval accuracy by ~40% in our tests. Here's why..."

Type 4: Behind the scenes
"The artifact generator prompt took 3 days to get right.
Here's what bad vs good output looks like, and what changed..."
[side-by-side screenshot]
```

**Post frequency:** 3–4 times per week. Consistency > volume.

**Target accounts to engage with:**
- Andrej Karpathy (@karpathy) — post replies when he talks about papers
- Elvis Saravia (@omarsar0) — the inspiration for this product
- Simon Willison (@simonw) — writes about AI tools
- Swyx (@swyx) — ML community builder
- Papers with Code account — post about papers they feature

### Waitlist Landing Page

Build a simple landing page (shouko-ai.app) by Week 3:
- Hero: "Your AI reads papers. You keep the knowledge."
- 30-second screen recording of artifact creation
- Email capture form (use Resend + simple DB table)
- Target: 500 emails before launch

**Waitlist incentive:** First 100 signups get 3 months of Pro free.

### Reddit Seeding (passive)

Don't spam. Answer questions where Shouko-AI would help:
- r/MachineLearning: "How do you keep up with papers?"
- r/artificial: "Best tools for reading research papers?"
- r/PhD: "How do you manage your paper reading workflow?"

Answer genuinely. Mention you're building something. Link to waitlist if asked.

---

## Launch Week (Week 8)

### Hacker News "Show HN"

**Post title:** "Show HN: I built AI agents that turn ArXiv papers into interactive knowledge bases"

**Best time to post:** Tuesday or Wednesday, 9–11 AM Eastern time

**What to include in post:**
- The problem (reading papers, forgetting them)
- What it does (discovery → artifact → chat)
- How it works technically (people on HN love technical depth)
- What makes it different (agent-based, artifact model, compounding knowledge)
- Link to demo + signup

**Prep before posting:**
- Make sure the product works flawlessly (HN users will stress-test it)
- Have a simple demo paper pre-loaded so skeptics can test without signing up
- Monitor comments for 48h and reply to everything

**Realistic outcome:** 50–200 upvotes, 500–2,000 visitors, 50–200 signups.

### Product Hunt Launch

**Best day:** Tuesday or Wednesday

**Required assets:**
- Product name + tagline (60 chars max)
- Thumbnail (240×240)
- Gallery images (1270×760): 5 screenshots showing the core flow
- 30-second GIF demo
- Written description

**Hunter:** Ask someone with 1K+ followers to hunt it, or self-hunt.

**Day-of strategy:**
- Post at 12:01 AM PT
- Ask beta users to upvote (no brigading — they must be genuine users)
- Post update comments throughout the day

**Realistic outcome:** Top 10 product of day = 500–2,000 additional signups.

### YouTube Demo Video

Record a 5–8 minute screen recording:
1. Start with the problem (30 sec)
2. Show paper discovery (1 min)
3. Show artifact creation — real paper, real time (2 min)
4. Show chatting with the artifact (1 min)
5. Show the library growing over time (1 min)
6. Call to action: try it free (30 sec)

**Title formula:** "I built an AI that remembers research papers for me"
**Target:** 10,000–100,000 views in 6 months

Upload to YouTube, X (native video), LinkedIn.

---

## Post-Launch Content Strategy

### Weekly Content Loop

Every week:
1. Pick 1 interesting paper from the week's digest
2. Share the artifact's key insights on X (3–5 tweets)
3. This demonstrates the product AND provides value
4. Tag the paper authors if possible

**Example:**
```
"Used Shouko-AI to read 'FlashAttention-3' today. Key insight:
The trick isn't just tiling — it's hiding memory latency behind
async tensor core operations. Here's what the artifact surfaced..."

[image: artifact's key insights card]

"Full artifact (searchable, chattable) here: [link to public artifact]"
```

This is your killer growth loop: **show the product working on real content.**

### SEO Content (slow burn, high ROI)

Target these keywords with blog posts:
- "how to keep up with arxiv papers" (1,900/mo)
- "research paper summarizer AI" (1,300/mo)
- "best tools for reading research papers" (880/mo)
- "AI research assistant" (2,400/mo)
- "arxiv paper digest" (590/mo)

**Post format that ranks:** Listicle + genuine tool comparison. Be honest about competitors. People trust honesty.

### Free Public Artifacts (SEO hack)

Every week, create a public artifact for 1 landmark paper:
- "Attention Is All You Need" artifact
- "GPT-4 Technical Report" artifact
- "LLaMA 2" artifact

Make them publicly accessible without login. They get indexed by Google.
When someone searches "attention is all you need summary" → your artifact ranks.
This drives organic traffic + demonstrates product quality.

---

## Cold Outreach

Target: AI researchers on X with "PhD" or "Research Scientist" in bio.

**DM template:**
```
Hi [name],

I saw your thread on [specific paper/topic they posted about].
I'm building Shouko-AI — a system where AI agents automatically
read and transform ArXiv papers into interactive knowledge artifacts
you can actually query and build on.

Would love to get your feedback. Free Pro account if you try it.
[shouko-ai.app]

No obligations, genuinely want researcher input.
```

**Volume:** 20–30 DMs per week. Expect 10–15% response rate.

---

## Partnerships

### Paper Newsletter Sponsorships
- "The Batch" (deeplearning.ai) — highly targeted
- "Papers with Code Newsletter" — perfect audience
- "Import AI" (Jack Clark) — ML policy + research audience

Approach: offer to write a guest piece about research workflow, include product mention. More effective than banner ads.

### Discord/Slack Community Deals
- Offer free Pro accounts to community admins
- Ask to share in their #tools channel
- ML Discord servers: Eleuther, LessWrong, AI Alignment Forum community

### University Lab Outreach
- Target PhD students managing large literature reviews
- Offer team plan discounts for academic groups
- Partner with 2–3 university AI labs for case studies

---

## Viral Loops

### Public Artifact Sharing
- Every artifact has a share button → generates public read-only link
- Link shows artifact with "Create yours at shouko-ai.app" CTA
- Bottom of artifact: "Generated with Shouko-AI"

### Referral Program (Phase 2)
- Invite 3 friends → get 1 month Pro free
- Referred friend signs up → referrer gets credit
- Track in DB: referral_code column on users table

### "AI Paper of the Week"
- Automated weekly tweet: "This week's most-read paper in AI: [title]"
- Link to free public artifact
- Drives recurring X engagement, grows following

---

## Paid Acquisition (Phase 2 only — after PMF)

**Don't run paid ads until you have:**
- 500+ organic signups
- 50+ paying users
- Clear understanding of which channel converts

**When ready:**
- Google Ads: keyword "arxiv paper summarizer", "research paper AI"
- Budget: start $500/month test
- Success metric: CAC < $40 (3-month LTV of Pro user is ~$57)

---

## Metrics to Track (Weekly)

| Metric | Target at Launch | Target at Month 3 |
|---|---|---|
| Waitlist signups | 500 | — |
| Signups (registered) | 100 | 1,000 |
| Activated (1+ artifact) | 40% | 50% |
| Paying users | 10 | 100 |
| MRR | $190 | $2,000 |
| Churn rate | — | <5%/month |
| Artifacts created/day | 10 | 100 |
| Questions asked/day | 50 | 500 |
| X followers | 500 | 2,000 |

---

## Positioning Statement

**For:** AI/ML engineers and researchers who need to stay current with fast-moving research

**Who:** Read papers but don't retain or build on them

**Shouko-AI is:** A multi-agent research intelligence system

**That:** Automatically discovers, ingests, and transforms papers into interactive knowledge artifacts you can query and build on

**Unlike:** Elicit, Consensus, and Perplexity which give you one-time answers

**Shouko-AI:** Builds a compounding, personalized knowledge library that gets smarter every day you use it
