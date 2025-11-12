'use client';

import Sidebar from '@/components/Sidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen overflow-hidden" style={{ backgroundColor: '#18230F' }}>
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 px-4 sm:px-6 flex items-center" style={{ borderBottom: '1px solid #27391C', backgroundColor: '#27391C' }}>
          <h2 className="text-base sm:text-lg font-semibold text-white ml-12 lg:ml-0">
            Lead Generation Dashboard
          </h2>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto p-3 sm:p-4 md:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
