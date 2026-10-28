import React, { useState } from 'react';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { DashboardPage } from './pages/DashboardPage';
import { ReviewWorkbenchPage } from './pages/ReviewWorkbenchPage';
import { ReviewQueuePage } from './pages/ReviewQueuePage';
import { EvidenceLedgerPage } from './pages/EvidenceLedgerPage';
import { GuidelineClarityRadarPage } from './pages/GuidelineClarityRadarPage';
import { BrandKnowledgePage } from './pages/BrandKnowledgePage';
import { AssetsPage } from './pages/AssetsPage';
import { TeamPage } from './pages/TeamPage';
import { AuditLogPage } from './pages/AuditLogPage';
import { ReviewDetailPage } from './pages/ReviewDetailPage';

export const MainLayout: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);

  const handleOpenDocument = (documentId: string) => {
    setSelectedDocId(documentId);
  };

  const handleBackToWorkbench = () => {
    setSelectedDocId(null);
  };

  return (
    <div className="min-h-screen bg-navy-950 text-slate-100 flex flex-col font-sans">
      <Navbar onRefresh={() => {}} />

      <div className="flex flex-1">
        <Sidebar
          currentTab={currentTab}
          onTabChange={(tab) => {
            setSelectedDocId(null);
            setCurrentTab(tab);
          }}
        />

        <main className="flex-1 overflow-y-auto bg-gradient-to-b from-navy-950 via-navy-900/40 to-navy-950">
          {selectedDocId ? (
            <ReviewDetailPage
              documentId={selectedDocId}
              onBack={handleBackToWorkbench}
            />
          ) : (
            <>
              {currentTab === 'dashboard' && <DashboardPage onNavigate={(tab) => setCurrentTab(tab)} />}
              {currentTab === 'workbench' && <ReviewWorkbenchPage onOpenDocument={handleOpenDocument} />}
              {currentTab === 'queue' && <ReviewQueuePage onOpenDocument={handleOpenDocument} />}
              {currentTab === 'evidence' && <EvidenceLedgerPage />}
              {currentTab === 'radar' && <GuidelineClarityRadarPage />}
              {currentTab === 'brand' && <BrandKnowledgePage />}
              {currentTab === 'assets' && <AssetsPage />}
              {currentTab === 'team' && <TeamPage />}
              {currentTab === 'audit' && <AuditLogPage />}
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <MainLayout />
    </AuthProvider>
  );
}
