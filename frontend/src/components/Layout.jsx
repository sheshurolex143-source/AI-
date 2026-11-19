import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';
import AddTransactionModal from './AddTransactionModal';

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [addModalOpen, setAddModalOpen] = useState(false);
  const location = useLocation();

  // Determine current page title
  const getTitle = () => {
    switch (location.pathname) {
      case '/':
        return 'Financial Overview';
      case '/transactions':
        return 'Transactions & Categorization';
      case '/insights':
        return 'AI Insights & Forecast';
      case '/budgets':
        return 'Budgets & Financial Goals';
      case '/how-it-works':
        return 'AI Model Architecture & Lab';
      case '/settings':
        return 'System Settings & Retraining';
      default:
        return 'FinSight AI';
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex transition-colors duration-200">
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

      <div className="flex-1 lg:pl-64 flex flex-col min-w-0">
        <Navbar
          title={getTitle()}
          onOpenMobileMenu={() => setSidebarOpen(true)}
          onOpenAddModal={() => setAddModalOpen(true)}
        />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet context={{ openAddModal: () => setAddModalOpen(true) }} />
        </main>
      </div>

      {addModalOpen && (
        <AddTransactionModal
          isOpen={addModalOpen}
          onClose={() => setAddModalOpen(false)}
          onSuccess={() => {
            setAddModalOpen(false);
            window.dispatchEvent(new CustomEvent('transaction_added'));
          }}
        />
      )}
    </div>
  );
}

