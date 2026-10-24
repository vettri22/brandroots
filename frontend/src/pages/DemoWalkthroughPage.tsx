import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Badge } from '../components/Badge';
import { Compass, CheckCircle2, ArrowRight, ShieldCheck, BugPlay, UserCheck, Award } from 'lucide-react';

interface DemoWalkthroughPageProps {
  onNavigate: (tab: string, docId?: string) => void;
}

export const DemoWalkthroughPage: React.FC<DemoWalkthroughPageProps> = ({ onNavigate }) => {
  const { role, switchRole } = useAuth();

  const steps = [
    {
      num: 1,
      title: "Creator Submits Problematic Draft",
      persona: "creator" as const,
      personaName: "Alex Chen (Content Creator)",
      description: "Draft 'Q4 Commercial Sales Deck' contains an unsupported outcome guarantee ('guaranteed results'), outdated pricing ('$29/mo' instead of '$49/mo'), and prohibited terminology ('BioBot').",
      actionLabel: "Open Draft in Workbench",
      targetTab: "workbench",
      docId: "doc-demo-001"
    },
    {
      num: 2,
      title: "BrandRoots Detects Issues with Verified Sources",
      persona: "creator" as const,
      personaName: "Alex Chen (Content Creator)",
      description: "Deterministic rules flag '$29/mo' citing 'NovusBio Master Commercial Schedule Q4-2026'. Heuristic checks flag 'guaranteed results' citing 'NovusBio Brand Playbook 2026, Section 4.2'.",
      actionLabel: "Inspect Findings Panel",
      targetTab: "workbench",
      docId: "doc-demo-001"
    },
    {
      num: 3,
      title: "Creator Accepts Suggested Brand Corrections",
      persona: "creator" as const,
      personaName: "Alex Chen (Content Creator)",
      description: "Click 'Accept Suggestion' on the pricing finding ($29/mo -> $49/mo) and promotional claim finding. The canvas text updates in-place, creating a version snapshot v2 with recalculated compliance score.",
      actionLabel: "Apply Suggested Fixes",
      targetTab: "workbench",
      docId: "doc-demo-001"
    },
    {
      num: 4,
      title: "Creator Submits Revised Draft for Review",
      persona: "creator" as const,
      personaName: "Alex Chen (Content Creator)",
      description: "Creator transitions the draft from Draft -> Submitted. Lifecycle policy prevents the creator from self-approving.",
      actionLabel: "Submit Revised Draft",
      targetTab: "workbench",
      docId: "doc-demo-001"
    },
    {
      num: 5,
      title: "Reviewer Evaluates and Approves",
      persona: "reviewer" as const,
      personaName: "Dr. Maya Patel (Compliance Reviewer)",
      description: "Switch to Reviewer persona. Dr. Maya Patel inspects the revised version, adds audit comments, and grants formal approval.",
      actionLabel: "Switch to Reviewer & Review",
      targetTab: "workbench",
      docId: "doc-demo-001"
    },
    {
      num: 6,
      title: "Guideline Debugger Groups Recurring Findings",
      persona: "brand_owner" as const,
      personaName: "Elena Rostova (Brand Governance Owner)",
      description: "Across 5 stored drafts, writers repeatedly violated RULE-CLAIM-01 by promising 'guaranteed results'. The Debugger clusters these 5 cases, surfaces sample quotes, and calculates occurrence frequency.",
      actionLabel: "Inspect Debugger Clusters",
      targetTab: "debugger"
    },
    {
      num: 7,
      title: "System Surfaces Ambiguity Hypothesis & Proposes Clarification",
      persona: "brand_owner" as const,
      personaName: "Elena Rostova (Brand Governance Owner)",
      description: "The Debugger identifies that RULE-CLAIM-01 encourages bold persuasion without a strict boundary on outcome guarantees. It generates a draft clarification (v1 -> v2) explicitly adding the required boundary.",
      actionLabel: "Inspect Proposed Clarification",
      targetTab: "debugger"
    },
    {
      num: 8,
      title: "Brand Owner Explicitly Approves Clarification",
      persona: "brand_owner" as const,
      personaName: "Elena Rostova (Brand Governance Owner)",
      description: "Elena reviews the proposed text, optionally modifies the draft, and clicks 'Approve & Publish Guideline v2'. The active rule is updated in database and audit logged.",
      actionLabel: "Approve Guideline Clarification",
      targetTab: "debugger"
    },
    {
      num: 9,
      title: "Historical Traceability & Future Reviews",
      persona: "brand_owner" as const,
      personaName: "Elena Rostova (Brand Governance Owner)",
      description: "Historical review jobs preserve their snapshot of guideline v1. Any newly reviewed draft is automatically tested against clarified guideline v2.",
      actionLabel: "Verify Audit Trail",
      targetTab: "audit"
    }
  ];

  return (
    <div className="p-8 space-y-6 max-w-5xl mx-auto">
      {/* Banner */}
      <div className="bg-navy-950 p-6 rounded-2xl border border-amber-850/60 shadow-lg">
        <div className="flex items-center space-x-2.5 mb-2">
          <Compass className="w-5 h-5 text-amber-400" />
          <h1 className="text-xl font-bold text-white tracking-tight">Judge & Evaluator Demonstration Script</h1>
          <Badge variant="warning">Inkloom Round 2 Required Scenario</Badge>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          This 9-step guided walkthrough demonstrates the complete BrandRoots workflow: detecting errors, applying corrections, enforcing lifecycle transitions, clustering recurring issues in the <strong>Guideline Debugger</strong>, proposing a guideline clarification, and publishing version 2 with immutable historical traceability.
        </p>
      </div>

      {/* Steps List */}
      <div className="space-y-4">
        {steps.map((st) => (
          <div
            key={st.num}
            className="p-5 rounded-2xl bg-navy-950 border border-navy-800 shadow-md flex flex-col md:flex-row items-start md:items-center justify-between gap-4 hover:border-teal-500/40 transition-all"
          >
            <div className="space-y-1.5 max-w-2xl">
              <div className="flex items-center space-x-2">
                <span className="w-6 h-6 rounded-full bg-teal-500/20 text-teal-300 text-xs font-mono font-bold flex items-center justify-center border border-teal-500/40">
                  {st.num}
                </span>
                <h2 className="text-sm font-bold text-white tracking-tight">{st.title}</h2>
                <Badge variant={st.persona === 'brand_owner' ? 'teal' : st.persona === 'reviewer' ? 'warning' : 'neutral'}>
                  {st.personaName}
                </Badge>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed pl-8">
                {st.description}
              </p>
            </div>

            <div className="pl-8 md:pl-0 flex items-center space-x-2 shrink-0">
              <button
                onClick={async () => {
                  if (role !== st.persona) {
                    await switchRole(st.persona);
                  }
                  onNavigate(st.targetTab, st.docId);
                }}
                className="flex items-center space-x-1.5 px-3.5 py-2 bg-teal-500 hover:bg-teal-400 text-slate-950 rounded-xl text-xs font-bold shadow-md shadow-teal-500/20 transition-all"
              >
                <span>{st.actionLabel}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
