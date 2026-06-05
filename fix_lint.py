import os
import re

files = [
    "apps/web/app/(dashboard)/dashboard/page.tsx",
    "apps/web/app/login/page.tsx",
    "apps/web/components/billing/UsageBanner.tsx",
    "apps/web/components/shared/UpgradeModal.tsx"
]

for file in files:
    with open(file, 'r') as f:
        content = f.read()

    # Simple regex to replace single quotes that are likely unescaped entities
    # A bit risky but let's just do targeted replacements based on known errors
    content = content.replace("Today's", "Today&apos;s")
    content = content.replace("paper's", "paper&apos;s")
    content = content.replace("you've", "you&apos;ve")
    content = content.replace("It's", "It&apos;s")
    content = content.replace("You're", "You&apos;re")
    content = content.replace("We've", "We&apos;ve")
    content = content.replace("we've", "we&apos;ve")
    content = content.replace("We're", "We&apos;re")
    content = content.replace("we're", "we&apos;re")
    content = content.replace("AI's", "AI&apos;s")

    with open(file, 'w') as f:
        f.write(content)
